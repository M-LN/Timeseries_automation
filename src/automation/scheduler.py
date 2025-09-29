"""Scheduler utilities using APScheduler."""
from __future__ import annotations

from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from src.config import Settings, settings


def build_scheduler(config: Settings = settings) -> BackgroundScheduler:
    """Create a background scheduler configured for the automation agent."""
    scheduler = BackgroundScheduler(timezone=config.scheduler.timezone)
    return scheduler


def schedule_job(
    scheduler: BackgroundScheduler,
    cron_expression: str,
    func: Callable,
    *,
    name: str,
) -> None:
    """Register a job on the provided scheduler."""
    scheduler.add_job(func, trigger="cron", id=name, name=name, **_cron_to_kwargs(cron_expression))


def _cron_to_kwargs(cron_expression: str) -> dict[str, str]:
    """Convert a cron expression string into keyword arguments for APScheduler."""
    minute, hour, day, month, day_of_week = cron_expression.split()
    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
    }
