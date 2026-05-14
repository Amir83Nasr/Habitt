"""Interactive terminal UI for tico using Rich."""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from habitt.core.themes import THEME
from habitt.tico.todo_manager import TodoManager

console = Console()


def _render_checkbox(done: bool) -> str:
    """Return a checkbox string with appropriate color."""
    if done:
        return f"[{THEME['checkbox_done']}][x][/{THEME['checkbox_done']}]"
    return f"[{THEME['checkbox_open']}][ ][/{THEME['checkbox_open']}]"


def _tag_str(tag: Optional[str]) -> str:
    if tag:
        return f"[{THEME['tag']}]#{tag}[/{THEME['tag']}]"
    return ""


def show_list(manager: TodoManager, tag: Optional[str] = None) -> None:
    """Display todo items as a table."""
    console.clear()
    items = manager.list_all(tag=tag, include_done=True)
    title = "All Tasks"
    if tag:
        title += f" (tag: {tag})"

    table = Table(title=title, border_style=THEME["panel_border"])
    table.add_column("ID", style=THEME["dim"], width=8)
    table.add_column("Done", style="bold", width=6)
    table.add_column("Title", style="bold")
    table.add_column("Tag", style=THEME["tag"])

    if not items:
        table.add_row("", "", "No tasks found.", "")
    else:
        for item in items:
            table.add_row(
                item.id,
                _render_checkbox(item.done),
                item.title,
                _tag_str(item.tag),
            )

    console.print(table)
    console.print("")


def add_form(manager: TodoManager) -> None:
    """Interactive form to add a new task."""
    console.clear()
    console.print(Panel.fit("Add New Task", style=THEME["panel_border"]))
    title = Prompt.ask("Title")
    tag = Prompt.ask("Tag (optional)", default="")
    tag = tag.strip() if tag.strip() else None
    item = manager.add(title, tag)
    console.print(
        f"[{THEME['success']}]Task added: {item.id} - {item.title}[/{THEME['success']}]"
    )
    Prompt.ask("\nPress Enter to continue", default="")


def remove_form(manager: TodoManager) -> None:
    """Interactive form to remove a task."""
    console.clear()
    show_list(manager)
    item_id = Prompt.ask("Enter task ID to remove")
    if manager.remove(item_id):
        console.print(
            f"[{THEME['success']}]Task {item_id} removed.[/{THEME['success']}]"
        )
    else:
        console.print(f"[{THEME['error']}]Task not found.[/{THEME['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def toggle_form(manager: TodoManager) -> None:
    """Toggle a task's done status."""
    console.clear()
    show_list(manager)
    item_id = Prompt.ask("Enter task ID to toggle done/undone")
    item = manager.toggle(item_id)
    if item:
        status = "done" if item.done else "undone"
        console.print(
            f"[{THEME['success']}]Task {item_id} marked as {status}.[/{THEME['success']}]"
        )
    else:
        console.print(f"[{THEME['error']}]Task not found.[/{THEME['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def search_by_tag(manager: TodoManager) -> None:
    """List tasks by a specific tag."""
    console.clear()
    tag = Prompt.ask("Tag to filter by")
    show_list(manager, tag=tag.strip())
    Prompt.ask("\nPress Enter to continue", default="")


def main_menu() -> None:
    """Entry point for tico TUI."""
    manager = TodoManager()

    while True:
        console.clear()
        console.print(Panel.fit("TICO - Todo Manager", style=THEME["app_title"]))
        console.print()
        console.print(f"[{THEME['info']}]1[/{THEME['info']}] Show tasks")
        console.print(f"[{THEME['info']}]2[/{THEME['info']}] Add task")
        console.print(f"[{THEME['info']}]3[/{THEME['info']}] Toggle done")
        console.print(f"[{THEME['info']}]4[/{THEME['info']}] Remove task")
        console.print(f"[{THEME['info']}]5[/{THEME['info']}] Filter by tag")
        console.print(f"[{THEME['dim']}]0[/{THEME['dim']}] Back")
        console.print()

        choice = Prompt.ask("Your choice", choices=["1", "2", "3", "4", "5", "0"])

        if choice == "1":
            console.clear()
            show_list(manager)
            Prompt.ask("\nPress Enter to continue", default="")
        elif choice == "2":
            add_form(manager)
        elif choice == "3":
            toggle_form(manager)
        elif choice == "4":
            remove_form(manager)
        elif choice == "5":
            search_by_tag(manager)
        elif choice == "0":
            break
