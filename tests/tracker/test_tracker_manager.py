"""Tests for TrackerManager."""

from zoneinfo import ZoneInfo

import jdatetime

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
    # mock today to a known date
    fake_today = jdatetime.datetime(1404, 8, 25, 12, 0, 0, tzinfo=TEHRAN)
    monkeypatch.setattr(
        "habitt.tracker.tracker_manager.parse_shamsi_datetime",
        lambda x: fake_today,
    )
    monkeypatch.setattr(
        "habitt.tracker.tracker_manager.today_shamsi_str",
        lambda: "1404/08/25",
    )

    # Add activity for today
    start = "1404/08/25 10:00:00"
    end = "1404/08/25 12:00:00"
    manager.add_activity("Long task", start, end)  # 120 min

    stats = manager.last_days_stats(7)
    # Should have 7 entries, last one for today = 120.0
    assert len(stats) == 7
    assert stats[-1][0] == "1404/08/25"
    assert stats[-1][1] == 120.0
    # Others zero
    for date_str, mins in stats[:-1]:
        assert mins == 0.0
