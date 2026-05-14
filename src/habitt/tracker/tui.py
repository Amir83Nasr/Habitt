"""Interactive terminal UI for tracker using Rich, including live timer."""

import sys
import time
import select
from datetime import timedelta
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.layout import Layout

from habitt.core.themes import THEME
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
        # Unix: need terminal in cbreak mode; we set it inside TimerSession
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
        """
        Start the live timer TUI.
        Returns Activity if stopped normally, None if cancelled.
        """
        # Save original terminal settings for Unix
        if sys.platform != "win32":
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        try:
            with Live(
                self._render_layout(),
                refresh_per_second=10,
                screen=True,
                transient=False,
            ) as live:
                while True:
                    live.update(self._render_layout())
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

        # Build an Activity from the session
        from habitt.tracker.models import Activity

        start_str = format_shamsi_datetime(self.start_time)
        end_str = format_shamsi_datetime(self.end_time)
        return Activity(title=self.title, start_time=start_str, end_time=end_str)

    def _render_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="timer", size=5),
            Layout(name="controls", size=5),
        )
        header = Panel(
            f"Timer: {self.title}",
            style=THEME["app_title"],
        )
        status = "PAUSED" if self.paused else "RUNNING"
        timer_text = f"[{THEME['clock']}]Elapsed: {self._format_elapsed()}   [{THEME['accent']}]{status}[/{THEME['accent']}]"
        controls_text = (
            f"[{THEME['info']}]p[/{THEME['info']}] Pause   "
            f"[{THEME['info']}]r[/{THEME['info']}] Resume   "
            f"[{THEME['info']}]s[/{THEME['info']}] Stop & Save   "
            f"[{THEME['dim']}]q[/{THEME['dim']}] Quit without saving"
        )
        layout["header"].update(header)
        layout["timer"].update(Panel(timer_text, border_style=THEME["panel_border"]))
        layout["controls"].update(Panel(controls_text, border_style=THEME["dim"]))
        return layout


def show_log(manager: TrackerManager) -> None:
    """Display today's activity log as a table."""
    console.clear()
    activities = manager.list_today()
    table = Table(
        title="Today's Activities",
        border_style=THEME["panel_border"],
    )
    table.add_column("ID", style=THEME["dim"], width=8)
    table.add_column("Title", style="bold")
    table.add_column("Start", style=THEME["info"])
    table.add_column("End", style=THEME["info"])
    table.add_column("Duration", style=THEME["accent"])

    if not activities:
        table.add_row("", "No activities logged today.", "", "", "")
    else:
        for a in activities:
            seconds = shamsi_diff_seconds(a.start_time, a.end_time)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m"
            table.add_row(
                a.id,
                a.title,
                a.start_time.split()[1],
                a.end_time.split()[1],
                duration_str,
            )

    console.print(table)


def add_manual_form(manager: TrackerManager) -> None:
    """Interactive form to manually add an activity."""
    console.clear()
    console.print(Panel.fit("Add Activity Manually", style=THEME["panel_border"]))
    title = Prompt.ask("Title")
    start = Prompt.ask("Start time (YYYY/MM/DD HH:MM)")
    end = Prompt.ask("End time (YYYY/MM/DD HH:MM)")
    try:
        manager.add_activity(title, start, end)
        console.print(f"[{THEME['success']}]Activity added.[/{THEME['success']}]")
    except ValueError as e:
        console.print(f"[{THEME['error']}]Invalid time format: {e}[/{THEME['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def show_stats(manager: TrackerManager) -> None:
    """Display daily statistics and a simple bar chart."""
    console.clear()
    stats = manager.last_days_stats(7)
    max_minutes = max((m for _, m in stats), default=1)

    table = Table(
        title="Daily Summary (last 7 days)",
        border_style=THEME["panel_border"],
    )
    table.add_column("Date", style=THEME["info"])
    table.add_column("Total", style="bold")
    table.add_column("Chart", style=THEME["accent"])

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
        console.clear()
        console.print(
            Panel.fit("TRACKER - Daily Activity Logger", style=THEME["app_title"])
        )
        console.print()
        console.print(f"[{THEME['info']}]1[/{THEME['info']}] Show today's log")
        console.print(f"[{THEME['info']}]2[/{THEME['info']}] Add activity manually")
        console.print(f"[{THEME['info']}]3[/{THEME['info']}] Start live timer")
        console.print(f"[{THEME['info']}]4[/{THEME['info']}] Statistics")
        console.print(f"[{THEME['dim']}]0[/{THEME['dim']}] Back")
        console.print()

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
                    f"[{THEME['success']}]Activity saved.[/{THEME['success']}]"
                )
            else:
                console.print(f"[{THEME['dim']}]Timer cancelled.[/{THEME['dim']}]")
            Prompt.ask("\nPress Enter to continue", default="")
        elif choice == "4":
            show_stats(manager)
            Prompt.ask("\nPress Enter to continue", default="")
        elif choice == "0":
            break
