"""Interactive terminal UI for tico using Rich."""

from typing import Optional, List

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.text import Text

from habitt.core.themes import get_active_theme
from habitt.tico.todo_manager import TodoManager, TodoItem

console = Console()


def _render_checkbox(done: bool, theme: dict) -> Text:
    """Return a styled checkbox: [x] for done, [ ] for open."""
    if done:
        return Text("[x]", style=theme["checkbox_done"])
    return Text("[ ]", style=theme["checkbox_open"])


def _render_title(item: TodoItem, theme: dict) -> Text:
    """Render task title: strikethrough and dim if done, bold if not."""
    style = theme["dim"] if item.done else "bold"
    text = Text(item.title, style=style)
    if item.done:
        text.stylize("strike")
    return text


def _tag_str(tag: Optional[str], theme: dict) -> Text:
    """Render tag with color."""
    if tag:
        return Text(f"#{tag}", style=theme["tag"])
    return Text("")


def _build_task_table(manager: TodoManager, tag: Optional[str] = None) -> Table:
    """Build a Rich Table of tasks with row numbers, status, title, tag."""
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
    table.add_column("Status", style="bold", width=6, justify="center")  # new header
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


def _remove_multiple(
    manager: TodoManager, items: List[TodoItem], numbers: List[int], theme: dict
) -> None:
    """Remove tasks by their row numbers in the given items list."""
    # Collect IDs to remove (in reverse order to avoid index shift if we were using list indices)
    ids_to_remove = []
    for num in numbers:
        if 1 <= num <= len(items):
            ids_to_remove.append(items[num - 1].id)
    if not ids_to_remove:
        console.print(f"[{theme['error']}]No valid rows selected.[/{theme['error']}]")
        return
    for task_id in ids_to_remove:
        manager.remove(task_id)
    console.print(
        f"[{theme['success']}]Removed {len(ids_to_remove)} task(s).[/{theme['success']}]"
    )


def main_menu() -> None:
    """Main TUI loop: always show tasks on top, actions at bottom."""
    manager = TodoManager()
    current_tag: Optional[str] = None

    while True:
        theme = get_active_theme()
        console.clear()

        # ---- Top: Task Table ----
        task_table = _build_task_table(manager, tag=current_tag)
        console.print(task_table)
        console.print("")  # spacer

        # ---- Bottom: Action Menu ----
        menu = (
            f"[{theme['info']}]1[/] Add   "
            f"[{theme['info']}]2[/] Toggle   "
            f"[{theme['info']}]3[/] Remove   "
            f"[{theme['info']}]4[/] Filter   "
            f"[{theme['info']}]5[/] Show all   "
            f"[{theme['dim']}]0[/] Back"
        )
        console.print(menu)
        console.print()

        choice = Prompt.ask("Choose", choices=["0", "1", "2", "3", "4", "5"])

        if choice == "1":
            # Add task without clearing the screen
            title = Prompt.ask("Title")
            tag = Prompt.ask("Tag (optional)", default="")
            tag = tag.strip() if tag.strip() else None
            manager.add(title, tag)
            console.print(
                f"[{theme['success']}]Task added: {title}[/{theme['success']}]"
            )
            Prompt.ask("Press Enter", default="")

        elif choice == "2":
            # Toggle: use current filter
            items = manager.list_all(tag=current_tag, include_done=True)
            if not items:
                Prompt.ask("No tasks to toggle. Press Enter", default="")
                continue
            choice_num = IntPrompt.ask("Row number to toggle")
            if 1 <= choice_num <= len(items):
                task = items[choice_num - 1]
                updated = manager.toggle(task.id)
                if updated:
                    status = "done" if updated.done else "undone"
                    console.print(
                        f"[{theme['success']}]'{updated.title}' marked as {status}.[/{theme['success']}]"
                    )
            else:
                console.print(
                    f"[{theme['error']}]Invalid row number.[/{theme['error']}]"
                )
            Prompt.ask("Press Enter", default="")

        elif choice == "3":
            # Remove (single or multiple)
            items = manager.list_all(tag=current_tag, include_done=True)
            if not items:
                Prompt.ask("No tasks to remove. Press Enter", default="")
                continue
            raw = Prompt.ask("Row numbers to remove (space-separated)")
            try:
                numbers = [int(x) for x in raw.split()]
            except ValueError:
                console.print(f"[{theme['error']}]Invalid input.[/{theme['error']}]")
                Prompt.ask("Press Enter", default="")
                continue
            _remove_multiple(manager, items, numbers, theme)
            Prompt.ask("Press Enter", default="")

        elif choice == "4":
            # Filter by tag
            tag = Prompt.ask("Tag to filter")
            current_tag = tag.strip() if tag.strip() else None

        elif choice == "5":
            current_tag = None  # reset filter

        elif choice == "0":
            break
