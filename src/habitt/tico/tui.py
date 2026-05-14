"""Interactive terminal UI for tico using Rich."""

from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from habitt.core.themes import get_active_theme
from habitt.tico.todo_manager import TodoManager, TodoItem

console = Console()


def _render_checkbox(done: bool, theme: dict) -> str:
    """Return a checkbox string with appropriate color."""
    if done:
        return f"[{theme['checkbox_done']}][x][/{theme['checkbox_done']}]"
    return f"[{theme['checkbox_open']}][ ][/{theme['checkbox_open']}]"


def _tag_str(tag: Optional[str], theme: dict) -> str:
    if tag:
        return f"[{theme['tag']}]#{tag}[/{theme['tag']}]"
    return ""


def _display_items(manager: TodoManager, tag: Optional[str] = None) -> List[TodoItem]:
    """Show tasks with row numbers and return the displayed items."""
    theme = get_active_theme()
    items = manager.list_all(tag=tag, include_done=True)

    title = "All Tasks"
    if tag:
        title += f" (tag: {tag})"

    table = Table(title=title, border_style=theme["panel_border"])
    table.add_column("#", style=theme["dim"], width=4, justify="right")
    table.add_column("Done", style="bold", width=6)
    table.add_column("Title", style="bold")
    table.add_column("Tag", style=theme["tag"])

    if not items:
        table.add_row("", "", "No tasks found.", "")
    else:
        for i, item in enumerate(items, start=1):
            table.add_row(
                str(i),
                _render_checkbox(item.done, theme),
                item.title,
                _tag_str(item.tag, theme),
            )

    console.clear()
    console.print(table)
    console.print("")
    return items


def show_list(manager: TodoManager, tag: Optional[str] = None) -> None:
    """Display todo items (no return)."""
    _display_items(manager, tag)
    Prompt.ask("Press Enter to continue", default="")


def add_form(manager: TodoManager) -> None:
    """Interactive form to add a new task."""
    theme = get_active_theme()
    console.clear()
    console.print(Panel.fit("Add New Task", style=theme["panel_border"]))
    title = Prompt.ask("Title")
    tag = Prompt.ask("Tag (optional)", default="")
    tag = tag.strip() if tag.strip() else None
    item = manager.add(title, tag)
    console.print(f"[{theme['success']}]Task added: {item.title}[/{theme['success']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def remove_form(manager: TodoManager) -> None:
    """Interactive form to remove a task by row number."""
    theme = get_active_theme()
    items = _display_items(manager)
    if not items:
        Prompt.ask("Press Enter to continue", default="")
        return

    choice = IntPrompt.ask("Enter row number to remove")
    if 1 <= choice <= len(items):
        item = items[choice - 1]
        if manager.remove(item.id):
            console.print(
                f"[{theme['success']}]Task '{item.title}' removed.[/{theme['success']}]"
            )
        else:
            console.print(
                f"[{theme['error']}]Failed to remove task.[/{theme['error']}]"
            )
    else:
        console.print(f"[{theme['error']}]Invalid row number.[/{theme['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def toggle_form(manager: TodoManager) -> None:
    """Toggle a task's done status by row number."""
    theme = get_active_theme()
    items = _display_items(manager)
    if not items:
        Prompt.ask("Press Enter to continue", default="")
        return

    choice = IntPrompt.ask("Enter row number to toggle done/undone")
    if 1 <= choice <= len(items):
        item = items[choice - 1]
        updated = manager.toggle(item.id)
        if updated:
            status = "done" if updated.done else "undone"
            console.print(
                f"[{theme['success']}]Task '{updated.title}' marked as {status}.[/{theme['success']}]"
            )
        else:
            console.print(
                f"[{theme['error']}]Could not toggle task.[/{theme['error']}]"
            )
    else:
        console.print(f"[{theme['error']}]Invalid row number.[/{theme['error']}]")
    Prompt.ask("\nPress Enter to continue", default="")


def search_by_tag(manager: TodoManager) -> None:
    """List tasks by a specific tag."""
    theme = get_active_theme()
    console.clear()
    tag = Prompt.ask("Tag to filter by")
    _display_items(manager, tag=tag.strip())
    Prompt.ask("\nPress Enter to continue", default="")


def main_menu() -> None:
    """Entry point for tico TUI."""
    manager = TodoManager()

    while True:
        theme = get_active_theme()
        console.clear()
        console.print(Panel.fit("TICO - Todo Manager", style=theme["app_title"]))
        console.print()
        console.print(f"[{theme['info']}]1[/{theme['info']}] Show tasks")
        console.print(f"[{theme['info']}]2[/{theme['info']}] Add task")
        console.print(f"[{theme['info']}]3[/{theme['info']}] Toggle done")
        console.print(f"[{theme['info']}]4[/{theme['info']}] Remove task")
        console.print(f"[{theme['info']}]5[/{theme['info']}] Filter by tag")
        console.print(f"[{theme['dim']}]0[/{theme['dim']}] Back")
        console.print()

        choice = Prompt.ask("Your choice", choices=["1", "2", "3", "4", "5", "0"])

        if choice == "1":
            show_list(manager)
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
