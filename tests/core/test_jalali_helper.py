"""Tests for Jalali date/time helpers."""

import jdatetime

from habitt.core.jalali_helper import (format_shamsi_datetime, now_shamsi_str,
                                       now_tehran, parse_shamsi_datetime,
                                       shamsi_diff_seconds, today_shamsi_str)


def test_now_tehran_returns_jdatetime():
    result = now_tehran()
    assert isinstance(result, jdatetime.datetime)
    assert result.tzinfo is not None


def test_now_shamsi_str_format():
    result = now_shamsi_str()
    # Should match YYYY/MM/DD HH:MM:SS
    parts = result.split()
    assert len(parts) == 2
    date_part, time_part = parts
    assert len(date_part.split("/")) == 3
    assert len(time_part.split(":")) == 3


def test_today_shamsi_str():
    result = today_shamsi_str()
    assert len(result.split("/")) == 3


def test_parse_shamsi_datetime():
    dt_str = "1404/08/23 14:30:45"
    dt = parse_shamsi_datetime(dt_str)
    assert dt.year == 1404
    assert dt.month == 8
    assert dt.day == 23
    assert dt.hour == 14
    assert dt.minute == 30
    assert dt.second == 45
    assert dt.tzinfo is not None


def test_format_shamsi_datetime():
    dt = jdatetime.datetime(1404, 8, 23, 14, 30, 45)
    formatted = format_shamsi_datetime(dt)
    assert formatted == "1404/08/23 14:30:45"


def test_shamsi_diff_seconds():
    start = "1404/08/23 14:00:00"
    end = "1404/08/23 14:30:25"
    diff = shamsi_diff_seconds(start, end)
    assert diff == (30 * 60) + 25  # 30 minutes 25 seconds
