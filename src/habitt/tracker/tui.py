"""Interactive terminal UI for tracker using Rich, including live timer."""

import sys
import time
import select
from datetime import timedelta
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.live import Live
from rich.layout import Layout

from habitt.core.themes import get_active_theme
from habitt.core.jalali_helper import (
    now_tehran,
    now_shamsi_str,
    format_shamsi_datetime,
    shamsi_diff_seconds,
)
from habitt.tracker.tracker_manager import TrackerManager

console = Console()


def _get_key_nonblocking() -> Optional[str]:
    """Return a single character if a key was pressed, else None. Cross-platform."""
    if sys.platform == "win32":
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8", errors="replace")
        return None
    else:
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None


class TimerSession:
    """Handles the live timer with pause, resume, stop."""

    def __init__(self, title: str) -> None:
        self.title = title
        self.start_time = now_tehran()
        self.paused = False
        self.pause_start = None
        self.total_paused = timedelta(0)
        self.stopped = False
        self.end_time = None
        self.cancelled = False

    def elapsed(self) -> timedelta:
        if self.stopped and self.end_time:
            return self.end_time - self.start_time - self.total_paused
        if self.paused and self.pause_start:
            return self.pause_start - self.start_time - self.total_paused
        return now_tehran() - self.start_time - self.total_paused

    def _format_elapsed(self) -> str:
        seconds = int(self.elapsed().total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def run(self) -> Optional["Activity"]:
        """Start the live timer TUI. Returns Activity if stopped normally, else None."""
        theme = get_active_theme()
        if sys.platform != "win32":
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        try:
            with Live(
                self._render_layout(theme),
                refresh_per_second=10,
                screen=True,
                transient=False,
            ) as live:
                while True:
                    live.update(self._render_layout(theme))
                    key = _get_key_nonblocking()
                    if key:
                        if key.lower() == "p" and not self.paused:
                            self.paused = True
                            self.pause_start = now_tehran()
                        elif key.lower() == "r" and self.paused:
                            if self.pause_start:
                                self.total_paused += now_tehran() - self.pause_start
                                self.pause_start = None
                            self.paused = False
                        elif key.lower() == "s":
                            self.stopped = True
                            if self.paused and self.pause_start:
                                self.total_paused += now_tehran() - self.pause_start
                                self.pause_start = None
                                self.paused = False
                            self.end_time = now_tehran()
                            break
                        elif key.lower() == "q":
                            self.cancelled = True
                            break
                    time.sleep(0.1)
        finally:
            if sys.platform != "win32":
                import termios

                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if self.cancelled:
            return None

        from habitt.tracker.models import Activity

        start_str = format_shamsi_datetime(self.start_time)
        end_str = format_shamsi_datetime(self.end_time)
        return Activity(title=self.title, start_time=start_str, end_time=end_str)

    def _render_layout(self, theme: dict) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="timer", size=5),
            Layout(name="controls", size=5),
        )
        header = Panel(
            f"Timer: {self.title}",
            style=theme["app_title"],
        )
        status = "PAUSED" if self.paused else "RUNNING"
        timer_text = (
            f"[{theme['clock']}]Elapsed: {self._format_elapsed()}   "
            f"[{theme['accent']}]{status}[/{theme['accent']}]"
        )
        controls_text = (
            f"[{theme['info']}]p[/{theme['info']}] Pause   "
            f"[{theme['info']}]r[/{theme['info']}] Resume   "
            f"[{theme['info']}]s[/{theme['info']}] Stop & Save   "
            f"[{theme['dim']}]q[/{theme['dim']}] Quit without saving"
        )
        layout["header"].update(header)
        layout["timer"].update(Panel(timer_text, border_style=theme["panel_border"]))
        layout["controls"].update(Panel(controls_text, border_style=theme["dim"]))
        return layout


