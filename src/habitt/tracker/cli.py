"""Click-based CLI for quick tracker commands (start/pause/resume/stop)."""

import json
from dataclasses import asdict, dataclass
from typing import Optional

import click

from habitt.core.config import TIMER_STATE_FILE
from habitt.core.jalali_helper import (
    now_shamsi_str,
    now_tehran,
    parse_shamsi_datetime,
)
from habitt.tracker.tracker_manager import TrackerManager
from habitt.tracker.tui import show_log, show_stats


@dataclass
class TimerState:
    title: str
    start_time: str
    paused: bool = False
    pause_start: Optional[str] = None
    total_paused_seconds: float = 0.0


def _load_timer_state() -> Optional[TimerState]:
    if not TIMER_STATE_FILE.exists():
        return None
    with open(TIMER_STATE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return TimerState(**data)


def _save_timer_state(state: TimerState) -> None:
    with open(TIMER_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)


def _clear_timer_state() -> None:
    TIMER_STATE_FILE.unlink(missing_ok=True)


@click.group()
def main() -> None:
    """Tracker - Daily activity logger. Run without subcommand for TUI."""
    pass


@main.command()
@click.argument("title")
def start(title: str) -> None:
    """Start a new timer for an activity."""
    if _load_timer_state():
        click.echo("A timer is already running. Stop it first.")
        return
    state = TimerState(
        title=title,
        start_time=now_shamsi_str(),
        paused=False,
        pause_start=None,
        total_paused_seconds=0.0,
    )
    _save_timer_state(state)
    click.echo(f"Timer started for '{title}'.")


@main.command()
def pause() -> None:
    """Pause the running timer."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return
    if state.paused:
        click.echo("Timer is already paused.")
        return
    state.paused = True
    state.pause_start = now_shamsi_str()
    _save_timer_state(state)
    click.echo("Timer paused.")


@main.command()
def resume() -> None:
    """Resume a paused timer."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return
    if not state.paused:
        click.echo("Timer is not paused.")
        return
    # Add paused duration
    pause_dt = parse_shamsi_datetime(state.pause_start)
    now_dt = now_tehran()
    paused_seconds = (now_dt - pause_dt).total_seconds()
    state.total_paused_seconds += paused_seconds
    state.paused = False
    state.pause_start = None
    _save_timer_state(state)
    click.echo("Timer resumed.")


@main.command()
def stop() -> None:
    """Stop the timer and save the activity."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return
    # Finalize pause if necessary
    if state.paused and state.pause_start:
        pause_dt = parse_shamsi_datetime(state.pause_start)
        now_dt = now_tehran()
        state.total_paused_seconds += (now_dt - pause_dt).total_seconds()

    end_time = now_shamsi_str()
    manager = TrackerManager()
    manager.add_activity(state.title, state.start_time, end_time)
    _clear_timer_state()
    click.echo(f"Timer stopped. Activity '{state.title}' saved.")


@main.command()
def log() -> None:
    """Show today's activities."""
    manager = TrackerManager()
    show_log(manager)


@main.command()
def stats() -> None:
    """Show statistics for the last 7 days."""
    manager = TrackerManager()
    show_stats(manager)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tracker.tui import main_menu as tracker_tui

        tracker_tui()
    else:
        main()
