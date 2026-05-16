"""Tests for TrackerManager."""

import json
from datetime import timedelta
from zoneinfo import ZoneInfo

import jdatetime
import pytest

from habitt.core.jalali_helper import parse_shamsi_datetime
from habitt.tracker.tracker_manager import TrackerManager

TEHRAN = ZoneInfo("Asia/Tehran")


def _make_time(year, month, day, hour, minute):
    dt = jdatetime.datetime(year, month, day, hour, minute, tzinfo=TEHRAN)
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def test_add_activity(temp_data_dir):
    manager = TrackerManager()
    start = _make_time(1404, 8, 23, 10, 0)
    end = _make_time(1404, 8, 23, 11, 30)
    activity = manager.add_activity("Work", start, end)
    assert activity.title == "Work"
    assert activity.date == "1404/08/23"
    assert len(manager.activities) == 1


def test_list_today(temp_data_dir, monkeypatch):
    manager = TrackerManager()
    # Add an activity for today
    today_str = "1404/08/24"  # assume today is this date
    # We'll mock today_shamsi_str to return that
    from habitt.tracker import tracker_manager

    monkeypatch.setattr(tracker_manager, "today_shamsi_str", lambda: today_str)

    start = f"{today_str} 09:00:00"
    end = f"{today_str} 10:00:00"
    manager.add_activity("Today task", start, end)

    # Add an activity for another day
    other_start = "1404/08/23 09:00:00"
    other_end = "1404/08/23 10:00:00"
    manager.add_activity("Yesterday", other_start, other_end)

    today_activities = manager.list_today()
    assert len(today_activities) == 1
    assert today_activities[0].title == "Today task"


def test_daily_total_minutes(temp_data_dir):
    manager = TrackerManager()
    date = "1404/08/24"
    start = f"{date} 09:00:00"
    end = f"{date} 10:30:00"
    manager.add_activity("Task", start, end)

    minutes = manager.daily_total_minutes(date)
    assert minutes == 90.0


def test_last_days_stats(temp_data_dir, monkeypatch):
    manager = TrackerManager()

    # Add an activity for a known date: today
    from habitt.core.jalali_helper import today_shamsi_str

    today = today_shamsi_str()
    start = f"{today} 10:00:00"
    end = f"{today} 12:00:00"
    manager.add_activity("Long task", start, end)  # 120 min

    # Also add an activity for yesterday (to verify ordering)
    yesterday_dt = parse_shamsi_datetime(f"{today} 00:00:00") - timedelta(days=1)
    yesterday_str = yesterday_dt.strftime("%Y/%m/%d")
    start_y = f"{yesterday_str} 08:00:00"
    end_y = f"{yesterday_str} 09:00:00"
    manager.add_activity("Short", start_y, end_y)  # 60 min

    stats = manager.last_days_stats(7)
    # Should have 7 entries, last two are yesterday and today
    assert len(stats) == 7
    assert stats[-1][0] == today
    assert stats[-1][1] == 120.0
    assert stats[-2][0] == yesterday_str
    assert stats[-2][1] == 60.0
    # Earlier days should be zero
    for _date_str, mins in stats[:-2]:
        assert mins == 0.0


def test_export_json(temp_data_dir):
    manager = TrackerManager()
    manager.add_activity("A", "1404/08/25 10:00:00", "1404/08/25 11:00:00")
    path = manager.export_data(temp_data_dir, "json")
    assert path.exists()
    data = json.load(open(path))
    assert len(data) == 1


def test_export_date_data_txt(temp_data_dir):
    manager = TrackerManager()
    manager.add_activity("A", "1404/08/25 10:00:00", "1404/08/25 11:00:00")
    path = manager.export_date_data(temp_data_dir, "1404/08/25", "txt")
    assert path.exists()
    content = path.read_text()
    assert "TRACKER REPORT" in content
    assert "Total time: 1h 0m" in content


def test_export_date_range_txt(temp_data_dir):
    manager = TrackerManager()
    manager.add_activity("A", "1404/08/25 10:00:00", "1404/08/25 11:00:00")
    path = manager.export_date_range(temp_data_dir, "1404/08/25", "1404/08/25", "txt")
    assert path.exists()


def test_export_invalid_format(temp_data_dir):
    manager = TrackerManager()
    with pytest.raises(ValueError):
        manager.export_data(temp_data_dir, "xml")


def test_export_date_range_invalid_date(temp_data_dir):
    manager = TrackerManager()
    with pytest.raises(ValueError):
        manager.export_date_range(temp_data_dir, "invalid", "1404/08/25", "txt")
