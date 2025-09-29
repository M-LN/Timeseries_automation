"""Persistence utilities for forecast runs."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.engine import Engine

from src.automation.notifications import NotionLogger
from src.config import BASE_DIR, settings
from src.forecasting.models import ForecastResult


def create_db_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine honouring relative SQLite paths."""
    if database_url.startswith("sqlite:///"):
        raw_path = Path(database_url.replace("sqlite:///", ""))
        if not raw_path.is_absolute():
            db_path = BASE_DIR / raw_path
        else:
            db_path = raw_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{db_path}", future=True)
    return create_engine(database_url, future=True)


metadata = MetaData()


forecast_runs_table = Table(
    "forecast_runs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", String, nullable=False),
    Column("horizon", Integer, nullable=False),
    Column("data_source", String, nullable=False),
    Column("latest_price", Float, nullable=False),
    Column("rmse", Float, nullable=False),
    Column("mae", Float, nullable=False),
    Column("mape", Float, nullable=False),
    Column("report_path", String, nullable=False),
)


forecast_values_table = Table(
    "forecast_values",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("run_id", Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), nullable=False),
    Column("timestamp", String, nullable=False),
    Column("actual", Float, nullable=False),
    Column("forecast", Float, nullable=False),
)


def record_forecast_run(
    result: ForecastResult,
    metrics: Dict[str, float],
    *,
    horizon: int,
    data_source: str,
    report_path: Path,
) -> None:
    """Persist a single forecast execution and its series to the configured database."""
    engine = create_db_engine(settings.database.database_url)
    timestamp = datetime.now(UTC).isoformat()
    metadata.create_all(engine)

    pred_aligned = result.y_pred.reindex(result.y_true.index)
    series = pd.DataFrame(
        {
            "timestamp": result.y_true.index.to_list(),
            "actual": result.y_true.values,
            "forecast": pred_aligned.values,
        }
    )
    series["timestamp"] = series["timestamp"].apply(
        lambda value: value.isoformat() if hasattr(value, "isoformat") else str(value)
    )

    with engine.begin() as connection:
        inserted = connection.execute(
            forecast_runs_table.insert().returning(forecast_runs_table.c.id),
            {
                "timestamp": timestamp,
                "horizon": horizon,
                "data_source": data_source,
                "latest_price": metrics["latest"],
                "rmse": metrics["rmse"],
                "mae": metrics["mae"],
                "mape": metrics["mape"],
                "report_path": str(report_path),
            },
        )
        run_id = inserted.scalar_one()

        if not series.empty:
            payload = [
                {
                    "run_id": run_id,
                    "timestamp": row.timestamp,
                    "actual": float(row.actual),
                    "forecast": float(row.forecast),
                }
                for row in series.itertuples()
            ]
            connection.execute(forecast_values_table.insert(), payload)


def ensure_forecast_table_exists() -> None:
    """Create the persistence tables if using SQLite (other engines manage schema externally)."""
    database_url = settings.database.database_url
    if not database_url.startswith("sqlite:///"):
        return

    engine = create_db_engine(database_url)
    metadata.create_all(engine)


ensure_forecast_table_exists()


def sync_to_notion(metrics: Dict[str, float], *, horizon: int, data_source: str, report_path: Path) -> None:
    """Log the forecast run to Notion if configuration is provided."""
    token = settings.apis.notion_token
    database_id = settings.apis.notion_database_id
    if not token or not database_id:
        return

    logger = NotionLogger(token, database_id)
    properties = {
        "Horizon": {"number": horizon},
        "RMSE": {"number": round(metrics["rmse"], 4)},
        "MAE": {"number": round(metrics["mae"], 4)},
        "MAPE": {"number": round(metrics["mape"], 4)},
        "Data Source": {"select": {"name": data_source}},
        "Report": {"url": report_path.as_uri()},
    }
    try:
        logger.log_forecast(
            title=f"Forecast run {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
            properties=properties,
        )
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"Notion logging skipped: {exc}")


class ForecastLogger:
    """Database interface for forecast run history and analysis."""
    
    def __init__(self, database_settings):
        self.database_url = database_settings.database_url
        self.engine = create_db_engine(self.database_url)
        metadata.create_all(self.engine)
    
    def get_recent_runs(self, limit: int = 50) -> pd.DataFrame:
        """Retrieve recent forecast runs with metrics."""
        query = f"""
        SELECT 
            id,
            timestamp as created_at,
            horizon as horizon_hours,
            data_source,
            latest_price as mean_forecast,
            rmse,
            mae,
            mape,
            report_path
        FROM forecast_runs 
        ORDER BY timestamp DESC 
        LIMIT {limit}
        """
        
        df = pd.read_sql(query, self.engine)
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def get_forecast_values(self, run_id: int) -> pd.DataFrame:
        """Retrieve detailed forecast values for a specific run."""
        query = f"""
        SELECT 
            timestamp,
            actual,
            forecast
        FROM forecast_values 
        WHERE run_id = {run_id}
        ORDER BY timestamp
        """
        
        df = pd.read_sql(query, self.engine)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, float]:
        """Get aggregate performance metrics for the last N days."""
        cutoff_date = (datetime.now(UTC) - pd.Timedelta(days=days)).isoformat()
        
        query = f"""
        SELECT 
            AVG(rmse) as avg_rmse,
            AVG(mae) as avg_mae,
            AVG(mape) as avg_mape,
            COUNT(*) as total_runs,
            COUNT(DISTINCT data_source) as unique_sources
        FROM forecast_runs 
        WHERE timestamp >= '{cutoff_date}'
        """
        
        result = pd.read_sql(query, self.engine)
        return result.iloc[0].to_dict() if not result.empty else {}
