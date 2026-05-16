"""Interactive terminal UI for tracker using Rich – with configurable Pomodoro."""

from __future__ import annotations

import json
import select
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, cast

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from habitt.core.config import get_data_dir
from habitt.core.jalali_helper import (
    format_shamsi_datetime,
    now_tehran,
    shamsi_diff_seconds,
    today_shamsi_str,
)
from habitt.core.menu_utils import select_from_options
from habitt.core.themes import get_active_theme
from habitt.core.validators import prompt_time
from habitt.tracker.models import Activity
from habitt.tracker.tracker_manager import TrackerManager

console = Console()

POMODORO_CONFIG_FILE = get_data_dir() / "pomodoro_config.json"


def load_pomodoro_config() -> dict[str, Any]:
    default: dict[str, Any] = {
        "work": 25,
        "short_break": 5,
        "long_break": 15,
        "cycles": 4,
    }
    if POMODORO_CONFIG_FILE.exists():
        try:
            with open(POMODORO_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return default


def save_pomodoro_config(config: dict[str, Any]) -> None:
    POMODORO_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POMODORO_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def _get_key_nonblocking() -> str | None:
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
            diff = self.end_time - self.start_time - self.total_paused
            return cast(timedelta, diff)
        if self.paused and self.pause_start:
            diff = self.pause_start - self.start_time - self.total_paused
            return cast(timedelta, diff)
        diff = now_tehran() - self.start_time - self.total_paused
        return cast(timedelta, diff)

    def _format_elapsed(self) -> str:
        seconds = int(self.elapsed().total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def run(self) -> Activity | None:
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

    def _render_layout(self, theme: dict[str, str]) -> Layout:
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


class PomodoroSession:
    def __init__(self, config: dict[str, Any]) -> None:
        self.work_min = config["work"]
        self.short_break_min = config["short_break"]
        self.long_break_min = config["long_break"]
        self.cycles_before_long = config["cycles"]
        self.cycle = 0
        self.cancelled = False

    def run(self, manager: TrackerManager) -> None:
        theme = get_active_theme()
        while not self.cancelled:
            self.cycle += 1
            if not self._run_phase("Work", self.work_min, manager, theme):
                break
            if self.cycle % self.cycles_before_long == 0:
                if not self._run_phase(
                    "Long Break", self.long_break_min, manager, theme
                ):
                    break
            else:
                if not self._run_phase("Break", self.short_break_min, manager, theme):
                    break

    def _run_phase(
        self, label: str, minutes: int, manager: TrackerManager, theme: dict[str, str]
    ) -> bool:
        total_seconds = minutes * 60
        start_time = now_tehran()
        paused = False
        pause_start = None
        total_paused = timedelta(0)

        if sys.platform != "win32":
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)

        try:
            progress = Progress(
                TextColumn(f"[{theme['info']}]{label}[/{theme['info']}] "),
                BarColumn(bar_width=40, style=theme["accent"]),
                TaskProgressColumn(),
                TextColumn("remaining"),
            )
            task = progress.add_task("", total=total_seconds)

            with Live(progress, refresh_per_second=10, screen=True) as live:
                while True:
                    elapsed = (now_tehran() - start_time) - total_paused
                    remaining = total_seconds - elapsed.total_seconds()
                    if remaining <= 0:
                        break
                    progress.update(task, completed=elapsed.total_seconds())
                    live.update(progress)

                    key = _get_key_nonblocking()
                    if key:
                        if key.lower() == "p" and not paused:
                            paused = True
                            pause_start = now_tehran()
                        elif key.lower() == "r" and paused:
                            if pause_start:
                                total_paused += now_tehran() - pause_start
                                pause_start = None
                            paused = False
                        elif key.lower() == "q":
                            self.cancelled = True
                            return False
                    time.sleep(0.1)
        finally:
            if sys.platform != "win32":
                import termios

                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if label == "Work":
            end_time = now_tehran()
            title = f"Pomodoro #{self.cycle}"
            start_str = format_shamsi_datetime(start_time)
            end_str = format_shamsi_datetime(end_time)
            manager.add_activity(title, start_str, end_str)

        sys.stdout.write("\a")
        sys.stdout.flush()
        return True


def _parse_numbers(raw: str, theme: dict[str, str]) -> list[int]:
    try:
        return [int(x) for x in raw.split()]
    except ValueError:
        console.print(
            f"[{theme['error']}]Invalid input. Use numbers separated by spaces."
            f"[/{theme['error']}]"
        )
        return []


def show_log(manager: TrackerManager) -> None:
    """
    Display all activities grouped by date.

    If no activities exist, show a message.
    """
    theme = get_active_theme()
    activities = manager.list_all()
    if not activities:
        console.print("No activities logged.", style=theme["dim"])
        return

    # Group by date
    dates: dict[str, list[Activity]] = {}
    for a in activities:
        dates.setdefault(a.date, []).append(a)

    for date_str, _day_activities in dates.items():
        table = _build_log_table(manager, date_filter=date_str)
        console.print(table)
        console.print()


def _build_log_table(manager: TrackerManager, date_filter: str | None = None) -> Table:
    """Build a table for a single date or all activities (if date_filter is None)."""
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
    manager = TrackerManager()

    while True:
        theme = get_active_theme()
        console.clear()

        console.rule("T R A C K E R", style=theme["info"])
        console.print()

        today_table = _build_log_table(manager, date_filter=today_shamsi_str())
        console.print(today_table)
        console.print()

        options = [
            ("l", "Log"),
            ("a", "Add manual"),
            ("t", "Timer"),
            ("p", "Pomodoro"),
            ("r", "Remove"),
            ("s", "Stats"),
            ("e", "Export"),
            ("q", "Back"),
        ]
        cmd = select_from_options(options, theme=theme, cancel_key="q")
        if cmd is None or cmd == "q":
            break

        elif cmd == "l":
            date_input = Prompt.ask("Date (YYYY/MM/DD) or empty for all", default="")
            if date_input.strip():
                log_table = _build_log_table(manager, date_filter=date_input.strip())
                console.print(log_table)
            else:
                show_log(manager)
            Prompt.ask("Press Enter to return", default="")

        elif cmd == "a":
            title = Prompt.ask("Title")
            today = today_shamsi_str()
            default_start_hm = now_tehran().strftime("%H:%M")
            start_hm = prompt_time(
                f"Start time (HH:MM) [default: {default_start_hm}]",
                default=default_start_hm,
            )
            default_end_hm = now_tehran().strftime("%H:%M")
            end_hm = prompt_time(
                f"End time (HH:MM) [default: {default_end_hm}]",
                default=default_end_hm,
            )
            start_full = f"{today} {start_hm}:00"
            end_full = f"{today} {end_hm}:00"
            try:
                manager.add_activity(title, start_full, end_full)
                console.print(
                    f"[{theme['success']}]Activity added.[/{theme['success']}]"
                )
            except ValueError as e:
                console.print(f"[{theme['error']}]Invalid time: {e}[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")

        elif cmd == "t":
            title = Prompt.ask("Activity title for timer")
            timer_session = TimerSession(title)
            activity = timer_session.run()
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

        elif cmd == "p":
            config = load_pomodoro_config()
            while True:
                console.clear()
                console.rule("Pomodoro Settings", style=theme["info"])
                console.print(f"1. Work duration: {config['work']} min")
                console.print(f"2. Short break: {config['short_break']} min")
                console.print(f"3. Long break: {config['long_break']} min")
                console.print(f"4. Cycles before long break: {config['cycles']}")
                console.print("5. Start")
                console.print("0. Back")
                choice = Prompt.ask("Choose", choices=["0", "1", "2", "3", "4", "5"])
                if choice == "0":
                    break
                elif choice == "1":
                    new_val = Prompt.ask("Work minutes", default=str(config["work"]))
                    if new_val.isdigit() and int(new_val) > 0:
                        config["work"] = int(new_val)
                elif choice == "2":
                    new_val = Prompt.ask(
                        "Short break minutes", default=str(config["short_break"])
                    )
                    if new_val.isdigit() and int(new_val) >= 0:
                        config["short_break"] = int(new_val)
                elif choice == "3":
                    new_val = Prompt.ask(
                        "Long break minutes", default=str(config["long_break"])
                    )
                    if new_val.isdigit() and int(new_val) >= 0:
                        config["long_break"] = int(new_val)
                elif choice == "4":
                    new_val = Prompt.ask("Cycles", default=str(config["cycles"]))
                    if new_val.isdigit() and int(new_val) > 0:
                        config["cycles"] = int(new_val)
                elif choice == "5":
                    save_pomodoro_config(config)
                    pom_session = PomodoroSession(config)
                    pom_session.run(manager)
                    break

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
                    f"[{theme['success']}]Removed {len(ids_to_remove)} activity(s)."
                    f"[/{theme['success']}]"
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


if __name__ == "__main__":
    main_menu()
