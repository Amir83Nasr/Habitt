"""Core logic for activity logging and statistics."""

import uuid
from typing import List, Tuple

from habitt.core.config import TRACKER_FILE
from habitt.core.storage import load_json, save_json
from habitt.core.jalali_helper import (
    shamsi_diff_seconds,
    today_shamsi_str,
    parse_shamsi_datetime,
)
from habitt.tracker.models import Activity


class TrackerManager:
    def __init__(self) -> None:
        self.activities: List[Activity] = []
        self._load()

    def _load(self) -> None:
        data = load_json(TRACKER_FILE)
        self.activities = [Activity.from_dict(item) for item in data]

    def _save(self) -> None:
        save_json(TRACKER_FILE, [a.to_dict() for a in self.activities])

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
        """Total logged minutes for a given Shamsi date."""
        total_seconds = 0.0
        for a in self.activities:
            if a.date == date_str:
                total_seconds += shamsi_diff_seconds(a.start_time, a.end_time)
        return total_seconds / 60.0

    def last_days_stats(self, days: int = 7) -> List[Tuple[str, float]]:
        """Return list of (date, total_minutes) for the last `days` including today."""
        today = parse_shamsi_datetime(today_shamsi_str() + " 00:00:00")
        result = []
        for offset in range(days - 1, -1, -1):
            day = today - offset  # jdatetime supports timedelta arithmetic
            date_str = day.strftime("%Y/%m/%d")
            minutes = self.daily_total_minutes(date_str)
            result.append((date_str, minutes))
        return result
