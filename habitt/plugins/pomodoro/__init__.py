"""Pomodoro Timer plugin for Habitt."""

from __future__ import annotations

import json
import select
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

from rich.live import Live
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from habitt.core.config import get_data_dir
from habitt.core.jalali_helper import format_shamsi_datetime, now_tehran
from habitt.core.plugin_base import PluginBase
from habitt.core.themes import get_active_theme

POMODORO_CONFIG_FILE = get_data_dir() / "pomodoro_config.json"

DEFAULT_POMODORO_CONFIG = {
    "work": 25,
    "short_break": 5,
    "long_break": 15,
    "cycles": 4,
}


def load_config() -> dict[str, Any]:
    if POMODORO_CONFIG_FILE.exists():
        try:
            with open(POMODORO_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for key, val in DEFAULT_POMODORO_CONFIG.items():
                if key not in data:
                    data[key] = val
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_POMODORO_CONFIG)


def save_config(config: dict[str, Any]) -> None:
    POMODORO_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POMODORO_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


class PomodoroPlugin(PluginBase):
    name = "pomodoro"
    description = "Pomodoro timer (work/break cycles)"

    def run_tui(self) -> None:
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()
        theme = get_active_theme()
        config = load_config()

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
                save_config(config)
                self._start_cycles(config)
                break

    def _start_cycles(self, config: dict[str, Any]) -> None:
        from habitt.tracker.tracker_manager import TrackerManager

        manager = TrackerManager()
        cycle = 0
        cancelled = False
        theme = get_active_theme()

        def run_phase(label: str, minutes: int) -> bool:
            nonlocal cancelled
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

                        key = self._get_key_nonblocking()
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
                                cancelled = True
                                return False
                        time.sleep(0.1)
            finally:
                if sys.platform != "win32":
                    import termios

                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if label == "Work":
                end_time = now_tehran()
                title = f"Pomodoro #{cycle}"
                start_str = format_shamsi_datetime(start_time)
                end_str = format_shamsi_datetime(end_time)
                manager.add_activity(title, start_str, end_str)

            sys.stdout.write("\a")
            sys.stdout.flush()
            return True

        while not cancelled:
            cycle += 1
            if not run_phase("Work", config["work"]):
                break
            if cycle % config["cycles"] == 0:
                if not run_phase("Long Break", config["long_break"]):
                    break
            else:
                if not run_phase("Break", config["short_break"]):
                    break

    @staticmethod
    def _get_key_nonblocking():
        if sys.platform == "win32":
            import msvcrt

            if msvcrt.kbhit():
                return msvcrt.getch().decode("utf-8", errors="replace")
            return None
        else:
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
        return None
