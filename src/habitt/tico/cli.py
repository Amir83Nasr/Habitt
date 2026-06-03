"""Click-based CLI for quick todo commands."""

from __future__ import annotations

import click
import click_completion
from rich.console import Console

from habitt.core.jalali_helper import today_shamsi_str
from habitt.tico.todo_manager import TodoManager
from habitt.tico.tui import _build_task_table

console = Console()


def _resolve_task_id(manager: TodoManager, identifier: str) -> str:
    """
    Try to interpret identifier as a 1-based row number.
    If it is an integer, return the ID of the task at that position.
    Otherwise treat it as a task ID directly.
    """
    try:
        num = int(identifier)
        if 1 <= num <= len(manager.items):
            return manager.items[num - 1].id
        else:
            raise click.BadParameter(f"No task at row {num}.")
    except ValueError:
        if manager.get_by_id(identifier) is None:
            raise click.BadParameter(f"No task with ID '{identifier}'.") from None
        return identifier


@click.group()
def main() -> None:
    """Tico - Todo manager. Run without subcommand for TUI."""
    pass


@main.command()
@click.argument("title")
@click.option("--tag", "-t", default=None, help="Tag for the task")
def add(title: str, tag: str | None) -> None:
    """Add a new task."""
    manager = TodoManager()
    item = manager.add(title, tag)
    click.echo(f"Added: {item.id} - {item.title}")


@main.command()
@click.argument("identifier")
def done(identifier: str) -> None:
    """Mark a task as done by row number or ID."""
    manager = TodoManager()
    task_id = _resolve_task_id(manager, identifier)
    item = manager.toggle(task_id)
    if item and item.done:
        click.echo(f"Task '{item.title}' marked as done.")
    elif item:
        click.echo(f"Task '{item.title}' is already done.")
    else:
        click.echo("Operation failed.")


@main.command()
@click.argument("identifier")
def undo(identifier: str) -> None:
    """Mark a task as undone by row number or ID."""
    manager = TodoManager()
    task_id = _resolve_task_id(manager, identifier)
    item = manager.get_by_id(task_id)
    if item and item.done:
        manager.toggle(task_id)
        click.echo(f"Task '{item.title}' marked as undone.")
    elif item:
        click.echo(f"Task '{item.title}' is already undone.")
    else:
        click.echo("Task not found.")


@main.command()
@click.argument("identifier")
def remove(identifier: str) -> None:
    """Remove a task by row number or ID."""
    manager = TodoManager()
    task_id = _resolve_task_id(manager, identifier)
    if manager.remove(task_id):
        click.echo("Task removed.")
    else:
        click.echo("Task not found.")


@main.command()
@click.option("--force", is_flag=True, help="Skip confirmation")
def reset(force: bool) -> None:
    """Delete all tasks."""
    if not force:
        confirm = click.confirm("Delete all tasks?")
        if not confirm:
            click.echo("Cancelled.")
            return
    from habitt.core.config import get_tico_file

    get_tico_file().unlink(missing_ok=True)
    click.echo("All tasks deleted.")


@main.command()
@click.option("--tag", "-t", default=None, help="Filter by tag")
@click.option("--date", "-d", default=None, help="Filter by date (YYYY/MM/DD)")
def list(tag: str | None, date: str | None) -> None:
    manager = TodoManager()
    if date is None:
        date = today_shamsi_str()  # پیش‌فرض امروز برای CLI هم
    table = _build_task_table(manager, tag=tag, date=date)
    console.print(table)


@main.command()
@click.option(
    "--format", "-f", "fmt", default="json", type=click.Choice(["json", "csv", "txt"])
)
@click.option("--date", "-d", default=None, help="Export specific date (YYYY/MM/DD)")
def export(fmt: str, date: str | None) -> None:
    from pathlib import Path

    manager = TodoManager()
    desktop = Path.home() / "Desktop"
    if date:
        path = manager.export_date_data(desktop, date, fmt)
    else:
        path = manager.export_data(desktop, fmt)
    click.echo(f"Exported to {path}")


click_completion.init()

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tico.tui import main_menu as tico_tui

        tico_tui()
    else:
        main()
