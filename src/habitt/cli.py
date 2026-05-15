"""Main entry point for habitt launcher (tico + tracker + plugins)."""

import click
import click_completion
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.prompt import Prompt
from rich.text import Text

from habitt.core.config import (get_builtin_plugins_dir, get_data_dir,
                                get_plugins_dir, set_data_dir)
from habitt.core.jalali_helper import today_shamsi_str
from habitt.core.plugin_base import PluginBase, discover_plugins
from habitt.core.themes import PRESETS, get_active_theme, save_theme

plugins = discover_plugins(get_plugins_dir(), get_builtin_plugins_dir())
click_completion.init()
console = Console()


def theme_menu() -> None:
    """Sub-menu for theme selection."""
    theme_names = list(PRESETS.keys())
    current = _get_current_theme_name()
    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("T H E M E", style=theme["info"])
        console.print()
        console.print(f"Current: [bold]{current}[/bold]\n")
        for i, name in enumerate(theme_names, start=1):
            marker = " (active)" if name == current else ""
            console.print(f"  [{theme['info']}]{i}[/{theme['info']}] {name}{marker}")
        console.print(f"  [{theme['dim']}]0[/{theme['dim']}] Back")
        console.print()
        prompt = Text("Choose", style=theme["info"])
        prompt.append(" > ", style="white")
        choice = Prompt.ask(
            prompt, choices=[str(i) for i in range(len(theme_names) + 1)]
        )
        if choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(theme_names):
            try:
                save_theme(theme_names[idx])
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
    Prompt.ask("Press Enter to continue", default="")


def change_data_dir() -> None:
    """Prompt user for a new data directory and save it."""
    theme = get_active_theme()
    console.clear()
    console.print(Panel.fit("Change Data Directory", style=theme["panel_border"]))
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


def settings_main_menu() -> None:
    """Main settings menu – clean style."""
    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("S E T T I N G S", style=theme["info"])
        console.print()
        console.print(f"  [{theme['info']}]1.[/] Theme")
        console.print(f"  [{theme['info']}]2.[/] Export All Data")
        console.print(f"  [{theme['info']}]3.[/] Change Data Directory")
        console.print(f"  [{theme['error']}]4.[/] Reset All Data")
        console.print(f"  [{theme['dim']}]0.[/] Back")
        console.print()
        prompt = Text("Choose", style=theme["info"])
        prompt.append(" > ", style="white")
        choice = Prompt.ask(prompt, choices=["0", "1", "2", "3", "4"])
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


def plugins_menu(plugins: list) -> None:
    """Sub-menu showing available plugins."""
    theme = get_active_theme()
    while True:
        console.clear()
        console.rule("P L U G I N S", style=theme["info"])
        console.print()
        if not plugins:
            console.print("No plugins installed.")
        else:
            for i, plugin in enumerate(plugins, start=1):
                console.print(
                    f"  [{theme['info']}]{i}.[/] {plugin.name} - {plugin.description}"
                )
        console.print(f"  [{theme['dim']}]0.[/] Back")
        console.print()

        prompt = Text("Choose", style=theme["info"])
        prompt.append(" > ", style="white")
        choices = ["0"] + [str(i) for i in range(1, len(plugins) + 1)]
        choice = Prompt.ask(prompt, choices=choices)
        if choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(plugins):
            plugins[idx].run_tui()


def launcher_menu() -> None:
    """Display the main launcher menu with dynamic plugin entries."""
    while True:
        theme = get_active_theme()
        console.clear()

        # Header
        console.rule("H A B I T T", style="bright_blue")
        console.print()

        # Dashboard
        from habitt.tico.todo_manager import TodoManager
        from habitt.tracker.tracker_manager import TrackerManager

        todo_mgr = TodoManager()
        open_tasks = len(todo_mgr.list_all(include_done=False))
        total_tasks = len(todo_mgr.list_all())
        done_tasks = total_tasks - open_tasks

        tracker_mgr = TrackerManager()
        today_activities = tracker_mgr.list_today()
        today_minutes = tracker_mgr.daily_total_minutes(today_shamsi_str())
        hours = int(today_minutes // 60)
        mins = int(today_minutes % 60)
        time_str = f"{hours}h {mins}m"

        task_progress = Progress(
            TextColumn("Tasks  "),
            BarColumn(bar_width=30, style=theme["accent"]),
            TextColumn(f"  {done_tasks}/{total_tasks}"),
        )
        task_bar = task_progress
        task_bar.add_task(
            "", total=total_tasks if total_tasks > 0 else 1, completed=done_tasks
        )

        target_minutes = 8 * 60
        time_progress = Progress(
            TextColumn("Time   "),
            BarColumn(bar_width=30, style=theme["clock"]),
            TextColumn(f"  {time_str} / 8h"),
        )
        time_bar = time_progress
        time_bar.add_task(
            "",
            total=target_minutes if target_minutes > 0 else 1,
            completed=today_minutes,
        )

        left_panel = Panel(task_bar, title="Tasks", border_style=theme["panel_border"])
        right_panel = Panel(
            time_bar, title="Today's Focus", border_style=theme["panel_border"]
        )
        console.print(Columns([left_panel, right_panel]))
        console.print()

        # Menu
        console.print(f"  [{theme['info']}]1.[/] Todo")
        console.print(f"  [{theme['info']}]2.[/] Tracker")
        console.print(f"  [{theme['info']}]3.[/] Settings")
        console.print(f"  [{theme['info']}]4.[/] Plugins")
        console.print(f"  [{theme['dim']}]0.[/] Exit")
        console.print()

        prompt = Text("Choose", style=theme["info"])
        prompt.append(" > ", style="white")
        choice = Prompt.ask(prompt, choices=["0", "1", "2", "3", "4"])

        if choice == "1":
            from habitt.tico.tui import main_menu as tico_menu

            tico_menu()
        elif choice == "2":
            from habitt.tracker.tui import main_menu as tracker_menu

            tracker_menu()
        elif choice == "3":
            settings_main_menu()
        elif choice == "4":
            plugins = discover_plugins(get_plugins_dir(), get_builtin_plugins_dir())
            plugins_menu(plugins)
        elif choice == "0":
            break


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Habitt - the launcher for tico and tracker and plugins."""
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


@main.command("plugins")
def list_plugins() -> None:
    """List all installed plugins."""
    plugins = discover_plugins(get_plugins_dir(), get_builtin_plugins_dir())
    if not plugins:
        console.print("[dim]No plugins found.[/dim]")
    else:
        for plugin in plugins:
            console.print(f" - {plugin.name}: {plugin.description}")


@main.command("plugin")
@click.argument("name")
@click.argument("action", required=False, default="tui")
def run_plugin(name: str, action: str) -> None:
    """Run a plugin by name (default: tui)."""
    plugins = discover_plugins(get_plugins_dir(), get_builtin_plugins_dir())
    for plugin in plugins:
        if plugin.name == name:
            if action == "tui":
                plugin.run_tui()
            else:
                plugin.cli([action])
            return
    console.print(f"[red]Plugin '{name}' not found.[/red]")


if __name__ == "__main__":
    main()
