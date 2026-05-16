"""Main entry point for habitt launcher (tico + tracker + plugins)."""

from __future__ import annotations

from pathlib import Path

import click
import click_completion
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.prompt import Prompt

from habitt.core.config import (
    get_builtin_plugins_dir,
    get_data_dir,
    get_plugins_dir,
    set_data_dir,
)
from habitt.core.jalali_helper import today_shamsi_str
from habitt.core.menu_utils import select_from_options
from habitt.core.plugin_base import PluginBase, discover_plugins
from habitt.core.themes import get_active_theme, get_all_themes, save_theme

click_completion.init()
console = Console()


def focus_music_menu() -> None:
    """Sub-menu for Focus music settings."""

    from habitt.core.focus_config import (
        list_builtin_music,
        list_user_music,
        load_focus_config,
        save_focus_config,
    )

    config = load_focus_config()
    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("Focus Music", style=theme["info"])
        console.print()
        console.print(
            "[dim]Place your music files in ~/.habitt/focus_music/ "
            "or use built-in tracks.[/dim]\n"
        )

        current = config.get("music_source", "none")
        if current == "none":
            status = "No music"
        elif current.startswith("builtin:"):
            name = current.split(":", 1)[1]
            stem = Path(name).stem
            status = f"[built-in] {stem}"
        elif current.startswith("custom:"):
            path = Path(current.split(":", 1)[1])
            status = f"[custom] {path.stem}"
        else:
            status = current

        console.print(f"Current: [bold]{status}[/bold]\n")

        options: list[tuple[str, str]] = []

        # Built-in music
        for name in list_builtin_music():
            stem = Path(name).stem
            label = f"[built-in] {stem}"
            if current == f"builtin:{name}":
                label += " (active)"
            options.append((f"builtin:{name}", label))

        # User music
        for f in list_user_music():
            stem = f.stem
            label = f"[custom] {stem}"
            if current == f"custom:{f}":
                label += " (active)"
            options.append((f"custom:{f}", label))

        options.append(("none", "No music"))
        options.append(("0", "Back"))

        choice = select_from_options(options, theme=theme, show_key=False)
        if choice is None or choice == "0":
            break
        else:
            config["music_source"] = choice
            save_focus_config(config)


def _get_current_theme_name() -> str:
    """Return the name of the currently active theme."""
    import json

    try:
        from habitt.core.config import CONFIG_FILE

        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        theme = config.get("theme", "blue_purple")
        if isinstance(theme, str):
            return theme
    except Exception:
        pass
    return "blue_purple"


def theme_menu() -> None:
    """Sub-menu for theme selection."""
    all_themes = get_all_themes()
    theme_names = list(all_themes.keys())
    current = _get_current_theme_name()
    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("T H E M E", style=theme["info"])
        console.print(f"Current: [bold]{current}[/bold]\n")
        options = []
        for i, name in enumerate(theme_names, start=1):
            marker = " (active)" if name == current else ""
            options.append((str(i), f"{name}{marker}"))
        options.append(("0", "Back"))
        choice = select_from_options(options, theme=theme)
        if choice is None or choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(theme_names):
            try:
                save_theme(theme_names[idx])
                current = theme_names[idx]
                console.print(
                    f"[{theme['success']}]Theme changed to '{current}'."
                    f"[/{theme['success']}]"
                )
            except Exception as e:
                console.print(f"[{theme['error']}]Error: {e}[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")


def export_all_data() -> None:
    """Export both tico and tracker data to Desktop."""
    theme = get_active_theme()
    fmt = Prompt.ask("Format (json/csv/txt)", choices=["json", "csv", "txt"])

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
    console.rule("Change Data Directory", style=theme["info"])
    current = get_data_dir()
    console.print(f"Current data directory: [bold]{current}[/bold]\n")
    new_path = Prompt.ask("Enter new data directory path")
    if new_path.strip():
        try:
            set_data_dir(new_path.strip())
            console.print(
                f"[{theme['success']}]Data directory changed to {new_path}"
                f"[/{theme['success']}]"
            )
            console.print("[yellow]Note: existing data was not moved.[/yellow]")
        except Exception as e:
            console.print(f"[{theme['error']}]Failed: {e}[/{theme['error']}]")
    else:
        console.print(f"[{theme['dim']}]No change made.[/{theme['dim']}]")
    Prompt.ask("Press Enter to continue", default="")


