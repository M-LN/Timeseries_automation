"""Client utilities for fetching weather data from the OpenWeather API."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import requests


@dataclass
class WeatherQuery:
    """Represents the parameters for querying the OpenWeather API."""

    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    units: str = "metric"

    def to_params(self, api_key: str) -> Dict[str, Any]:
        """Convert the query to a requests-compatible params dictionary."""
        params: Dict[str, Any] = {"appid": api_key, "units": self.units}
        if self.city:
            params["q"] = self.city
        if self.latitude is not None and self.longitude is not None:
            params["lat"] = self.latitude
            params["lon"] = self.longitude
        return params


def fetch_current_weather(api_key: str, query: WeatherQuery) -> Dict[str, Any]:
    """Fetch the current weather conditions from OpenWeather."""
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params=query.to_params(api_key),
        timeout=30,
    )
    response.raise_for_status()
    payload: Dict[str, Any] = response.json()
    payload["fetched_at"] = datetime.utcnow().isoformat()
    return payload
