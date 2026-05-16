"""Tests for calendar plugin."""

import jdatetime

from habitt.core.themes import get_active_theme
from habitt.plugins.calendar import CalendarPlugin


def test_build_month_table():
    plugin = CalendarPlugin()
    theme = get_active_theme()
    today = jdatetime.date.today()
    table = plugin._build_month_table(today.year, today.month, theme, today)
    assert table.row_count > 0  # at least header and one week
