"""Core logic for activity logging and statistics."""

import csv
import json
import uuid
from datetime import timedelta
from pathlib import Path
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
        return config.get_tracker_file()

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

    def remove_activity(self, activity_id: str) -> bool:
        for i, a in enumerate(self.activities):
            if a.id == activity_id:
                del self.activities[i]
                self._save()
                return True
        return False

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
            day = today - timedelta(days=offset)
            date_str = day.strftime("%Y/%m/%d")
            minutes = self.daily_total_minutes(date_str)
            result.append((date_str, minutes))
        return result

    def export_data(self, directory: Path, format: str = "json") -> Path:
        """Export all activities to a file on Desktop. Returns path."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tracker_export.{format}"
        filepath = directory / filename

        activities = self.list_all()
        if format == "json":
            save_json(filepath, [a.to_dict() for a in activities])
        elif format == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Start", "End", "Date"])
                for a in activities:
                    writer.writerow([a.id, a.title, a.start_time, a.end_time, a.date])
        elif format == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("TRACKER - Activity Export\n")
                f.write("=" * 30 + "\n")
                for a in activities:
                    f.write(f"{a.title}: {a.start_time} -> {a.end_time}  ({a.date})\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
        return filepath

    def export_date_data(self, directory: Path, date_str: str, fmt: str) -> Path:
        """Export activities of a specific date to a file."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tracker_{date_str.replace('/', '-')}.{fmt}"
        filepath = directory / filename

        activities = [a for a in self.activities if a.date == date_str]
        if fmt == "json":
            save_json(filepath, [a.to_dict() for a in activities])
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Start", "End", "Date"])
                for a in activities:
                    writer.writerow([a.id, a.title, a.start_time, a.end_time, a.date])
        elif fmt == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                total_seconds = sum(
                    shamsi_diff_seconds(a.start_time, a.end_time) for a in activities
                )
                total_h = int(total_seconds // 3600)
                total_m = int((total_seconds % 3600) // 60)

                f.write(f"TRACKER REPORT - {date_str}\n")
                f.write("=" * 58 + "\n")
                f.write(f"{'Title':<20} {'Start':<12} {'End':<12} {'Duration':>12}\n")
                f.write("-" * 58 + "\n")
                for a in activities:
                    start_hm = a.start_time.split()[1]
                    end_hm = a.end_time.split()[1]
                    secs = shamsi_diff_seconds(a.start_time, a.end_time)
                    h = int(secs // 3600)
                    m = int((secs % 3600) // 60)
                    dur = f"{h}h {m}m"
                    f.write(f"{a.title:<20} {start_hm:<12} {end_hm:<12} {dur:>12}\n")
                f.write("-" * 58 + "\n")
                f.write(f"Total time: {total_h}h {total_m}m\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath

    def export_date_range(
        self, directory: Path, start_date: str, end_date: str, fmt: str
    ) -> Path:
        """Export a summary of each day in a date range."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tracker_{start_date.replace('/', '-')}_to_{end_date.replace('/', '-')}.{fmt}"
        filepath = directory / filename

        start_dt = parse_shamsi_datetime(start_date + " 00:00:00")
        end_dt = parse_shamsi_datetime(end_date + " 00:00:00")

        if fmt == "json":
            data = {}
            current = start_dt
            while current <= end_dt:
                date_str = current.strftime("%Y/%m/%d")
                day_activities = [
                    a.to_dict() for a in self.activities if a.date == date_str
                ]
                data[date_str] = day_activities
                current += timedelta(days=1)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Title", "Start", "End", "Duration (min)"])
                current = start_dt
                while current <= end_dt:
                    date_str = current.strftime("%Y/%m/%d")
                    for a in self.activities:
                        if a.date == date_str:
                            secs = shamsi_diff_seconds(a.start_time, a.end_time)
                            mins = secs / 60
                            writer.writerow(
                                [date_str, a.title, a.start_time, a.end_time, mins]
                            )
                    current += timedelta(days=1)
        elif fmt == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("TRACKER RANGE REPORT\n")
                f.write(f"{start_date}  to  {end_date}\n")
                f.write("=" * 50 + "\n\n")
                current = start_dt
                while current <= end_dt:
                    date_str = current.strftime("%Y/%m/%d")
                    day_activities = [a for a in self.activities if a.date == date_str]
                    total_secs = sum(
                        shamsi_diff_seconds(a.start_time, a.end_time)
                        for a in day_activities
                    )
                    total_h = int(total_secs // 3600)
                    total_m = int((total_secs % 3600) // 60)
                    f.write(f"--- {date_str}  (Total: {total_h}h {total_m}m) ---\n")
                    for a in day_activities:
                        start_hm = a.start_time.split()[1]
                        end_hm = a.end_time.split()[1]
                        f.write(f"  {start_hm} - {end_hm} | {a.title}\n")
                    f.write("\n")
                f.write("=" * 50 + "\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath
