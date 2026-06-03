"""Jalali (Shamsi) date/time helpers using jdatetime and zoneinfo."""

from __future__ import annotations

from datetime import datetime, tzinfo
from typing import cast
from zoneinfo import ZoneInfo

import jdatetime

TEHRAN_TZ: tzinfo = ZoneInfo("Asia/Tehran")


def now_shamsi_str() -> str:
    """Return current Jalali datetime as string (YYYY/MM/DD HH:MM:SS)."""
    result = now_tehran().strftime("%Y/%m/%d %H:%M:%S")
    return cast(str, result)


def today_shamsi_str() -> str:
    """Return today's Jalali date as YYYY/MM/DD."""
    result = now_tehran().strftime("%Y/%m/%d")
    return cast(str, result)


def format_shamsi_datetime(dt: jdatetime.datetime) -> str:
    result = dt.strftime("%Y/%m/%d %H:%M:%S")
    return cast(str, result)


def shamsi_diff_seconds(start_str: str, end_str: str) -> float:
    start_dt = parse_shamsi_datetime(start_str)
    end_dt = parse_shamsi_datetime(end_str)
    diff = end_dt - start_dt
    seconds = diff.total_seconds()
    return cast(float, seconds)


def now_tehran() -> jdatetime.datetime:
    """Return current Jalali datetime in Asia/Tehran timezone."""
    gregorian_now = datetime.now(TEHRAN_TZ)
    result = jdatetime.datetime.fromgregorian(datetime=gregorian_now)
    assert isinstance(result, jdatetime.datetime)
    return result


def parse_shamsi_datetime(text: str) -> jdatetime.datetime:
    """
    Parse a Shamsi datetime string (YYYY/MM/DD HH:MM[:SS]) into a
    timezone-aware jdatetime.datetime.
    """
    parts = text.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid Shamsi datetime format: {text}")
    date_part, time_part = parts
    year, month, day = map(int, date_part.split("/"))
    hour, minute, *sec = map(int, time_part.split(":"))
    second = sec[0] if sec else 0

    naive = jdatetime.datetime(year, month, day, hour, minute, second)
    result = naive.replace(tzinfo=TEHRAN_TZ)
    return cast(jdatetime.datetime, result)


def is_valid_shamsi_date(text: str) -> bool:
    try:
        parts = text.strip().split("/")
        if len(parts) != 3:
            return False
        year, month, day = map(int, parts)
        jdatetime.date(year, month, day)
        return True
    except (ValueError, OverflowError):
        return False
