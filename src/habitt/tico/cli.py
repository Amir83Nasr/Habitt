"""Click-based CLI for quick todo commands."""

import click

from habitt.tico.todo_manager import TodoManager
from habitt.tico.tui import show_list as tui_show_list


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
    tui_show_list(manager, tag=tag)


@main.command()
@click.argument("task_id")
def done(task_id: str) -> None:
    """Mark a task as done."""
    manager = TodoManager()
    item = manager.toggle(task_id)
    if item and item.done:
        click.echo(f"Task {task_id} marked as done.")
    else:
        click.echo("Task not found or already undone.")


@main.command()
@click.argument("task_id")
def undo(task_id: str) -> None:
    """Mark a task as undone."""
    manager = TodoManager()
    # To undo we need to ensure it ends up undone, so toggle if currently done
    item = manager.get_by_id(task_id)
    if item and item.done:
        manager.toggle(task_id)
        click.echo(f"Task {task_id} marked as undone.")
    elif item:
        click.echo(f"Task {task_id} is already undone.")
    else:
        click.echo("Task not found.")


@main.command()
@click.argument("task_id")
def remove(task_id: str) -> None:
    """Remove a task."""
    manager = TodoManager()
    if manager.remove(task_id):
        click.echo(f"Task {task_id} removed.")
    else:
        click.echo("Task not found.")


# If no subcommand is given, launch the TUI
if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        from habitt.tico.tui import main_menu as tico_tui

        tico_tui()
    else:
        main()
