"""Tests for Jalali date/time helpers."""

import jdatetime
import pytest

from habitt.core.jalali_helper import (
    TEHRAN_TZ,
    format_shamsi_datetime,
    now_shamsi_str,
    now_tehran,
    parse_shamsi_datetime,
    shamsi_diff_seconds,
    today_shamsi_str,
)


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


def test_parse_shamsi_datetime_invalid():
    with pytest.raises(ValueError):
        parse_shamsi_datetime("invalid")
    with pytest.raises(ValueError):
        parse_shamsi_datetime("1404/01/01")


def test_format_shamsi_datetime():

    dt = jdatetime.datetime(1404, 8, 25, 14, 30, 45, tzinfo=TEHRAN_TZ)
    result = format_shamsi_datetime(dt)
    assert result == "1404/08/25 14:30:45"


def test_shamsi_diff_seconds():
    diff = shamsi_diff_seconds("1404/08/25 10:00:00", "1404/08/25 10:30:00")
    assert diff == 1800.0
