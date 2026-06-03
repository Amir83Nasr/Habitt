"""Click-based CLI for quick tracker commands (start/pause/resume/stop/status)."""

from __future__ import annotations

import json
import select
import sys
import termios
import tty
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import cast

import click
from rich.console import Console
from rich.live import Live
from rich.table import Table

from habitt.core.config import get_timer_state_file
from habitt.core.jalali_helper import now_shamsi_str, now_tehran, parse_shamsi_datetime
from habitt.tracker.tracker_manager import TrackerManager

console = Console()


@dataclass
class TimerState:
    title: str
    start_time: str
    paused: bool = False
    pause_start: str | None = None
    total_paused_seconds: float = 0.0


def _load_timer_state() -> TimerState | None:
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


def _elapsed_seconds(state: TimerState) -> float:
    start_dt = parse_shamsi_datetime(state.start_time)
    if state.paused and state.pause_start is not None:
        pause_dt = parse_shamsi_datetime(state.pause_start)
        return cast(
            float, (pause_dt - start_dt).total_seconds() - state.total_paused_seconds
        )
    return cast(
        float, (now_tehran() - start_dt).total_seconds() - state.total_paused_seconds
    )


def _get_key_blocking() -> str:
    """Read a single keypress without Enter, blocking until key is pressed."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # اگر ESC باشه، ممکنه دنباله داشته باشه (کلیدهای جهت‌نما)
        if ch == "\x1b":
            # نخوان بقیه رو، فقط ESC رو برگردون
            pass
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _get_key_nonblocking() -> str | None:
    """Check if a key was pressed, return it or None."""
    if sys.platform == "win32":
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8", errors="replace")
        return None
    else:
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
    return None


def _live_status(state: TimerState) -> None:
    """Display live timer status with working keyboard controls."""

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    stopped = False

    try:

        def build_table() -> Table:
            elapsed_seconds = _elapsed_seconds(state)
            elapsed = timedelta(seconds=int(elapsed_seconds))
            status_str = "PAUSED" if state.paused else "RUNNING"
            status_color = "yellow" if state.paused else "green"

            table = Table(
                title="Timer Status",
                show_header=False,
                box=None,
                title_justify="left",
                padding=(0, 1),
            )

            table.add_column(style="bold dim", width=10)
            table.add_column()
            table.add_row("Title", f"[bold]{state.title or 'Untitled'}[/bold]")
            table.add_row("Started", state.start_time)
            table.add_row("Status", f"[{status_color}]{status_str}[/{status_color}]")
            table.add_row("Elapsed", str(elapsed))
            table.add_section()
            table.add_row(
                "Controls", "[blue](p) Pause  (r) Resume  (s) Stop & Save  (h) Hide"
            )
            return table

        with Live(build_table(), refresh_per_second=4, screen=False) as live:
            while True:
                live.update(build_table())

                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == "h":
                        break
                    elif key.lower() == "p":
                        _pause_timer()
                        loaded = _load_timer_state()
                        if loaded:
                            state = loaded
                    elif key.lower() == "r":
                        _resume_timer()
                        loaded = _load_timer_state()
                        if loaded:
                            state = loaded
                    elif key.lower() == "s":
                        stopped = True
                        break
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass

    # بعد از خروج از live view، اگه s زده شده بود، تایتل بپرس
    if stopped:
        _stop_timer_cli()


def _pause_timer() -> None:
    state = _load_timer_state()
    if not state or state.paused:
        return
    state.paused = True
    state.pause_start = now_shamsi_str()
    _save_timer_state(state)


def _resume_timer() -> None:
    state = _load_timer_state()
    if not state or not state.paused or state.pause_start is None:
        return
    pause_dt = parse_shamsi_datetime(state.pause_start)
    now_dt = now_tehran()
    state.total_paused_seconds += (now_dt - pause_dt).total_seconds()
    state.paused = False
    state.pause_start = None
    _save_timer_state(state)


def _stop_timer_cli() -> None:
    """Stop the timer, ask for title, and save activity."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return

    if state.paused and state.pause_start is not None:
        pause_dt = parse_shamsi_datetime(state.pause_start)
        now_dt = now_tehran()
        state.total_paused_seconds += (now_dt - pause_dt).total_seconds()

    end_time = now_shamsi_str()

    # برگشتیم به حالت عادی ترمینال – input درست کار می‌کنه
    title = input("Activity title: ").strip()
    if not title:
        title = state.title or "Untitled"

    manager = TrackerManager()
    manager.add_activity(title, state.start_time, end_time)
    _clear_timer_state()
    click.echo(f"Activity '{title}' saved.")


@click.group()
def main() -> None:
    """Tracker - Daily activity logger. Run without subcommand for TUI."""
    pass


@main.command()
@click.argument("title", required=False)
def start(title: str | None = None) -> None:
    """Start a new timer and show live status."""
    if _load_timer_state():
        click.echo("A timer is already running. Stop it first.")
        return

    state = TimerState(
        title=title or "",
        start_time=now_shamsi_str(),
        paused=False,
        pause_start=None,
        total_paused_seconds=0.0,
    )
    _save_timer_state(state)
    click.echo(f"Timer started: {title or 'Untitled'}")
    click.echo("")
    _live_status(state)


@main.command()
def status() -> None:
    """Show live timer status (re-attach to running timer)."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return
    try:
        _live_status(state)
    except KeyboardInterrupt:
        click.echo("\nTimer running in background.")


@main.command()
def pause() -> None:
    """Pause the running timer."""
    _pause_timer()
    state = _load_timer_state()
    if state:
        click.echo(f"Timer paused. Elapsed: {_elapsed_seconds(state):.0f}s")


@main.command()
def resume() -> None:
    """Resume a paused timer."""
    _resume_timer()
    state = _load_timer_state()
    if state:
        click.echo(f"Timer resumed. Elapsed: {_elapsed_seconds(state):.0f}s")


@main.command()
def stop() -> None:
    """Stop the timer and save the activity."""
    state = _load_timer_state()
    if not state:
        click.echo("No timer is running.")
        return
    _stop_timer_cli()


@main.command()
def log() -> None:
    """Show today's activities."""
    manager = TrackerManager()
    from habitt.core.jalali_helper import today_shamsi_str
    from habitt.tracker.tui import _build_log_table

    table = _build_log_table(manager, date_filter=today_shamsi_str())
    console.print(table)


@main.command()
def stats() -> None:
    """Show statistics for the last 7 days."""
    manager = TrackerManager()
    from habitt.tracker.tui import _build_stats_table

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


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tracker.tui import main_menu as tracker_tui

        tracker_tui()
    else:
        main()
