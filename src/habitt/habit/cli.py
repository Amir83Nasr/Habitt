"""Click entry point for habit launcher. Supports direct shortcuts."""

import click

from habitt.habit.tui import main_menu


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Habit - the launcher for tico and tracker."""
    if ctx.invoked_subcommand is None:
        main_menu()


@main.command()
def todo() -> None:
    """Launch tico directly."""
    from habitt.tico.tui import main_menu as tico_menu

    tico_menu()


@main.command()
def track() -> None:
    """Launch tracker directly."""
    from habitt.tracker.tui import main_menu as tracker_menu

    tracker_menu()


if __name__ == "__main__":
    main()
