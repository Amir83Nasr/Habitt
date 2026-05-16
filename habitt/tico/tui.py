"""Interactive terminal UI for tico using Rich – minimalist redesign."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from habitt.core.menu_utils import select_from_options
from habitt.core.themes import get_active_theme
from habitt.tico.models import TodoItem  # فقط یکبار
from habitt.tico.todo_manager import TodoManager  # TodoItem رو از این نیار

console = Console()


def _render_checkbox(done: bool, theme: dict[str, str]) -> Text:
    """Render a [x] or [ ] with theme colours."""

    if done:
        return Text("[x]", style=theme["checkbox_done"])
    return Text("[ ]", style=theme["checkbox_open"])


def _render_title(item: TodoItem, theme: dict[str, str]) -> Text:
    """Render task title with strikethrough if done."""

    style = theme["dim"] if item.done else "bold"
    text = Text(item.title, style=style)
    if item.done:
        text.stylize("strike")
    return text


def _tag_str(tag: str | None, theme: dict[str, str]) -> Text:
    """Render tag with colour."""

    if tag:
        return Text(f"#{tag}", style=theme["tag"])
    return Text("")


def _build_task_table(manager: TodoManager, tag: str | None = None) -> Table:
    """Build the Rich table for the current task list."""

    theme = get_active_theme()
    items = manager.list_all(tag=tag, include_done=True)

    table = Table(
        title="Tasks" if not tag else f"Tasks (tag: {tag})",
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
        table.add_row("", "", "No tasks yet.", "")
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
    """Convert space-separated numbers to ints, showing error on invalid input."""

    try:
        return [int(x) for x in raw.split()]
    except ValueError:
        console.print(
            f"[{theme['error']}]Invalid input. "
            f"Use numbers separated by spaces.[/{theme['error']}]"
        )
        return []


def main_menu() -> None:
    """Main TUI loop: tasks always on top, single-letter commands."""
    manager = TodoManager()
    current_tag: str | None = None

    while True:
        theme = get_active_theme()
        console.clear()

        # ---- Header ----
        console.rule("T I C O", style=theme["info"])
        console.print()

        # ---- Task table ----
        task_table = _build_task_table(manager, tag=current_tag)
        console.print(task_table)
        console.print()

        # ---- Command bar ----
        options = [
            ("a", "Add"),
            ("t", "Toggle"),
            ("r", "Remove"),
            ("f", "Filter"),
            ("s", "Show all"),
            ("q", "Back"),
        ]
        cmd = select_from_options(options, theme=theme, cancel_key="q")
        if cmd is None or cmd == "q":
            break

        if cmd == "a":
            # Add task without clearing the screen
            title = Prompt.ask("Title")
            tag: str | None
            tag = Prompt.ask("Tag (optional)", default="")
            tag = tag.strip() if tag.strip() else None
            manager.add(title, tag)
            current_tag = None
            console.print(
                f"[{theme['success']}]Task added: {title}[/{theme['success']}]"
            )
            Prompt.ask("Press Enter", default="")

        elif cmd == "t":
            # Toggle
            items = manager.list_all(tag=current_tag, include_done=True)
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
                else:
                    console.print(
                        f"[{theme['error']}]No valid rows selected.[/{theme['error']}]"
                    )
            Prompt.ask("Press Enter", default="")

        elif cmd == "r":
            # Remove
            items = manager.list_all(tag=current_tag, include_done=True)
            if not items:
                Prompt.ask("No tasks to remove. Press Enter", default="")
                continue
            raw = Prompt.ask("Row numbers to remove (space-separated)")
            numbers = _parse_numbers(raw, theme)
            if numbers:
                ids_to_remove = []
                for num in numbers:
                    if 1 <= num <= len(items):
                        ids_to_remove.append(items[num - 1].id)
                for task_id in ids_to_remove:
                    manager.remove(task_id)
                console.print(
                    f"[{theme['success']}]Removed {len(ids_to_remove)} task(s)."
                    f"[/{theme['success']}]"
                )
            Prompt.ask("Press Enter", default="")

        elif cmd == "f":
            tag_input = Prompt.ask("Tag to filter")
            current_tag = tag_input.strip() if tag_input.strip() else None

        elif cmd == "s":
            current_tag = None  # reset filter

        elif cmd == "q":
            break

        else:
            console.print(
                f"[{theme['error']}]Unknown command. Use A, T, R, F, S, Q."
                f"[/{theme['error']}]"
            )
            Prompt.ask("Press Enter", default="")
