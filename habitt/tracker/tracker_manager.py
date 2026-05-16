"""Core logic for activity logging, statistics and export.

Manages JSON persistence, exports to multiple formats (including
pretty-printed TXT), and provides date-range summaries.
"""

from __future__ import annotations

import csv
import json
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any

from habitt.core import config
from habitt.core.jalali_helper import (
    is_valid_shamsi_date,
    parse_shamsi_datetime,
    shamsi_diff_seconds,
    today_shamsi_str,
)
from habitt.core.storage import load_json, save_json
from habitt.tracker.models import Activity


class TrackerManager:
    """Manages the collection of logged activities."""

    def __init__(self) -> None:
        self.activities: list[Activity] = []
        self._load()

    def _filepath(self) -> Path:
        """Return the path to the tracker JSON file."""
        return config.get_tracker_file()

    def _load(self) -> None:
        """Load activities from the JSON file."""
        data = load_json(self._filepath())
        self.activities = [Activity.from_dict(item) for item in data]

    def _save(self) -> None:
        """Persist activities to the JSON file."""
        save_json(self._filepath(), [a.to_dict() for a in self.activities])

    def add_activity(self, title: str, start_time: str, end_time: str) -> Activity:
        """Create a new activity, assign an ID, and persist."""
        activity = Activity(title=title, start_time=start_time, end_time=end_time)
        activity.id = uuid.uuid4().hex[:6]
        self.activities.append(activity)
        self._save()
        return activity

    def remove_activity(self, activity_id: str) -> bool:
        """Remove an activity by its ID. Returns True if found."""
        for i, a in enumerate(self.activities):
            if a.id == activity_id:
                del self.activities[i]
                self._save()
                return True
        return False

    def list_today(self) -> list[Activity]:
        """Return activities whose date matches today."""
        today = today_shamsi_str()
        return [a for a in self.activities if a.date == today]

    def list_all(self) -> list[Activity]:
        """Return all activities."""
        return self.activities

    def daily_total_minutes(self, date_str: str) -> float:
        """Total logged minutes for a given Shamsi date."""
        total_seconds = 0.0
        for a in self.activities:
            if a.date == date_str:
                total_seconds += shamsi_diff_seconds(a.start_time, a.end_time)
        return total_seconds / 60.0

    def last_days_stats(self, days: int = 7) -> list[tuple[str, float]]:
        """Return (date, total_minutes) for the last `days` including today."""
        today = parse_shamsi_datetime(today_shamsi_str() + " 00:00:00")
        result = []
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            date_str = day.strftime("%Y/%m/%d")
            minutes = self.daily_total_minutes(date_str)
            result.append((date_str, minutes))
        return result

    # ----- Export helpers -------------------------------------------------
    def export_data(self, directory: Path, fmt: str = "json") -> Path:
        """Export all activities to a file with beautiful formatting."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tracker_export.{fmt}"
        filepath = directory / filename

        activities = self.list_all()
        if fmt == "json":
            save_json(filepath, [a.to_dict() for a in activities])
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Title", "Start", "End", "Duration"])
                for a in activities:
                    secs = shamsi_diff_seconds(a.start_time, a.end_time)
                    h = int(secs // 3600)
                    m = int((secs % 3600) // 60)
                    dur = f"{h}h {m}m"
                    writer.writerow([a.date, a.title, a.start_time, a.end_time, dur])
        elif fmt == "txt":
            # Group by date
            dates: dict[str, list[Activity]] = {}
            for a in activities:
                dates.setdefault(a.date, []).append(a)

            # Calculate maximum title width across all activities
            all_titles = [a.title for a in activities]
            max_title_width = max((len(t) for t in all_titles), default=5)
            max_title_width = min(max_title_width, 50)  # Limit to keep table reasonable

            # Fixed widths
            num_width = 4
            start_width = 8
            end_width = 8
            dur_width = 10

            # Total table width
            table_width = (
                num_width + max_title_width + start_width + end_width + dur_width + 10
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n")
                f.write("  TRACKER - ALL ACTIVITIES\n")
                f.write("  " + "=" * (table_width - 4) + "\n\n")

                grand_total_secs = 0.0
                day_count = 0

                for date_str in sorted(dates.keys()):
                    day_activities = dates[date_str]
                    day_secs = sum(
                        shamsi_diff_seconds(a.start_time, a.end_time)
                        for a in day_activities
                    )
                    grand_total_secs += day_secs
                    day_h = int(day_secs // 3600)
                    day_m = int((day_secs % 3600) // 60)
                    day_count += 1

                    # Day header
                    f.write(f"  {date_str}")
                    f.write(f"  (Total: {day_h}h {day_m}m)")
                    f.write(f"  - {len(day_activities)} activities\n")
                    f.write("  " + "-" * (table_width - 4) + "\n")

                    # Table header
                    f.write(
                        f"  {'#':<{num_width}}"
                        f"{'Title':<{max_title_width}}"
                        f"{'Start':>{start_width}}"
                        f"{'End':>{end_width}}"
                        f"{'Duration':>{dur_width}}\n"
                    )
                    f.write("  " + "-" * (table_width - 4) + "\n")

                    for i, a in enumerate(day_activities, start=1):
                        start_hm = a.start_time.split()[1][:5]
                        end_hm = a.end_time.split()[1][:5]
                        secs = shamsi_diff_seconds(a.start_time, a.end_time)
                        h = int(secs // 3600)
                        m = int((secs % 3600) // 60)
                        dur = f"{h}h {m}m"

                        # Truncate title if too long
                        title = a.title[:max_title_width]

                        f.write(
                            f"  {i:<{num_width}}"
                            f"{title:<{max_title_width}}"
                            f"{start_hm:>{start_width}}"
                            f"{end_hm:>{end_width}}"
                            f"{dur:>{dur_width}}\n"
                        )

                    f.write("  " + "-" * (table_width - 4) + "\n\n")

                # Grand total
                grand_h = int(grand_total_secs // 3600)
                grand_m = int((grand_total_secs % 3600) // 60)

                f.write("  " + "=" * (table_width - 4) + "\n")
                f.write(
                    f"  {day_count} days  |  "
                    f"{len(activities)} activities  |  "
                    f"Total: {grand_h}h {grand_m}m\n"
                )
                f.write("  " + "=" * (table_width - 4) + "\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath

    def export_date_data(self, directory: Path, date_str: str, fmt: str) -> Path:
        """Export activities of a specific date with beautiful formatting."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tracker_{date_str.replace('/', '-')}.{fmt}"
        filepath = directory / filename

        activities = [a for a in self.activities if a.date == date_str]
        if fmt == "json":
            save_json(filepath, [a.to_dict() for a in activities])
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "Start", "End", "Duration"])
                for a in activities:
                    secs = shamsi_diff_seconds(a.start_time, a.end_time)
                    h = int(secs // 3600)
                    m = int((secs % 3600) // 60)
                    dur = f"{h}h {m}m"
                    writer.writerow([a.title, a.start_time, a.end_time, dur])
        elif fmt == "txt":
            total_seconds = sum(
                shamsi_diff_seconds(a.start_time, a.end_time) for a in activities
            )
            total_h = int(total_seconds // 3600)
            total_m = int((total_seconds % 3600) // 60)

            # محاسبهٔ پهنای ستون‌ها
            title_width = max((len(a.title) for a in activities), default=5)
            title_width = max(title_width, 5)  # حداقل ۵
            # عرض کل جدول
            table_width = (
                7 + title_width + 14 + 10 + 10 + 10
            )  # # + Title + Date + Start + End + Duration

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"TRACKER REPORT - {date_str}\n")
                f.write("=" * table_width + "\n")

                # هدر
                f.write(
                    f"{'#':<5}  "
                    f"{'Title':<{title_width}}  "
                    f"{'Date':<10}  "
                    f"{'Start':<8}  "
                    f"{'End':<8}  "
                    f"{'Duration':>8}\n"
                )
                f.write("-" * table_width + "\n")

                if not activities:
                    f.write("No activities recorded on this day.\n")
                else:
                    for i, a in enumerate(activities, start=1):
                        start_hm = a.start_time.split()[1][:5]  # فقط HH:MM
                        end_hm = a.end_time.split()[1][:5]
                        secs = shamsi_diff_seconds(a.start_time, a.end_time)
                        h = int(secs // 3600)
                        m = int((secs % 3600) // 60)
                        dur = f"{h}h {m}m"
                        f.write(
                            f"{i:<5}  "
                            f"{a.title:<{title_width}}  "
                            f"{a.date:<10}  "
                            f"{start_hm:<8}  "
                            f"{end_hm:<8}  "
                            f"{dur:>8}\n"
                        )

                f.write("-" * table_width + "\n")
                f.write(f"Total time: {total_h}h {total_m}m\n")
                f.write("=" * table_width + "\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath

    def export_date_range(
        self, directory: Path, start_date: str, end_date: str, fmt: str
    ) -> Path:
        """Export a summary of each day in a date range with beautiful formatting."""
        if not is_valid_shamsi_date(start_date):
            raise ValueError(f"Invalid start date: {start_date}")
        if not is_valid_shamsi_date(end_date):
            raise ValueError(f"Invalid end date: {end_date}")

        directory.mkdir(parents=True, exist_ok=True)
        filename = (
            f"tracker_{start_date.replace('/', '-')}"
            f"_to_{end_date.replace('/', '-')}.{fmt}"
        )
        filepath = directory / filename

        start_dt = parse_shamsi_datetime(start_date + " 00:00:00")
        end_dt = parse_shamsi_datetime(end_date + " 00:00:00")

        if fmt == "json":
            data: dict[str, list[dict[str, Any]]] = {}
            current = start_dt
            while current <= end_dt:
                date_str = current.strftime("%Y/%m/%d")
                day_dicts = [a.to_dict() for a in self.activities if a.date == date_str]
                data[date_str] = day_dicts
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
            # Collect all activities in range for width calculation
            range_activities: list[Activity] = []
            current = start_dt
            while current <= end_dt:
                date_str = current.strftime("%Y/%m/%d")
                range_activities.extend(
                    a for a in self.activities if a.date == date_str
                )
                current += timedelta(days=1)

            max_title_width = max((len(a.title) for a in range_activities), default=5)
            max_title_width = min(max_title_width, 50)

            num_width = 4
            start_width = 8
            end_width = 8
            dur_width = 10
            table_width = (
                num_width + max_title_width + start_width + end_width + dur_width + 10
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n")
                f.write("  TRACKER - DATE RANGE REPORT\n")
                f.write(f"  {start_date}  to  {end_date}\n")
                f.write("  " + "=" * (table_width - 4) + "\n\n")

                grand_total_secs = 0.0
                day_count = 0
                total_activities = 0

                current = start_dt
                while current <= end_dt:
                    date_str = current.strftime("%Y/%m/%d")
                    day_activities = [a for a in self.activities if a.date == date_str]
                    day_secs = sum(
                        shamsi_diff_seconds(a.start_time, a.end_time)
                        for a in day_activities
                    )
                    grand_total_secs += day_secs
                    day_h = int(day_secs // 3600)
                    day_m = int((day_secs % 3600) // 60)

                    if day_activities:
                        day_count += 1
                        total_activities += len(day_activities)

                        # Day header
                        f.write(
                            f"  {date_str}  "
                            f"(Total: {day_h}h {day_m}m)  "
                            f"- {len(day_activities)} activities\n"
                        )
                        f.write("  " + "-" * (table_width - 4) + "\n")

                        # Table header
                        f.write(
                            f"  {'#':<{num_width}}"
                            f"{'Title':<{max_title_width}}"
                            f"{'Start':>{start_width}}"
                            f"{'End':>{end_width}}"
                            f"{'Duration':>{dur_width}}\n"
                        )
                        f.write("  " + "-" * (table_width - 4) + "\n")

                        for i, a in enumerate(day_activities, start=1):
                            start_hm = a.start_time.split()[1][:5]
                            end_hm = a.end_time.split()[1][:5]
                            secs = shamsi_diff_seconds(a.start_time, a.end_time)
                            h = int(secs // 3600)
                            m = int((secs % 3600) // 60)
                            dur = f"{h}h {m}m"
                            title = a.title[:max_title_width]

                            f.write(
                                f"  {i:<{num_width}}"
                                f"{title:<{max_title_width}}"
                                f"{start_hm:>{start_width}}"
                                f"{end_hm:>{end_width}}"
                                f"{dur:>{dur_width}}\n"
                            )

                        f.write("  " + "-" * (table_width - 4) + "\n\n")
                    else:
                        # Day with no activities
                        f.write(f"  {date_str}  -  No activities\n\n")

                    current += timedelta(days=1)

                # Grand total
                grand_h = int(grand_total_secs // 3600)
                grand_m = int((grand_total_secs % 3600) // 60)

                f.write("  " + "=" * (table_width - 4) + "\n")
                f.write(
                    f"  {day_count} active days  |  "
                    f"{total_activities} activities  |  "
                    f"Total: {grand_h}h {grand_m}m\n"
                )
                f.write("  " + "=" * (table_width - 4) + "\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath
