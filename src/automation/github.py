"""Utilities for committing artifacts to GitHub via the REST API."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests


@dataclass
class GitHubRepoConfig:
    token: str
    repo: str  # format: "owner/name"
    branch: str = "main"
    committer_name: str = "Automation Agent"
    committer_email: str = "automation@example.com"


class GitHubCommitter:
    """Minimal client for committing files to a GitHub repository."""

    def __init__(self, config: GitHubRepoConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "timeseries-automation-agent",
            }
        )

    def commit_file(self, path: Path, destination: str, message: str) -> dict:
        """Create or update a file in the configured repository."""
        content_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        url = f"https://api.github.com/repos/{self._config.repo}/contents/{destination}"
        payload = {
            "message": message,
            "content": content_b64,
            "branch": self._config.branch,
            "committer": {
                "name": self._config.committer_name,
                "email": self._config.committer_email,
            },
        }
        existing_sha = self._get_existing_sha(url)
        if existing_sha:
            payload["sha"] = existing_sha

        response = self._session.put(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def commit_text(self, content: str, destination: str, message: str) -> dict:
        """Convenience wrapper for committing textual content."""
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
        url = f"https://api.github.com/repos/{self._config.repo}/contents/{destination}"
        payload = {
            "message": message,
            "content": content_b64,
            "branch": self._config.branch,
            "committer": {
                "name": self._config.committer_name,
                "email": self._config.committer_email,
            },
        }
        existing_sha = self._get_existing_sha(url)
        if existing_sha:
            payload["sha"] = existing_sha

        response = self._session.put(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def _get_existing_sha(self, url: str) -> Optional[str]:
        response = self._session.get(url, params={"ref": self._config.branch}, timeout=30)
        if response.status_code == 200:
            return response.json().get("sha")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return None