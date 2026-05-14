"""Jalali (Shamsi) date/time helpers using jdatetime and zoneinfo."""

from datetime import datetime
from zoneinfo import ZoneInfo

import jdatetime

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def now_tehran() -> jdatetime.datetime:
    """Return current Jalali datetime in Asia/Tehran timezone."""
    gregorian_now = datetime.now(TEHRAN_TZ)
    return jdatetime.datetime.fromgregorian(datetime=gregorian_now)


def now_shamsi_str() -> str:
    """Return current Jalali datetime as string (YYYY/MM/DD HH:MM:SS)."""
    return now_tehran().strftime("%Y/%m/%d %H:%M:%S")


def today_shamsi_str() -> str:
    """Return today's Jalali date as YYYY/MM/DD."""
    return now_tehran().strftime("%Y/%m/%d")


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

    # Build a naive Jalali datetime, then attach Tehran timezone
    naive = jdatetime.datetime(year, month, day, hour, minute, second)
    return naive.replace(tzinfo=TEHRAN_TZ)


def format_shamsi_datetime(dt: jdatetime.datetime) -> str:
    """Format a jdatetime.datetime as 'YYYY/MM/DD HH:MM:SS'."""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def shamsi_diff_seconds(start_str: str, end_str: str) -> float:
    """Return (end - start) in seconds."""
    start_dt = parse_shamsi_datetime(start_str)
    end_dt = parse_shamsi_datetime(end_str)
    return (end_dt - start_dt).total_seconds()
