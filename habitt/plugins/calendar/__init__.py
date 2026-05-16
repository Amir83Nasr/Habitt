"""Shamsi Calendar plugin for Habitt – displays monthly calendar."""

from __future__ import annotations

import jdatetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from habitt.core.plugin_base import PluginBase
from habitt.core.themes import get_active_theme

console = Console()

# Persian weekday names (0 = Shanbeh, 6 = Jomeh)
WEEKDAY_NAMES = [
    "Shanbeh",
    "Yekshanbeh",
    "Doshanbeh",
    "Seshanbeh",
    "Chaharshanbeh",
    "Panjshanbeh",
    "Jomeh",
]

# Persian month names (1..12)
MONTH_NAMES = [
    "",
    "Farvardin",
    "Ordibehesht",
    "Khordad",
    "Tir",
    "Mordad",
    "Shahrivar",
    "Mehr",
    "Aban",
    "Azar",
    "Dey",
    "Bahman",
    "Esfand",
]


class CalendarPlugin(PluginBase):
    name = "calendar"
    description = "Show Shamsi monthly calendar"

    def run_tui(self) -> None:
        """Main loop: display month and handle navigation."""
        theme = get_active_theme()
        today = jdatetime.date.today()
        year, month = today.year, today.month

        while True:
            console.clear()
            table = self._build_month_table(year, month, theme, today)
            console.print(table)
            console.print()
            console.print(
                f"[{theme['dim']}]n[/{theme['dim']}]ext  "
                f"[{theme['dim']}]p[/{theme['dim']}]rev  "
                f"[{theme['dim']}]t[/{theme['dim']}]oday  "
                f"[{theme['dim']}]q[/{theme['dim']}]uit"
            )
            cmd = Prompt.ask("Action").strip().lower()
            if cmd == "n":
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            elif cmd == "p":
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
            elif cmd == "t":
                today = jdatetime.date.today()
                year, month = today.year, today.month
            elif cmd == "q":
                break

    def _build_month_table(
        self, year: int, month: int, theme: dict, today: jdatetime.date
    ) -> Table:
        """Create a Rich table for the given Shamsi month."""
        title = f"{MONTH_NAMES[month]} {year}"
        table = Table(title=title, expand=True, border_style=theme["panel_border"])

        # Columns: 7 weekdays
        for i, name in enumerate(WEEKDAY_NAMES):
            if i == 6:  # Jomeh (Friday)
                table.add_column(name, style=theme["error"], justify="center")
            else:
                table.add_column(name, style=theme["dim"], justify="center")

        # First day of month (0 = Shanbeh)
        first_weekday = jdatetime.date(year, month, 1).weekday()
        # Number of days in month
        if month == 12:
            next_month = jdatetime.date(year + 1, 1, 1)
        else:
            next_month = jdatetime.date(year, month + 1, 1)
        days_in_month = (next_month - jdatetime.date(year, month, 1)).days

        # Build weeks
        current_day = 1
        # First row
        week: list[Text | str] = [""] * 7
        for i in range(first_weekday, 7):
            if current_day <= days_in_month:
                week[i] = self._render_day(current_day, year, month, today, theme)
                current_day += 1
        table.add_row(*week)

        # Remaining rows
        while current_day <= days_in_month:
            week = [""] * 7
            for i in range(7):
                if current_day <= days_in_month:
                    week[i] = self._render_day(current_day, year, month, today, theme)
                    current_day += 1
                else:
                    break
            table.add_row(*week)

        return table

    def _render_day(
        self, day: int, year: int, month: int, today: jdatetime.date, theme: dict
    ) -> Text:
        """Return a styled Text for the given day number."""
        date = jdatetime.date(year, month, day)
        is_today = date == today
        is_friday = date.weekday() == 6

        if is_today and is_friday:
            style = f"bold underline {theme['error']}"
        elif is_today:
            style = f"bold underline {theme['info']}"
        elif is_friday:
            style = theme["error"]
        else:
            style = ""

        return Text(str(day), style=style)
