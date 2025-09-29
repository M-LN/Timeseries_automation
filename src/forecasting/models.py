"""Forecasting model interfaces and baselines."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class ForecastResult:
    """Represents the outcome of a forecast."""

    y_true: pd.Series
    y_pred: pd.Series

    def rmse(self) -> float:
        return float(np.sqrt(np.mean((self.y_true - self.y_pred) ** 2)))

    def mae(self) -> float:
        return float(np.mean(np.abs(self.y_true - self.y_pred)))

    def mape(self) -> float:
        mask = self.y_true != 0
        return float(np.mean(np.abs((self.y_true[mask] - self.y_pred[mask]) / self.y_true[mask])) * 100)


def naive_forecast(series: pd.Series, horizon: int) -> ForecastResult:
    """Generate a naive forecast using the last observed value."""
    y_true = series.tail(horizon)
    if y_true.empty:
        raise ValueError("Series must contain at least 'horizon' values")
    y_pred = pd.Series(np.repeat(series.iloc[-1], horizon), index=y_true.index)
    return ForecastResult(y_true=y_true, y_pred=y_pred)


def train_test_split(series: pd.Series, test_size: int) -> tuple[pd.Series, pd.Series]:
    """Split a timeseries into train and test segments."""
    if test_size <= 0:
        raise ValueError("test_size must be positive")
    if test_size >= len(series):
        raise ValueError("test_size must be smaller than the series length")
    return series.iloc[:-test_size], series.iloc[-test_size:]


@dataclass
class RollingWindowConfig:
    """Configuration for rolling window evaluation."""

    window_size: int
    step_size: int = 1


def rolling_forecast(series: pd.Series, horizon: int, config: RollingWindowConfig) -> Iterable[ForecastResult]:
    """Yield naive forecasts across rolling windows of the series."""
    for start in range(config.window_size, len(series) - horizon + 1, config.step_size):
        window = series.iloc[start - config.window_size : start]
        actual = series.iloc[start : start + horizon]
        yield naive_forecast(pd.concat([window, actual]), horizon=horizon)