def reset_all_data() -> None:
    """Delete all todo and tracker data files after confirmation."""
    theme = get_active_theme()
    console.clear()
    console.rule("Reset All Data", style=theme["error"])
    console.print(
        "[bold red]This will permanently delete all your tasks and "
        "activities.[/bold red]"
    )
    confirm = Prompt.ask("Type 'YES' to confirm")
    if confirm != "YES":
        console.print(f"[{theme['dim']}]Reset cancelled.[/{theme['dim']}]")
        Prompt.ask("Press Enter to continue", default="")
        return
    data_dir = get_data_dir()
    for name in ["tico.json", "tracker.json", "timer_state.json"]:
        (data_dir / name).unlink(missing_ok=True)
    console.print(f"[{theme['success']}]All data cleared.[/{theme['success']}]")
    Prompt.ask("Press Enter to continue", default="")


def settings_main_menu() -> None:
    """Main settings menu with arrow navigation."""

    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("S E T T I N G S", style=theme["info"])
        options = [
            ("1", "Theme"),
            ("2", "Export All Data"),
            ("3", "Change Data Directory"),
            ("4", "Reset All Data"),
            ("5", "Focus Music"),
            ("0", "Back"),
        ]
        choice = select_from_options(options, theme=theme)

        if choice is None or choice == "0":
            break
        if choice == "1":
            theme_menu()
        elif choice == "2":
            export_all_data()
            Prompt.ask("Press Enter to continue", default="")
        elif choice == "3":
            change_data_dir()
        elif choice == "4":
            reset_all_data()
        elif choice == "5":
            focus_music_menu()


def plugins_menu(plugins: list[PluginBase]) -> None:
    """Sub-menu showing available plugins."""
    theme = get_active_theme()
    while True:
        console.clear()
        console.rule("P L U G I N S", style=theme["info"])
        if not plugins:
            console.print("No plugins installed.")
            Prompt.ask("Press Enter to return", default="")
            break
        options = []
        for i, plugin in enumerate(plugins, start=1):
            options.append((str(i), f"{plugin.name} - {plugin.description}"))
        options.append(("0", "Back"))
        choice = select_from_options(options, theme=theme)
        if choice is None or choice == "0":
            break
        idx = int(choice) - 1
        if 0 <= idx < len(plugins):
            plugins[idx].run_tui()


def launcher_menu() -> None:
    """Display the main launcher menu with dashboard and arrow navigation."""
    while True:
        theme = get_active_theme()
        console.clear()
        console.rule("H A B I T T", style="bright_blue")
        console.print()

        from habitt.tico.todo_manager import TodoManager
        from habitt.tracker.tracker_manager import TrackerManager

        todo_mgr = TodoManager()
        open_tasks = len(todo_mgr.list_all(include_done=False))
        total_tasks = len(todo_mgr.list_all())
        done_tasks = total_tasks - open_tasks

        tracker_mgr = TrackerManager()
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
            "",
            total=total_tasks if total_tasks > 0 else 1,
            completed=int(done_tasks),
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
            completed=int(today_minutes),
        )

        left_panel = Panel(task_bar, title="Tasks", border_style=theme["panel_border"])
        right_panel = Panel(
            time_bar, title="Today's Focus", border_style=theme["panel_border"]
        )
        console.print(Columns([left_panel, right_panel]))
        console.print()

        options = [
            ("1", "Tico"),
            ("2", "Tracker"),
            ("3", "Settings"),
            ("4", "Plugins"),
            ("0", "Exit"),
        ]
        choice = select_from_options(options, theme=theme)
        if choice is None or choice == "0":
            break
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


@main.command()
@click.option("--force", is_flag=True, help="Skip confirmation")
def reset(force: bool) -> None:
    """Delete all tasks and activities."""
    if not force:
        confirm = click.confirm(
            "This will permanently delete all your tasks and activities. Continue?"
        )
        if not confirm:
            click.echo("Reset cancelled.")
            return
    data_dir = get_data_dir()
    for name in ["tico.json", "tracker.json", "timer_state.json"]:
        (data_dir / name).unlink(missing_ok=True)
    click.echo("All data cleared.")


if __name__ == "__main__":
    main()
