"""Arrow-navigable menu utility for Habitt TUI."""

from __future__ import annotations

import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()


def select_from_options(
    options: list[tuple[str, str]],
    title: str = "",
    theme: dict[str, str] | None = None,
    cancel_key: str = "q",
    show_key: bool = True,
) -> str | None:
    if not options:
        return None

    idx = 0
    theme = theme or {}

    def render(cancel_key: str) -> Text:
        out = Text()
        if title:
            out.append(title + "\n", style=theme.get("info", ""))
        for i, (key, label) in enumerate(options):
            prefix = "> " if i == idx else "  "
            if show_key:
                line = f"{prefix}[{key}] {label}"
            else:
                line = f"{prefix}{label}"
            if i == idx:
                out.append(line + "\n", style=theme.get("info", "bold"))
            else:
                out.append(line + "\n", style="")
        out.append(f"\n↑/↓ move  Enter select  {cancel_key} cancel")
        return out

    with Live(render(cancel_key), refresh_per_second=10, screen=False) as live:
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
                # direct key shortcut only if show_key is True
                if show_key:
                    for _, (k, _) in enumerate(options):
                        if k.lower() == key.lower():
                            return k
            live.update(render(cancel_key))
