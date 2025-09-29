"""Helpers for retrieving electricity price data from Nord Pool or related APIs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List

import requests


@dataclass
class PriceQuery:
    """Parameters for querying spot prices."""

    area: str = "DK1"
    currency: str = "EUR"
    resolution: str = "hour"


def fetch_spot_prices(api_key: str, query: PriceQuery, target_date: date) -> List[Dict[str, Any]]:
    """Fetch spot price data for the specified date."""
    params = {
        "deliveryDate": target_date.isoformat(),
        "area": query.area,
        "currency": query.currency,
        "resolution": query.resolution,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        "https://api.nordpoolgroup.com/marketdata/page/10",
        params=params,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])
