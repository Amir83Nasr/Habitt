"""Main entry point for habitt launcher (tico + tracker)."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns

from habitt.core.themes import get_active_theme, save_theme, PRESETS
from habitt.core.jalali_helper import today_shamsi_str
from habitt.core.config import get_data_dir, set_data_dir

console = Console()


def _get_current_theme_name() -> str:
    """Return the name of the currently active theme."""
    import json

    try:
        from habitt.core.config import CONFIG_FILE

        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("theme", "blue_purple")
    except Exception:
        pass
    return "blue_purple"


def settings_menu() -> None:
    """Display theme settings."""
    theme = get_active_theme()
    theme_names = list(PRESETS.keys())
    current_theme = _get_current_theme_name()

    while True:
        console.clear()
        console.print(Panel.fit("Settings", style=theme["app_title"]))
        console.print()
        console.print(f"Current theme: [bold]{current_theme}[/bold]\n")
        console.print("Available themes:")
        for i, name in enumerate(theme_names, start=1):
            marker = " (active)" if name == current_theme else ""
            console.print(f"  [{theme['info']}]{i}[/{theme['info']}] {name}{marker}")
        console.print(f"  [{theme['dim']}]0[/{theme['dim']}] Back")
        console.print()

        choice = Prompt.ask(
            "Your choice", choices=[str(i) for i in range(len(theme_names) + 1)]
        )
        if choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(theme_names):
            new_theme = theme_names[idx]
            try:
                save_theme(new_theme)
                theme = get_active_theme()
                current_theme = new_theme
                console.print(
                    f"[{theme['success']}]Theme changed to '{new_theme}'.[/{theme['success']}]"
                )
            except Exception as e:
                console.print(
                    f"[{theme['error']}]Failed to save theme: {e}[/{theme['error']}]"
                )
            Prompt.ask("\nPress Enter to continue", default="")
        else:
            console.print(f"[{theme['error']}]Invalid choice.[/{theme['error']}]")
            Prompt.ask("\nPress Enter to continue", default="")


def theme_menu() -> None:
    """Sub-menu for theme selection."""
    theme = get_active_theme()
    theme_names = list(PRESETS.keys())
    current = _get_current_theme_name()
    while True:
        console.clear()
        console.print(Panel.fit("Theme Settings", style=theme["app_title"]))
        console.print(f"Current theme: [bold]{current}[/bold]\n")
        for i, name in enumerate(theme_names, start=1):
            marker = " (active)" if name == current else ""
            console.print(f"  [{theme['info']}]{i}[/{theme['info']}] {name}{marker}")
        console.print(f"  [{theme['dim']}]0[/{theme['dim']}] Back")
        console.print()
        choice = Prompt.ask(
            "Choose", choices=[str(i) for i in range(len(theme_names) + 1)]
        )
        if choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(theme_names):
            try:
                save_theme(theme_names[idx])
                theme = get_active_theme()
                current = theme_names[idx]
                console.print(
                    f"[{theme['success']}]Theme changed to '{current}'.[/{theme['success']}]"
                )
            except Exception as e:
                console.print(f"[{theme['error']}]Error: {e}[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")
        else:
            console.print(f"[{theme['error']}]Invalid choice.[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")


def export_all_data() -> None:
    """Export both tico and tracker data to Desktop in chosen format."""
    theme = get_active_theme()
    fmt = Prompt.ask("Format (json/csv/txt)", choices=["json", "csv", "txt"])
    from pathlib import Path
    from habitt.tico.todo_manager import TodoManager
    from habitt.tracker.tracker_manager import TrackerManager

    desktop = Path.home() / "Desktop"
    try:
        tico_path = TodoManager().export_data(desktop, fmt)
        tracker_path = TrackerManager().export_data(desktop, fmt)
        console.print(f"[{theme['success']}]Tico → {tico_path}[/{theme['success']}]")
        console.print(
            f"[{theme['success']}]Tracker → {tracker_path}[/{theme['success']}]"
        )
    except Exception as e:
        console.print(f"[{theme['error']}]Export failed: {e}[/{theme['error']}]")


def settings_main_menu() -> None:
    """Main settings menu with sub-options."""
    theme = get_active_theme()
    while True:
        console.clear()
        console.print(Panel.fit("Settings", style=theme["app_title"]))
        console.print(f"[{theme['info']}]1[/] Theme")
        console.print(f"[{theme['info']}]2[/] Export All Data")
        console.print(f"[{theme['info']}]3[/] Change Data Directory")
        console.print(f"[{theme['error']}]4[/] Reset All Data")
        console.print(f"[{theme['dim']}]0[/] Back")
        console.print()
        choice = Prompt.ask("Choose", choices=["0", "1", "2", "3", "4"])
        if choice == "1":
            theme_menu()
        elif choice == "2":
            export_all_data()
            Prompt.ask("Press Enter to continue", default="")
        elif choice == "3":
            change_data_dir()
        elif choice == "4":
            reset_all_data()
        elif choice == "0":
            break


def change_data_dir() -> None:
    """Prompt user for a new data directory and save it."""
    theme = get_active_theme()
    console.clear()
    console.print(Panel.fit("Change Data Directory", style=theme["app_title"]))
    current = get_data_dir()
    console.print(f"Current data directory: [bold]{current}[/bold]\n")
    new_path = Prompt.ask("Enter new data directory path")
    if new_path.strip():
        try:
            set_data_dir(new_path.strip())
            console.print(
                f"[{theme['success']}]Data directory changed to {new_path}[/{theme['success']}]"
            )
            console.print("[yellow]Note: existing data was not moved.[/yellow]")
        except Exception as e:
            console.print(
                f"[{theme['error']}]Failed to set directory: {e}[/{theme['error']}]"
            )
    else:
        console.print(f"[{theme['dim']}]No change made.[/{theme['dim']}]")
    Prompt.ask("Press Enter to continue", default="")


def reset_all_data() -> None:
    """Delete all todo and tracker data files after confirmation."""
    theme = get_active_theme()
    console.clear()
    console.print(Panel.fit("Reset All Data", style=theme["error"]))
    console.print(
        "[bold red]This will permanently delete all your tasks and activities.[/bold red]"
    )
    confirm = Prompt.ask("Type 'YES' to confirm")
    if confirm != "YES":
        console.print(f"[{theme['dim']}]Reset cancelled.[/{theme['dim']}]")
        Prompt.ask("Press Enter to continue", default="")
        return

    data_dir = get_data_dir()
    files_to_remove = [
        data_dir / "tico.json",
        data_dir / "tracker.json",
        data_dir / "timer_state.json",
    ]
    for filepath in files_to_remove:
        try:
            filepath.unlink(missing_ok=True)
        except OSError:
            pass
    console.print(
        f"[{theme['success']}]All data has been cleared.[/{theme['success']}]"
    )
    Prompt.ask("Press Enter to continue", default="")


def launcher_menu() -> None:
    """Display the main launcher menu with quick stats."""
    while True:
        theme = get_active_theme()
        console.clear()

        # Header
        console.print(Panel.fit("HABITT", style=theme["app_title"]))

        # Quick stats
        from habitt.tico.todo_manager import TodoManager
        from habitt.tracker.tracker_manager import TrackerManager

        todo_mgr = TodoManager()
        open_tasks = len(todo_mgr.list_all(include_done=False))
        total_tasks = len(todo_mgr.list_all())
        tracker_mgr = TrackerManager()
        today_activities = tracker_mgr.list_today()
        today_minutes = tracker_mgr.daily_total_minutes(today_shamsi_str())
        hours = int(today_minutes // 60)
        mins = int(today_minutes % 60)
        time_str = f"{hours}h {mins}m"

        left = Panel(
            f"[bold]Todo[/bold]\nOpen: {open_tasks}\nTotal: {total_tasks}",
            style=theme["panel_border"],
        )
        right = Panel(
            f"[bold]Tracker Today[/bold]\nEntries: {len(today_activities)}\nTime: {time_str}",
            style=theme["panel_border"],
        )
        console.print(Columns([left, right]))
        console.print("")

        # Menu
        console.print(
            f"[{theme['info']}]1[/] Todo (tico)   "
            f"[{theme['info']}]2[/] Tracker   "
            f"[{theme['info']}]3[/] Settings   "
            f"[{theme['dim']}]0[/] Exit"
        )
        console.print()

        choice = Prompt.ask("Choose", choices=["0", "1", "2", "3"])

        if choice == "1":
            from habitt.tico.tui import main_menu as tico_menu

            tico_menu()
        elif choice == "2":
            from habitt.tracker.tui import main_menu as tracker_menu

            tracker_menu()
        elif choice == "3":
            settings_main_menu()
        elif choice == "0":
            break


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Habitt - the launcher for tico and tracker."""
    if ctx.invoked_subcommand is None:
        launcher_menu()


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
