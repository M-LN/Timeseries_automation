"""High-level orchestration for the forecasting automation agent."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Dict, Protocol, Tuple

import numpy as np
import pandas as pd

from src.automation.github import GitHubCommitter, GitHubRepoConfig
from src.automation.notifications import SlackNotifier
from src.config import REPORTS_DIR, settings
from src.data_collection.nordpool import PriceQuery, fetch_spot_prices
from src.data_preparation.transformers import add_calendar_features, add_lag_features
from src.forecasting.models import ForecastResult, naive_forecast, train_test_split
from src.reporting.logging import record_forecast_run, sync_to_notion
from src.reporting.visualization import render_forecast_plot


class Notifier(Protocol):
    """Protocol for notification integrations."""

    def post_message(self, channel: str, text: str) -> dict:  # pragma: no cover - protocol definition only
        ...

@dataclass
class PipelineOutput:
    """Artifacts produced by a pipeline execution."""

    forecast: ForecastResult
    message: str
    report_path: Path
    metrics: Dict[str, float]
    data_source: str


@dataclass
class ForecastPipeline:
    """Executable pipeline covering data ingestion, modelling, and notification."""

    slack_notifier: Notifier
    price_query: PriceQuery = field(default_factory=PriceQuery)

    def run(self, horizon: int = 24) -> PipelineOutput:
        frame, data_source = self._load_price_frame(horizon)
        frame = add_calendar_features(frame, "DateTime")
        frame = add_lag_features(frame, "SpotPrice", lags=[1, 24])
        frame.dropna(inplace=True)
        if len(frame) <= horizon:
            raise ValueError("Not enough observations to perform forecast – increase data window or reduce horizon.")
        train, test = train_test_split(frame["SpotPrice"], test_size=horizon)
        result = naive_forecast(pd.concat([train, test]), horizon=horizon)
        metrics = self._collect_metrics(result)
        message = self._build_message(metrics)
        self.slack_notifier.post_message(channel="#energy-forecast", text=message)
        report_path = render_forecast_plot(
            result,
            output_dir=REPORTS_DIR / "plots",
            title="Spot Price Forecast",
            horizon_hours=horizon,
        )
        self._maybe_upload_chart(report_path)
        self._persist_run(result, metrics, data_source, report_path, horizon)
        self._maybe_commit_to_github(result, metrics, data_source, report_path, horizon)
        return PipelineOutput(
            forecast=result,
            message=message,
            report_path=report_path,
            metrics=metrics,
            data_source=data_source,
        )

    def _collect_metrics(self, result: ForecastResult) -> Dict[str, float]:
        latest = float(result.y_pred.iloc[-1])
        previous = float(result.y_true.iloc[-2]) if len(result.y_true) > 1 else latest
        delta_pct = ((latest - previous) / previous) * 100 if previous else 0.0
        return {
            "latest": latest,
            "previous": previous,
            "delta_pct": delta_pct,
            "rmse": result.rmse(),
            "mae": result.mae(),
            "mape": result.mape(),
        }

    def _build_message(self, metrics: Dict[str, float]) -> str:
        direction = "↑" if metrics["delta_pct"] >= 0 else "↓"
        return (
            f"*Dagens elpris-forecast:* {metrics['latest']:.2f} €/MWh ({direction}{abs(metrics['delta_pct']):.1f}% fra sidste observation)\n"
            f"• RMSE: {metrics['rmse']:.2f}\n"
            f"• MAE: {metrics['mae']:.2f}\n"
            f"• MAPE: {metrics['mape']:.2f}%"
        )

    def _load_price_frame(self, horizon: int) -> Tuple[pd.DataFrame, str]:
        target_date = date.today()
        if not settings.apis.nordpool_api_key:
            return self._generate_synthetic_frame(target_date, horizon), "synthetic"

        try:
            raw_prices = fetch_spot_prices(settings.apis.nordpool_api_key, self.price_query, target_date)
        except Exception:
            return self._generate_synthetic_frame(target_date, horizon), "synthetic"

        frame = pd.DataFrame(raw_prices)
        if {"DateTime", "SpotPrice"}.issubset(frame.columns):
            frame = frame[["DateTime", "SpotPrice"]].copy()
            frame["DateTime"] = pd.to_datetime(frame["DateTime"], errors="coerce")
            frame["SpotPrice"] = pd.to_numeric(frame["SpotPrice"], errors="coerce")
            frame.dropna(subset=["DateTime", "SpotPrice"], inplace=True)
            frame.sort_values("DateTime", inplace=True)
            frame.reset_index(drop=True, inplace=True)
            if len(frame) > horizon:
                return frame, "api"

        return self._generate_synthetic_frame(target_date, horizon), "synthetic"

    def _generate_synthetic_frame(self, target_date: date, horizon: int) -> pd.DataFrame:
        hours = max(horizon + 48, 72)
        start = datetime.combine(target_date, datetime.min.time()) - timedelta(hours=hours - 1)
        timestamps = [start + timedelta(hours=i) for i in range(hours)]
        rng = np.random.default_rng(seed=target_date.toordinal())
        base = 60 + 5 * np.sin(2 * np.pi * np.arange(hours) / 24)
        trend = np.linspace(-2, 2, hours)
        noise = rng.normal(0, 1.5, hours)
        prices = base + trend + noise
        frame = pd.DataFrame({"DateTime": timestamps, "SpotPrice": prices})
        frame["Source"] = "synthetic"
        return frame

    def _maybe_upload_chart(self, report_path: Path) -> None:
        upload = getattr(self.slack_notifier, "upload_file", None)
        if callable(upload) and settings.apis.slack_token:
            try:
                upload(
                    channel="#energy-forecast",
                    filepath=report_path,
                    title=f"Spot price forecast {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
                )
            except Exception as exc:  # pragma: no cover - best effort
                print(f"Slack upload skipped: {exc}")

    def _persist_run(
        self,
        result: ForecastResult,
        metrics: Dict[str, float],
        data_source: str,
        report_path: Path,
        horizon: int,
    ) -> None:
        try:
            record_forecast_run(
                result,
                metrics,
                horizon=horizon,
                data_source=data_source,
                report_path=report_path,
            )
        except Exception as exc:  # pragma: no cover - best effort persistence
            print(f"Database logging skipped: {exc}")
        sync_to_notion(metrics, horizon=horizon, data_source=data_source, report_path=report_path)

    def _maybe_commit_to_github(
        self,
        result: ForecastResult,
        metrics: Dict[str, float],
        data_source: str,
        report_path: Path,
        horizon: int,
    ) -> None:
        token = settings.apis.github_token
        repo = settings.apis.github_repo
        if not token or not repo:
            return

        config = GitHubRepoConfig(
            token=token,
            repo=repo,
            branch=settings.apis.github_branch,
            committer_name=settings.apis.github_committer_name,
            committer_email=settings.apis.github_committer_email,
        )
        committer = GitHubCommitter(config)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        try:
            remote_plot_path = f"reports/plots/{report_path.name}"
            committer.commit_file(
                report_path,
                destination=remote_plot_path,
                message=f"Add forecast plot {timestamp}",
            )

            history_payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "horizon": horizon,
                "data_source": data_source,
                "metrics": metrics,
                "report_path": remote_plot_path,
                "values": {
                    "index": [str(item) for item in result.y_true.index.tolist()],
                    "actual": result.y_true.astype(float).tolist(),
                    "forecast": result.y_pred.reindex(result.y_true.index).astype(float).tolist(),
                },
            }
            committer.commit_text(
                json.dumps(history_payload, indent=2),
                destination=f"reports/history/{report_path.stem}.json",
                message=f"Add forecast metrics {timestamp}",
            )
        except Exception as exc:  # pragma: no cover - best effort
            print(f"GitHub commit skipped: {exc}")


class ConsoleNotifier:
    def post_message(self, channel: str, text: str) -> dict:  # pragma: no cover - simple console stub
        print(f"[{channel}] {text}")
        return {"channel": channel, "text": text}


def _create_notifier() -> Notifier:
    token = settings.apis.slack_token
    if token:
        return SlackNotifier(token)
    return ConsoleNotifier()


def main() -> None:
    """Placeholder CLI entry point."""

    pipeline = ForecastPipeline(slack_notifier=_create_notifier())
    try:
        output = pipeline.run(horizon=24)
        print(f"Report gemt: {output.report_path}")
    except Exception as exc:  # pragma: no cover - console feedback
        print(f"Pipeline execution failed: {exc}")


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    main()
