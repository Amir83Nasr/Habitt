"""Click-based CLI for quick tracker commands (start/pause/resume/stop)."""

import json
from dataclasses import asdict, dataclass
from typing import Optional

import click
import click_completion
from rich.console import Console

from habitt.core.config import get_timer_state_file
from habitt.core.jalali_helper import (now_shamsi_str, now_tehran,
                                       parse_shamsi_datetime, today_shamsi_str)
from habitt.tracker.tracker_manager import TrackerManager
from habitt.tracker.tui import _build_log_table, _build_stats_table

console = Console()


@dataclass
class TimerState:
    title: str
    start_time: str
    paused: bool = False
    pause_start: Optional[str] = None
    total_paused_seconds: float = 0.0


def _load_timer_state() -> Optional[TimerState]:
    filepath = get_timer_state_file()
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    return TimerState(**data)


def _save_timer_state(state: TimerState) -> None:
    filepath = get_timer_state_file()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)


def _clear_timer_state() -> None:
    filepath = get_timer_state_file()
    filepath.unlink(missing_ok=True)


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
    table = _build_log_table(manager, date_filter=today_shamsi_str())
    console.print(table)


@main.command()
def stats() -> None:
    """Show statistics for the last 7 days."""
    manager = TrackerManager()
    table = _build_stats_table(manager)
    console.print(table)


@main.command()
@click.option(
    "--format", "-f", "fmt", default="json", type=click.Choice(["json", "csv", "txt"])
)
def export(fmt: str) -> None:
    """Export all activities to Desktop."""
    from pathlib import Path

    manager = TrackerManager()
    desktop = Path.home() / "Desktop"
    path = manager.export_data(desktop, fmt)
    click.echo(f"Exported to {path}")


@main.command()
@click.option("--force", is_flag=True, help="Skip confirmation")
def reset(force: bool) -> None:
    """Delete all activities and timer state."""
    if not force:
        confirm = click.confirm("Delete all activities?")
        if not confirm:
            click.echo("Cancelled.")
            return
    from habitt.core.config import get_tracker_file, get_timer_state_file

    get_tracker_file().unlink(missing_ok=True)
    get_timer_state_file().unlink(missing_ok=True)
    click.echo("All activities deleted.")


click_completion.init()

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tracker.tui import main_menu as tracker_tui

        tracker_tui()
    else:
        main()
