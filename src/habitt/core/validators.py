"""Input validation helpers for dates and times."""

from rich.console import Console
from rich.prompt import Prompt

from habitt.core.jalali_helper import is_valid_shamsi_date, today_shamsi_str

console = Console()


def _zero_pad_time(text: str) -> str:
    """Convert '7:9' -> '07:09'."""
    if ":" not in text:
        raise ValueError("Time must contain ':'")
    h, m = text.split(":", 1)
    return f"{h.zfill(2)}:{m.zfill(2)}"


def prompt_shamsi_date(prompt_text: str, default_today: bool = False) -> str:
    """Loop until user enters a valid Shamsi date or uses default."""
    while True:
        default_val = today_shamsi_str() if default_today else ""
        user_input = Prompt.ask(prompt_text, default=default_val)
        if not user_input.strip():
            if default_today:
                return today_shamsi_str()
            console.print("[red]Date cannot be empty.[/red]")
            continue
        if is_valid_shamsi_date(user_input.strip()):
            return user_input.strip()
        console.print("[red]Invalid date format. Use YYYY/MM/DD.[/red]")


def prompt_time(prompt_text: str, default: str = None) -> str:
    """Loop until user enters a valid time (HH:MM)."""
    while True:
        user_input = Prompt.ask(prompt_text, default=default if default else "")
        if not user_input.strip():
            if default is not None:
                return default
            console.print("[red]Time cannot be empty.[/red]")
            continue
        try:
            padded = _zero_pad_time(user_input.strip())
            # Validate
            h, m = padded.split(":")
            if 0 <= int(h) <= 23 and 0 <= int(m) <= 59:
                return padded
            else:
                raise ValueError
        except ValueError:
            console.print(
                "[red]Invalid time format. Use HH:MM (e.g., 07:09 or 7:9).[/red]"
            )