def show_log(manager: TrackerManager) -> None:
    """Display today's activity log as a table with row numbers."""
    theme = get_active_theme()
    console.clear()
    activities = manager.list_today()
    table = Table(
        title="Today's Activities",
        border_style=theme["panel_border"],
    )
    table.add_column("#", style=theme["dim"], width=4, justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Start", style=theme["info"])
    table.add_column("End", style=theme["info"])
    table.add_column("Duration", style=theme["accent"])

    if not activities:
        table.add_row("", "No activities logged today.", "", "", "")
    else:
        for i, a in enumerate(activities, start=1):
            seconds = shamsi_diff_seconds(a.start_time, a.end_time)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m"
            table.add_row(
                str(i),
                a.title,
                a.start_time.split()[1],
                a.end_time.split()[1],
                duration_str,
            )

    console.print(table)


def add_manual_form(manager: TrackerManager) -> None:
    """Interactive form to manually add an activity."""
    theme = get_active_theme()
    console.clear()
    console.print(Panel.fit("Add Activity Manually", style=theme["panel_border"]))
    title = Prompt.ask("Title")
    start = Prompt.ask("Start time (YYYY/MM/DD HH:MM)")
    end = Prompt.ask("End time (YYYY/MM/DD HH:MM)")
    try:
        manager.add_activity(title, start, end)
        console.print(f"[{theme['success']}]Activity added.[/{theme['success']}]")
    except ValueError as e:
        console.print(f"[{theme['error']}]Invalid time format: {e}[/{theme['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def show_stats(manager: TrackerManager) -> None:
    """Display daily statistics and a simple bar chart."""
    theme = get_active_theme()
    console.clear()
    stats = manager.last_days_stats(7)
    max_minutes = max((m for _, m in stats), default=1)

    table = Table(
        title="Daily Summary (last 7 days)",
        border_style=theme["panel_border"],
    )
    table.add_column("Date", style=theme["info"])
    table.add_column("Total", style="bold")
    table.add_column("Chart", style=theme["accent"])

    bar_width = 20
    for date_str, minutes in stats:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        total_str = f"{hours}h {mins}m"
        bar_length = int((minutes / max_minutes) * bar_width) if max_minutes > 0 else 0
        bar = "█" * bar_length
        table.add_row(date_str, total_str, bar)

    console.print(table)


def main_menu() -> None:
    """Entry point for tracker TUI."""
    manager = TrackerManager()

    while True:
        theme = get_active_theme()
        console.clear()
        console.print(
            Panel.fit("TRACKER - Daily Activity Logger", style=theme["app_title"])
        )
        console.print()
        console.print(
            f"[{theme['info']}]1[/] Show log   "
            f"[{theme['info']}]2[/] Add manual   "
            f"[{theme['info']}]3[/] Live timer   "
            f"[{theme['info']}]4[/] Statistics   "
            f"[{theme['info']}]5[/] Export   "
            f"[{theme['dim']}]0[/] Back"
        )
        choice = Prompt.ask("Your choice", choices=["1", "2", "3", "4", "5", "0"])

        choice = Prompt.ask("Your choice", choices=["1", "2", "3", "4", "0"])

        if choice == "1":
            show_log(manager)
            Prompt.ask("\nPress Enter to continue", default="")
        elif choice == "2":
            add_manual_form(manager)
        elif choice == "3":
            console.clear()
            title = Prompt.ask("Activity title for timer")
            session = TimerSession(title)
            activity = session.run()
            if activity:
                manager.add_activity(
                    activity.title,
                    activity.start_time,
                    activity.end_time,
                )
                console.print(
                    f"[{theme['success']}]Activity saved.[/{theme['success']}]"
                )
            else:
                console.print(f"[{theme['dim']}]Timer cancelled.[/{theme['dim']}]")
            Prompt.ask("\nPress Enter to continue", default="")

        elif choice == "4":
            show_stats(manager)
            Prompt.ask("\nPress Enter to continue", default="")

        elif choice == "5":
            fmt = Prompt.ask("Format (json/csv/txt)", choices=["json", "csv", "txt"])
            desktop = Path.home() / "Desktop"
            try:
                path = manager.export_data(desktop, fmt)
                console.print(
                    f"[{theme['success']}]Exported to {path}[/{theme['success']}]"
                )
            except Exception as e:
                console.print(
                    f"[{theme['error']}]Export failed: {e}[/{theme['error']}]"
                )
            Prompt.ask("\nPress Enter to continue", default="")

        elif choice == "0":
            break
