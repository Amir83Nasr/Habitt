"""Tests for tracker TUI helpers."""

from habitt.core.themes import get_active_theme
from habitt.tracker.tracker_manager import TrackerManager
from habitt.tracker.tui import _build_log_table, _build_stats_table, _parse_numbers


def test_parse_numbers():
    assert _parse_numbers("2 4", get_active_theme()) == [2, 4]


def test_build_log_table_today(temp_data_dir):
    manager = TrackerManager()
    manager.add_activity("Work", "1404/08/25 10:00:00", "1404/08/25 12:00:00")
    manager.add_activity("Break", "1404/08/25 12:00:00", "1404/08/25 12:30:00")
    # fake today

    # We'll not filter by today because today is dynamic; we'll test filter by specific date
    table = _build_log_table(manager, date_filter="1404/08/25")
    assert table.row_count == 2


def test_build_stats_table(temp_data_dir):
    manager = TrackerManager()
    table = _build_stats_table(manager)
    assert table.row_count == 7  # 7 days
