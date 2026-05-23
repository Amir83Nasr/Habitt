"""Interactive terminal UI for tico using Rich – arrow-navigable redesign."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from habitt.core.jalali_helper import today_shamsi_str
from habitt.core.menu_utils import select_from_options
from habitt.core.themes import get_active_theme
from habitt.tico.models import TodoItem
from habitt.tico.todo_manager import TodoManager

console = Console()


def _render_checkbox(done: bool, theme: dict[str, str]) -> Text:
    if done:
        return Text("[x]", style=theme["checkbox_done"])
    return Text("[ ]", style=theme["checkbox_open"])


def _render_title(item: TodoItem, theme: dict[str, str]) -> Text:
    style = theme["dim"] if item.done else "bold"
    text = Text(item.title, style=style)
    if item.done:
        text.stylize("strike")
    return text


def _tag_str(tag: str | None, theme: dict[str, str]) -> Text:
    if tag:
        return Text(f"#{tag}", style=theme["tag"])
    return Text("")


def _build_task_table(
    manager: TodoManager,
    tag: str | None = None,
    date: str | None = None,
) -> Table:
    theme = get_active_theme()
    items = manager.list_all(tag=tag, include_done=True, date=date)
    title = f"Tasks for {date}" if date else "All Tasks"
    if tag:
        title += f" (tag: {tag})"

    table = Table(
        title=title,
        border_style=theme["panel_border"],
        show_lines=False,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("#", style=theme["dim"], width=4, justify="center")
    table.add_column("Status", style="bold", width=6, justify="center")
    table.add_column("Title", style="bold", ratio=3)
    table.add_column("Tag", style=theme["tag"], ratio=1, justify="center")

    if not items:
        table.add_row("", "", "No tasks.", "")
        return table

    for i, item in enumerate(items, start=1):
        table.add_row(
            str(i),
            _render_checkbox(item.done, theme),
            _render_title(item, theme),
            _tag_str(item.tag, theme),
        )
    return table


def _parse_numbers(raw: str, theme: dict[str, str]) -> list[int]:
    try:
        return [int(x) for x in raw.split()]
    except ValueError:
        console.print(
            f"[{theme['error']}]Invalid input. "
            f"Use numbers separated by spaces.[/{theme['error']}]"
        )
        return []


def main_menu() -> None:
    manager = TodoManager()
    current_tag: str | None = None
    current_date: str | None = today_shamsi_str()  # پیش‌فرض امروز

    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("T I C O", style=theme["info"])
        console.print()

        task_table = _build_task_table(manager, tag=current_tag, date=current_date)
        console.print(task_table)
        console.print()

        # منوی arrow شبیه tracker
        options = [
            ("l", "Log (change date)"),
            ("a", "Add task"),
            ("t", "Toggle done"),
            ("r", "Remove"),
            ("f", "Filter by tag"),
            ("s", "Show all (reset filters)"),
            ("e", "Export"),
            ("q", "Back"),
        ]
        choice = select_from_options(options, theme=theme)
        if choice is None or choice == "q":
            break

        elif choice == "l":
            # پرسیدن تاریخ
            date_input = Prompt.ask(
                f"Date (YYYY/MM/DD) [default: {today_shamsi_str()}]",
                default=today_shamsi_str(),
            )
            current_date = (
                date_input.strip() if date_input.strip() else today_shamsi_str()
            )
            # نمایش دوبارهٔ صفحه با تاریخ جدید
            console.clear()
            console.rule("T I C O", style=theme["info"])
            console.print()
            task_table = _build_task_table(manager, tag=current_tag, date=current_date)
            console.print(task_table)
            console.print()
            Prompt.ask("Press Enter to return to today's tasks", default="")
            current_date = today_shamsi_str()

        elif choice == "a":
            title = Prompt.ask("Title")
            tag: str | None
            tag = Prompt.ask("Tag (optional)", default="")
            tag = tag.strip() if tag.strip() else None
            date_input = Prompt.ask(
                f"Date (YYYY/MM/DD) [default: {today_shamsi_str()}]",
                default=today_shamsi_str(),
            )
            manager.add(title, tag, date=date_input.strip() or today_shamsi_str())
            current_tag = None
            # بعد از افزودن، بهتره به نمای امروز برگردیم؟ بله، طبق نیاز کاربر
            current_date = today_shamsi_str()
            console.print(
                f"[{theme['success']}]Task added: {title}[/{theme['success']}]"
            )
            Prompt.ask("Press Enter", default="")

        elif choice == "t":
            items = manager.list_all(
                tag=current_tag, include_done=True, date=current_date
            )
            if not items:
                Prompt.ask("No tasks to toggle. Press Enter", default="")
                continue
            raw = Prompt.ask("Row numbers to toggle (space-separated)")
            numbers = _parse_numbers(raw, theme)
            if numbers:
                toggled = 0
                for num in numbers:
                    if 1 <= num <= len(items):
                        updated = manager.toggle(items[num - 1].id)
                        if updated:
                            toggled += 1
                if toggled:
                    console.print(
                        f"[{theme['success']}]Toggled {toggled} task(s)."
                        f"[/{theme['success']}]"
                    )
            Prompt.ask("Press Enter", default="")

        elif choice == "r":
            items = manager.list_all(
                tag=current_tag, include_done=True, date=current_date
            )
            if not items:
                Prompt.ask("No tasks to remove. Press Enter", default="")
                continue
            raw = Prompt.ask("Row numbers to remove (space-separated)")
            numbers = _parse_numbers(raw, theme)
            if numbers:
                ids_to_remove = [
                    items[n - 1].id for n in numbers if 1 <= n <= len(items)
                ]
                for tid in ids_to_remove:
                    manager.remove(tid)
                console.print(
                    f"[{theme['success']}]Removed {len(ids_to_remove)} task(s)."
                    f"[/{theme['success']}]"
                )
            Prompt.ask("Press Enter", default="")

        elif choice == "f":
            tag_input = Prompt.ask("Tag to filter").strip()
            current_tag = tag_input if tag_input else None

        elif choice == "s":
            current_tag = None
            current_date = today_shamsi_str()

        elif choice == "e":
            export_choice = Prompt.ask(
                "Export: (1) Current view, (2) Specific date",
                choices=["1", "2"],
                default="1",
            )
            fmt = Prompt.ask(
                "Format (json/csv/txt)",
                choices=["json", "csv", "txt"],
                default="txt",
            )
            desktop = Path.home() / "Desktop"
            try:
                if export_choice == "1":
                    if current_date:
                        path = manager.export_date_data(desktop, current_date, fmt)
                    else:
                        path = manager.export_data(desktop, fmt)
                else:
                    date = Prompt.ask(
                        f"Date (YYYY/MM/DD) [default: {today_shamsi_str()}]",
                        default=today_shamsi_str(),
                    )
                    path = manager.export_date_data(desktop, date, fmt)
                console.print(
                    f"[{theme['success']}]Exported to {path}[/{theme['success']}]"
                )
            except Exception as e:
                console.print(
                    f"[{theme['error']}]Export failed: {e}[/{theme['error']}]"
                )
            Prompt.ask("Press Enter", default="")
