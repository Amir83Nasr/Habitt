"""Arrow-navigable menu utility for Habitt TUI."""

from typing import List, Optional, Tuple
import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()


def select_from_options(
    options: List[Tuple[str, str]],
    title: str = "",
    theme: Optional[dict] = None,
    cancel_key: str = "q",
) -> Optional[str]:
    """
    Display an arrow-navigable list and return the key of the selected option.

    Args:
        options: List of (key, label) tuples.
        title: Optional header text.
        theme: Active theme dict for styling.
        cancel_key: Key to cancel and return None.

    Returns:
        The key string of the chosen option, or None if cancelled.
    """
    if not options:
        return None

    idx = 0
    theme = theme or {}

    def render():
        out = Text()
        if title:
            out.append(title + "\n", style=theme.get("info", ""))
        for i, (key, label) in enumerate(options):
            prefix = "> " if i == idx else "  "
            line = f"{prefix}[{key}] {label}"
            if i == idx:
                out.append(line + "\n", style=theme.get("info", "bold"))
            else:
                out.append(line + "\n", style="")
        out.append(f"\n↑/↓ move  Enter select  {cancel_key} cancel")
        return out

    with Live(render(), refresh_per_second=10, screen=False) as live:
        while True:
            key = readchar.readkey()
            if key == readchar.key.UP:
                idx = (idx - 1) % len(options)
            elif key == readchar.key.DOWN:
                idx = (idx + 1) % len(options)
            elif key == readchar.key.ENTER:
                return options[idx][0]
            elif key.lower() == cancel_key.lower():
                return None
            else:
                # Direct key shortcut
                for i, (k, _) in enumerate(options):
                    if k.lower() == key.lower():
                        return k
            live.update(render())
