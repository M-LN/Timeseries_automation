"""Notification clients for Slack and Notion integrations."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import requests


class SlackNotifier:
    """Send messages to Slack channels via Web API."""

    def __init__(self, token: str) -> None:
        self._token = token

    def post_message(self, channel: str, text: str) -> Dict[str, Any]:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={"channel": channel, "text": text},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok", False):
            raise RuntimeError(f"Slack API error: {payload}")
        return payload

    def upload_file(self, channel: str, filepath: Path, title: str | None = None) -> Dict[str, Any]:
        with filepath.open("rb") as file_handle:
            response = requests.post(
                "https://slack.com/api/files.upload",
                headers={"Authorization": f"Bearer {self._token}"},
                data={
                    "channels": channel,
                    "title": title or filepath.name,
                },
                files={"file": (filepath.name, file_handle, "application/octet-stream")},
                timeout=60,
            )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok", False):
            raise RuntimeError(f"Slack file upload error: {payload}")
        return payload


class NotionLogger:
    """Create or update Notion database entries via the Notion API."""

    def __init__(self, token: str, database_id: str) -> None:
        self._token = token
        self._database_id = database_id

    def log_forecast(self, title: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            },
            json={
                "parent": {"database_id": self._database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title,
                                }
                            }
                        ]
                    },
                    **properties,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
