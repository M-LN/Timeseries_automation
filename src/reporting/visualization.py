"""Utilities for rendering forecast visualisations."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt
import pandas as pd

from src.forecasting.models import ForecastResult


def render_forecast_plot(
    result: ForecastResult,
    *,
    output_dir: Path,
    title: str = "Spot Price Forecast",
    horizon_hours: Optional[int] = None,
) -> Path:
    """Render a chart comparing actual vs predicted prices and return the image path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    horizon_hours = horizon_hours or len(result.y_pred)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"forecast_{timestamp}.png"

    frame = pd.DataFrame({
        "Actual": result.y_true,
        "Forecast": result.y_pred,
    })

    plt.figure(figsize=(10, 5))
    plt.plot(frame.index, frame["Actual"], label="Actual", marker="o")
    plt.plot(frame.index, frame["Forecast"], label="Forecast", linestyle="--", marker="x")
    plt.title(f"{title} (next {horizon_hours}h)")
    plt.xlabel("Time")
    plt.ylabel("€/MWh")
    plt.grid(True, linestyle=":", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path
