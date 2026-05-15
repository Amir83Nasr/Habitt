"""Interactive terminal UI for tracker using Rich – clean redesign."""

import select
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from habitt.core.jalali_helper import (
    format_shamsi_datetime,
    now_tehran,
    shamsi_diff_seconds,
    today_shamsi_str,
)
from habitt.core.themes import get_active_theme
from habitt.core.validators import prompt_shamsi_date, prompt_time
from habitt.tracker.tracker_manager import TrackerManager

console = Console()


def _get_key_nonblocking() -> Optional[str]:
    if sys.platform == "win32":
        import msvcrt

        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8", errors="replace")
        return None
    else:
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None


def _zero_pad_time(text: str) -> str:
    """Convert '7:9' -> '07:09', '12:5' -> '12:05', etc."""
    if ":" not in text:
        raise ValueError("Time must contain ':'")
    h, m = text.split(":", 1)
    h = h.zfill(2)
    m = m.zfill(2)
    return f"{h}:{m}"


class TimerSession:
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


def _parse_numbers(raw: str, theme: dict) -> List[int]:
    try:
        return [int(x) for x in raw.split()]
    except ValueError:
        console.print(
            f"[{theme['error']}]Invalid input. Use numbers separated by spaces.[/{theme['error']}]"
        )
        return []


def _build_log_table(
    manager: TrackerManager, date_filter: Optional[str] = None
) -> Table:
    """Build a table of activities filtered by date (all if None)."""
    theme = get_active_theme()
    if date_filter:
        activities = [a for a in manager.activities if a.date == date_filter]
        title = f"Activities on {date_filter}"
    else:
        activities = manager.list_all()
        title = "All Activities"

    table = Table(
        title=title,
        border_style=theme["panel_border"],
        show_lines=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("#", style=theme["dim"], width=4, justify="center")
    table.add_column("Title", style="bold", ratio=2)
    table.add_column("Date", style=theme["info"])
    table.add_column("Start", style=theme["info"])
    table.add_column("End", style=theme["info"])
    table.add_column("Duration", style=theme["accent"])

    if not activities:
        table.add_row("", "No activities found.", "", "", "", "")
        return table

    for i, a in enumerate(activities, start=1):
        seconds = shamsi_diff_seconds(a.start_time, a.end_time)
        hours, remainder = divmod(int(seconds), 3600)
        minutes, _ = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m"
        table.add_row(
            str(i),
            a.title,
            a.date,
            a.start_time.split()[1],
            a.end_time.split()[1],
            duration_str,
        )
    return table


def _build_stats_table(manager: TrackerManager) -> Table:
    theme = get_active_theme()
    stats = manager.last_days_stats(7)
    max_minutes = max((m for _, m in stats), default=1)

    table = Table(
        title="Daily Summary (last 7 days)",
        border_style=theme["panel_border"],
        show_lines=False,
        padding=(0, 1),
        expand=True,
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
    return table


def main_menu() -> None:
    """Entry point for tracker TUI with single-letter commands."""
    manager = TrackerManager()

    while True:
        theme = get_active_theme()
        console.clear()

        # Header with rule
        console.rule("T R A C K E R", style=theme["info"])
        console.print()

        # Today's log (default view)
        today_table = _build_log_table(manager, date_filter=today_shamsi_str())
        console.print(today_table)
        console.print()

        # Menu
        console.print(
            f"[{theme['info']}]L[/]og  "
            f"[{theme['info']}]A[/]dd  "
            f"[{theme['info']}]T[/]imer  "
            f"[{theme['info']}]R[/]emove  "
            f"[{theme['info']}]S[/]tats  "
            f"[{theme['info']}]E[/]xport  "
            f"[{theme['dim']}]Q[/]uit"
        )
        console.print()

        prompt = Text("Action", style=theme["info"])
        prompt.append(" > ", style="white")
        cmd = Prompt.ask(prompt).strip().lower()

        if cmd == "l":
            # Log: view specific date or all
            date_input = Prompt.ask("Date (YYYY/MM/DD) or empty for all", default="")
            if date_input.strip():
                log_table = _build_log_table(manager, date_filter=date_input.strip())
            else:
                log_table = _build_log_table(manager)
            console.print(log_table)
            Prompt.ask("Press Enter to return", default="")

        elif cmd == "a":
            title = Prompt.ask("Title")
            # Date with default today
            date_str = prompt_shamsi_date(
                "Date (YYYY/MM/DD) [default today]", default_today=True
            )
            # Start time (required)
            start_hm = prompt_time("Start time (HH:MM)")
            # End time default now
            default_end_hm = now_tehran().strftime("%H:%M")
            end_hm = prompt_time(
                "End time (HH:MM) [default: {default_end_hm}]", default=default_end_hm
            )
            start_full = f"{date_str} {start_hm}:00"
            end_full = f"{date_str} {end_hm}:00"
            try:
                manager.add_activity(title, start_full, end_full)
                console.print(
                    f"[{theme['success']}]Activity added.[/{theme['success']}]"
                )
            except ValueError as e:
                console.print(f"[{theme['error']}]Error: {e}[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")

        elif cmd == "t":
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
            Prompt.ask("Press Enter", default="")

        elif cmd == "r":
            today_items = manager.list_today()
            if not today_items:
                Prompt.ask("No activities to remove today. Press Enter", default="")
                continue
            raw = Prompt.ask("Row numbers to remove (space-separated)")
            numbers = _parse_numbers(raw, theme)
            if numbers:
                ids_to_remove = []
                for num in numbers:
                    if 1 <= num <= len(today_items):
                        ids_to_remove.append(today_items[num - 1].id)
                for aid in ids_to_remove:
                    manager.remove_activity(aid)
                console.print(
                    f"[{theme['success']}]Removed {len(ids_to_remove)} activity(s).[/{theme['success']}]"
                )
            Prompt.ask("Press Enter", default="")

        elif cmd == "s":
            console.clear()
            console.rule("Statistics", style=theme["info"])
            console.print()
            stats_table = _build_stats_table(manager)
            console.print(stats_table)
            Prompt.ask("Press Enter to return", default="")

        elif cmd == "e":
            # Export submenu with default dates
            today = today_shamsi_str()
            export_choice = Prompt.ask(
                "Export: (1) All, (2) Specific date, (3) Date range",
                choices=["1", "2", "3"],
                default="1",
            )
            fmt = Prompt.ask(
                "Format (json/csv/txt)", choices=["json", "csv", "txt"], default="txt"
            )
            desktop = Path.home() / "Desktop"
            try:
                if export_choice == "1":
                    path = manager.export_data(desktop, fmt)
                elif export_choice == "2":
                    date = Prompt.ask(
                        f"Date (YYYY/MM/DD) [default: {today}]", default=today
                    )
                    path = manager.export_date_data(desktop, date, fmt)
                else:  # range
                    start = Prompt.ask(
                        f"Start date (YYYY/MM/DD) [default: {today}]", default=today
                    )
                    end = Prompt.ask(
                        f"End date (YYYY/MM/DD) [default: {today}]", default=today
                    )
                    path = manager.export_date_range(desktop, start, end, fmt)
                console.print(
                    f"[{theme['success']}]Exported to {path}[/{theme['success']}]"
                )
            except Exception as e:
                console.print(
                    f"[{theme['error']}]Export failed: {e}[/{theme['error']}]"
                )
            Prompt.ask("Press Enter", default="")

        elif cmd == "q":
            break

        else:
            console.print(
                f"[{theme['error']}]Unknown command. Use L, A, T, R, S, E, Q.[/{theme['error']}]"
            )
            Prompt.ask("Press Enter", default="")
