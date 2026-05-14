"""Main launcher TUI that lets user pick tico or tracker."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from habitt.core.themes import THEME
from habitt.tico.tui import main_menu as tico_menu
from habitt.tracker.tui import main_menu as tracker_menu

console = Console()


def main_menu() -> None:
    """Display the main launcher menu."""
    while True:
        console.clear()
        console.print(Panel.fit("HABITT - Launcher", style=THEME["app_title"]))
        console.print()
        console.print(f"[{THEME['info']}]1[/{THEME['info']}] Todo (tico)")
        console.print(f"[{THEME['info']}]2[/{THEME['info']}] Tracker")
        console.print(f"[{THEME['dim']}]0[/{THEME['dim']}] Exit")
        console.print()

        choice = Prompt.ask("Your choice", choices=["1", "2", "0"])

        if choice == "1":
            tico_menu()
        elif choice == "2":
            tracker_menu()
        elif choice == "0":
            break
