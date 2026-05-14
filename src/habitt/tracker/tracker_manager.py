"""Core logic for activity logging and statistics."""

import uuid
from datetime import timedelta
from typing import List, Tuple

from habitt.core import config
from habitt.core.jalali_helper import (
    parse_shamsi_datetime,
    shamsi_diff_seconds,
    today_shamsi_str,
)
from habitt.core.storage import load_json, save_json
from habitt.tracker.models import Activity


class TrackerManager:
    def __init__(self) -> None:
        self.activities: List[Activity] = []
        self._load()

    def _filepath(self):
        return config.TRACKER_FILE

    def _load(self) -> None:
        data = load_json(self._filepath())
        self.activities = [Activity.from_dict(item) for item in data]

    def _save(self) -> None:
        save_json(self._filepath(), [a.to_dict() for a in self.activities])

    def add_activity(self, title: str, start_time: str, end_time: str) -> Activity:
        activity = Activity(title=title, start_time=start_time, end_time=end_time)
        activity.id = uuid.uuid4().hex[:6]
        self.activities.append(activity)
        self._save()
        return activity

    def list_today(self) -> List[Activity]:
        today = today_shamsi_str()
        return [a for a in self.activities if a.date == today]

    def list_all(self) -> List[Activity]:
        return self.activities

    def daily_total_minutes(self, date_str: str) -> float:
        total_seconds = 0.0
        for a in self.activities:
            if a.date == date_str:
                total_seconds += shamsi_diff_seconds(a.start_time, a.end_time)
        return total_seconds / 60.0

    def last_days_stats(self, days: int = 7) -> List[Tuple[str, float]]:
        today = parse_shamsi_datetime(today_shamsi_str() + " 00:00:00")
        result = []
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)  # FIXED: use timedelta
            date_str = day.strftime("%Y/%m/%d")
            minutes = self.daily_total_minutes(date_str)
            result.append((date_str, minutes))
        return result
