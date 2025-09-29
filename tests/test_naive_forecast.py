"""Smoke tests for the baseline forecasting and reporting utilities."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.config import settings
from src.forecasting.models import ForecastResult, naive_forecast, train_test_split
from src.pipeline import ForecastPipeline, PipelineOutput
from src.reporting.logging import create_db_engine
from src.reporting.visualization import render_forecast_plot


def test_naive_forecast_basic() -> None:
    series = pd.Series(range(10))
    train, test = train_test_split(series, test_size=3)
    result = naive_forecast(pd.concat([train, test]), horizon=3)
    assert len(result.y_true) == 3
    assert (result.y_pred == result.y_pred.iloc[0]).all()
    assert result.rmse() >= 0


class _RecorderNotifier:
    def __init__(self) -> None:
        self.messages = []

    def post_message(self, channel: str, text: str) -> dict:
        self.messages.append((channel, text))
        return {"channel": channel, "text": text}


def test_pipeline_run_uses_synthetic_data_when_no_api_key(tmp_path: Path) -> None:
    settings.apis.nordpool_api_key = None
    original_db_url = settings.database.database_url
    db_path = (tmp_path / "forecasts.db").resolve()
    db_url = f"sqlite:///{db_path.as_posix()}"
    settings.database.database_url = db_url
    notifier = _RecorderNotifier()
    try:
        pipeline = ForecastPipeline(slack_notifier=notifier)
        output = pipeline.run(horizon=24)
    finally:
        settings.database.database_url = original_db_url
    assert isinstance(output, PipelineOutput)
    assert len(output.forecast.y_pred) == 24
    assert notifier.messages
    message_text = notifier.messages[0][1]
    assert "RMSE" in message_text
    assert output.report_path.exists()
    assert output.metrics["rmse"] >= 0

    engine = create_db_engine(db_url)
    with engine.connect() as connection:
        run_count = connection.execute(text("SELECT COUNT(*) FROM forecast_runs")).scalar()
        value_count = connection.execute(text("SELECT COUNT(*) FROM forecast_values")).scalar()
    assert run_count >= 1
    assert value_count >= 24

    output.report_path.unlink(missing_ok=True)


def test_render_forecast_plot_creates_file(tmp_path: Path) -> None:
    series = pd.Series(range(10))
    result = ForecastResult(y_true=series.tail(3), y_pred=series.tail(3) + 1)
    output_path = render_forecast_plot(result, output_dir=tmp_path, title="Test Plot", horizon_hours=3)
    assert output_path.exists()
