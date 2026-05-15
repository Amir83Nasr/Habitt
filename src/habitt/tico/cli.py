"""Click-based CLI for quick todo commands."""

import click
from rich.console import Console

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
        # Row numbers are 1-based; list is in creation order
        if 1 <= num <= len(manager.items):
            return manager.items[num - 1].id
        else:
            raise click.BadParameter(f"No task at row {num}.")
    except ValueError:
        # Not a number – assume it's an ID
        if manager.get_by_id(identifier) is None:
            raise click.BadParameter(f"No task with ID '{identifier}'.")
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
@click.option("--tag", "-t", default=None, help="Filter by tag")
def list(tag: str | None) -> None:
    """List tasks (use --tag to filter)."""
    manager = TodoManager()
    table = _build_task_table(manager, tag=tag)
    console.print(table)


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
        click.echo(f"Task removed.")
    else:
        click.echo("Task not found.")


@main.command()
@click.option(
    "--format", "-f", "fmt", default="json", type=click.Choice(["json", "csv", "txt"])
)
def export(fmt: str) -> None:
    """Export all tasks to Desktop."""
    from pathlib import Path

    manager = TodoManager()
    desktop = Path.home() / "Desktop"
    path = manager.export_data(desktop, fmt)
    click.echo(f"Exported to {path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tico.tui import main_menu as tico_tui

        tico_tui()
    else:
        main()
