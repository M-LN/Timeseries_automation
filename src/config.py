"""Configuration management for the timeseries automation agent."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

load_dotenv()


@dataclass
class APISettings:
    """Holds API configuration values loaded from environment variables or secrets."""

    openweather_api_key: Optional[str] = None
    nordpool_api_key: Optional[str] = None
    slack_token: Optional[str] = None
    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    github_branch: str = "main"
    github_committer_name: str = "Automation Agent"
    github_committer_email: str = "automation@example.com"


@dataclass
class DatabaseSettings:
    """Database connection configuration."""

    database_url: str = "sqlite:///data/timeseries.db"


@dataclass
class SchedulerSettings:
    """Automation scheduler configuration."""

    timezone: str = "Europe/Copenhagen"
    fetch_cron: str = "0 5 * * *"  # default: every day at 05:00
    retrain_cron: str = "0 6 * * 1"  # default: every Monday at 06:00


@dataclass
class Settings:
    """Aggregated settings for the automation agent."""

    apis: APISettings = field(default_factory=APISettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    scheduler: SchedulerSettings = field(default_factory=SchedulerSettings)


def load_settings() -> Settings:
    return Settings(
        apis=APISettings(
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            nordpool_api_key=os.getenv("NORDPOOL_API_KEY"),
            slack_token=os.getenv("SLACK_TOKEN"),
            notion_token=os.getenv("NOTION_TOKEN"),
            notion_database_id=os.getenv("NOTION_DATABASE_ID"),
            github_token=os.getenv("GITHUB_TOKEN"),
            github_repo=os.getenv("GITHUB_REPO"),
            github_branch=os.getenv("GITHUB_BRANCH", "main"),
            github_committer_name=os.getenv("GITHUB_COMMITTER_NAME", "Automation Agent"),
            github_committer_email=os.getenv("GITHUB_COMMITTER_EMAIL", "automation@example.com"),
        ),
        database=DatabaseSettings(
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/timeseries.db"),
        ),
        scheduler=SchedulerSettings(
            timezone=os.getenv("SCHEDULER_TIMEZONE", "Europe/Copenhagen"),
            fetch_cron=os.getenv("FETCH_CRON", "0 5 * * *"),
            retrain_cron=os.getenv("RETRAIN_CRON", "0 6 * * 1"),
        ),
    )


settings = load_settings()
