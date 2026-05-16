"""Quick Notes plugin for Habitt – simple note-taking."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from habitt.core.jalali_helper import now_shamsi_str
from habitt.core.plugin_base import PluginBase
from habitt.core.themes import get_active_theme

console = Console()

NOTES_DIR = Path.home() / ".habitt" / "plugins" / "notes"
NOTES_FILE = NOTES_DIR / "notes.json"


class NotesPlugin(PluginBase):
    name = "notes"
    description = "Quick notes – jot down ideas and thoughts"

    def __init__(self) -> None:
        self.notes: list[dict[str, Any]] = []
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if NOTES_FILE.exists():
            try:
                with open(NOTES_FILE, encoding="utf-8") as f:
                    self.notes = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.notes = []

    def _save(self) -> None:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def run_tui(self) -> None:
        """Main TUI loop for the notes plugin."""
        while True:
            theme = get_active_theme()
            console.clear()
            console.rule("Q U I C K   N O T E S", style=theme["info"])
            console.print()

            self._list_notes(theme)

            console.print()
            console.print(
                f"[{theme['info']}]A[/]dd  "
                f"[{theme['info']}]S[/]earch  "
                f"[{theme['info']}]D[/]elete  "
                f"[{theme['info']}]E[/]xport  "
                f"[{theme['dim']}]Q[/]uit"
            )
            console.print()

            prompt = Text("Action", style=theme["info"])
            prompt.append(" > ", style="white")
            cmd = Prompt.ask(prompt).strip().lower()

            if cmd == "a":
                self._add_note(theme)
            elif cmd == "s":
                self._search_notes(theme)
            elif cmd == "d":
                self._delete_notes(theme)
            elif cmd == "e":
                self._export_notes(theme)
            elif cmd == "q":
                break
            else:
                console.print(f"[{theme['error']}]Unknown command.[/{theme['error']}]")
                Prompt.ask("Press Enter", default="")

    def _add_note(self, theme: dict[str, Any]) -> None:
        """Add a new note."""
        title = Prompt.ask("Title")
        body = Prompt.ask("Body (optional)", default="")
        note = {
            "title": title,
            "body": body.strip(),
            "created_at": now_shamsi_str(),
        }
        self.notes.append(note)
        self._save()
        console.print(f"[{theme['success']}]Note added.[/{theme['success']}]")
        Prompt.ask("Press Enter", default="")

    def _list_notes(self, theme: dict[str, Any]) -> None:
        """Display notes as a table."""
        if not self.notes:
            console.print("No notes yet.", style=theme["dim"])
            return

        table = Table(
            border_style=theme["panel_border"], show_lines=False, padding=(0, 1)
        )
        table.add_column("#", style=theme["dim"], width=4, justify="center")
        table.add_column("Title", style="bold")
        table.add_column("Date", style=theme["info"])
        table.add_column("Snippet", style=theme["dim"])

        for i, note in enumerate(self.notes, start=1):
            snippet = note["body"][:40] + ("..." if len(note["body"]) > 40 else "")
            table.add_row(str(i), note["title"], note["created_at"], snippet)

        console.print(table)

    def _search_notes(self, theme: dict[str, Any]) -> None:
        """Search notes by keyword."""
        keyword = Prompt.ask("Search keyword").strip().lower()
        if not keyword:
            return

        results = []
        for note in self.notes:
            if keyword in note["title"].lower() or keyword in note["body"].lower():
                results.append(note)

        console.clear()
        console.rule(f"Search results for '{keyword}'", style=theme["info"])
        if not results:
            console.print("No matches found.", style=theme["dim"])
        else:
            for i, note in enumerate(results, start=1):
                console.print(
                    f"[{theme['info']}]{i}[/] [bold]{note['title']}[/] "
                    f"({note['created_at']})"
                )
                if note["body"]:
                    console.print(f"   {note['body']}", style=theme["dim"])
                console.print()
        Prompt.ask("Press Enter", default="")

    def _delete_notes(self, theme: dict[str, Any]) -> None:
        """Delete notes by row numbers."""
        if not self.notes:
            console.print("No notes to delete.", style=theme["dim"])
            Prompt.ask("Press Enter", default="")
            return

        raw = Prompt.ask("Row numbers to delete (space-separated)")
        try:
            numbers = [int(x) for x in raw.split()]
        except ValueError:
            console.print(f"[{theme['error']}]Invalid input.[/{theme['error']}]")
            Prompt.ask("Press Enter", default="")
            return

        # حذف به ترتیب نزولی برای جلوگیری از تغییر ایندکس
        for num in sorted(numbers, reverse=True):
            if 1 <= num <= len(self.notes):
                del self.notes[num - 1]

        self._save()
        console.print(f"[{theme['success']}]Notes deleted.[/{theme['success']}]")
        Prompt.ask("Press Enter", default="")

    def _export_notes(self, theme: dict[str, Any]) -> None:
        """Export notes to Desktop."""
        fmt = Prompt.ask(
            "Format (json/csv/txt)", choices=["json", "csv", "txt"], default="json"
        )
        desktop = Path.home() / "Desktop"
        filename = f"notes_export.{fmt}"
        filepath = desktop / filename

        if fmt == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "Body", "Created"])
                for note in self.notes:
                    writer.writerow([note["title"], note["body"], note["created_at"]])
        else:  # txt
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("QUICK NOTES EXPORT\n")
                f.write("=" * 40 + "\n")
                for note in self.notes:
                    f.write(f"{note['title']}  ({note['created_at']})\n")
                    if note["body"]:
                        f.write(f"  {note['body']}\n")
                    f.write("\n")

        console.print(
            f"[{theme['success']}]Exported to {filepath}[/{theme['success']}]"
        )
        Prompt.ask("Press Enter", default="")
