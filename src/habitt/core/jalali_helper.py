"""Jalali (Shamsi) date/time helpers using jdatetime."""

from datetime import datetime

import jdatetime


def now_tehran() -> jdatetime.datetime:
    """Return current Jalali datetime in Asia/Tehran timezone."""
    return jdatetime.datetime.now(jdatetime.timezone("Asia/Tehran"))


def now_shamsi_str() -> str:
    """Return current Jalali datetime as string (YYYY/MM/DD HH:MM:SS)."""
    return now_tehran().strftime("%Y/%m/%d %H:%M:%S")


def today_shamsi_str() -> str:
    """Return today's Jalali date as YYYY/MM/DD."""
    return now_tehran().strftime("%Y/%m/%d")


def parse_shamsi_datetime(text: str) -> jdatetime.datetime:
    """Parse a Shamsi datetime string (YYYY/MM/DD HH:MM[:SS]) into jdatetime.datetime."""
    # Expects format like '1404/08/23 14:30'
    parts = text.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid Shamsi datetime format: {text}")
    date_part, time_part = parts
    year, month, day = map(int, date_part.split("/"))
    hour, minute, *sec = map(int, time_part.split(":"))
    second = sec[0] if sec else 0
    return jdatetime.datetime(
        year, month, day, hour, minute, second, tzinfo=jdatetime.timezone("Asia/Tehran")
    )


def format_shamsi_datetime(dt: jdatetime.datetime) -> str:
    """Format a jdatetime.datetime as 'YYYY/MM/DD HH:MM:SS'."""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def shamsi_diff_seconds(start_str: str, end_str: str) -> float:
    """Return (end - start) in seconds."""
    start_dt = parse_shamsi_datetime(start_str)
    end_dt = parse_shamsi_datetime(end_str)
    return (end_dt - start_dt).total_seconds()
