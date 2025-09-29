"""Data cleaning and feature engineering utilities."""
from __future__ import annotations

from typing import Iterable

import pandas as pd


def fill_missing_values(frame: pd.DataFrame, columns: Iterable[str], method: str = "ffill") -> pd.DataFrame:
    """Fill missing values using the specified method."""
    frame = frame.copy()
    frame[columns] = frame[columns].fillna(method=method)
    return frame


def add_lag_features(frame: pd.DataFrame, column: str, lags: Iterable[int]) -> pd.DataFrame:
    """Add lag features for the selected column."""
    frame = frame.copy()
    for lag in lags:
        frame[f"{column}_lag_{lag}"] = frame[column].shift(lag)
    return frame


def add_calendar_features(frame: pd.DataFrame, datetime_column: str) -> pd.DataFrame:
    """Add calendar-based features derived from a datetime column."""
    frame = frame.copy()
    dt = pd.to_datetime(frame[datetime_column])
    frame["hour"] = dt.dt.hour
    frame["day"] = dt.dt.day
    frame["weekday"] = dt.dt.weekday
    frame["month"] = dt.dt.month
    frame["weekofyear"] = dt.dt.isocalendar().week
    frame["is_weekend"] = dt.dt.weekday >= 5
    return frame
