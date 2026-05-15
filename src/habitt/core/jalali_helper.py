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


def is_valid_shamsi_date(text: str) -> bool:
    try:
        parts = text.strip().split("/")
        if len(parts) != 3:
            return False
        y, m, d = map(int, parts)
        jdatetime.date(y, m, d)
        return True
    except Exception:
        return False


def validate_time_format(text: str) -> bool:
    """Check if text is a valid time like HH:MM (with optional zero-pad)."""
    if ":" not in text:
        return False
    try:
        h, m = text.split(":", 1)
        h = h.zfill(2)
        m = m.zfill(2)
        if not (0 <= int(h) <= 23) or not (0 <= int(m) <= 59):
            return False
        return True
    except ValueError:
        return False


def prompt_shamsi_date(prompt_text: str, default_today: bool = False) -> str:
    """
    Prompt the user for a Shamsi date (YYYY/MM/DD).
    If default_today is True, empty input returns today's date.
    Repeats until a valid date is entered.
    """
    while True:
        user_input = Prompt.ask(
            prompt_text, default=today_shamsi_str() if default_today else ""
        )
        if not user_input.strip():
            if default_today:
                return today_shamsi_str()
            console.print("[red]Date cannot be empty.[/red]")
            continue
        if is_valid_shamsi_date(user_input.strip()):
            return user_input.strip()
        console.print(
            "[red]Invalid date format. Use YYYY/MM/DD (e.g., 1404/08/25).[/red]"
        )


def prompt_time(prompt_text: str, default: Optional[str] = None) -> str:
    """
    Prompt for a time (HH:MM). If default is given, empty input returns default.
    Automatically zero-pads and validates.
    """
    while True:
        user_input = Prompt.ask(prompt_text, default=default if default else "")
        if not user_input.strip():
            if default is not None:
                return default
            console.print("[red]Time cannot be empty. Please enter HH:MM.[/red]")
            continue
        try:
            padded = _zero_pad_time(user_input.strip())
            if not validate_time_format(padded):
                raise ValueError
            return padded
        except ValueError:
            console.print(
                "[red]Invalid time format. Use HH:MM (e.g., 07:09 or 7:9).[/red]"
            )
