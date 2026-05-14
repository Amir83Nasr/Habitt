"""Main entry point for habitt launcher (tico + tracker)."""

import click

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from habitt.core.themes import get_active_theme, save_theme, PRESETS

console = Console()


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
                theme = get_active_theme()  # reload
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


def _get_current_theme_name() -> str:
    """Return the name of the currently active theme."""
    import json

    try:
        if __import__("habitt.core.config").CONFIG_FILE.exists():
            with open(
                __import__("habitt.core.config").CONFIG_FILE, "r", encoding="utf-8"
            ) as f:
                config = json.load(f)
            return config.get("theme", "blue_purple")
    except Exception:
        pass
    return "blue_purple"


def launcher_menu() -> None:
    """Display the main launcher menu."""
    while True:
        theme = get_active_theme()
        console.clear()
        console.print(Panel.fit("HABITT - Launcher", style=theme["app_title"]))
        console.print()
        console.print(f"[{theme['info']}]1[/{theme['info']}] Todo (tico)")
        console.print(f"[{theme['info']}]2[/{theme['info']}] Tracker")
        console.print(f"[{theme['info']}]3[/{theme['info']}] Settings")
        console.print(f"[{theme['dim']}]0[/{theme['dim']}] Exit")
        console.print()

        choice = Prompt.ask("Your choice", choices=["1", "2", "3", "0"])

        if choice == "1":
            from habitt.tico.tui import main_menu as tico_menu

            tico_menu()
        elif choice == "2":
            from habitt.tracker.tui import main_menu as tracker_menu

            tracker_menu()
        elif choice == "3":
            settings_menu()
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
