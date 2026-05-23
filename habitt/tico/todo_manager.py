"""Core logic for todo operations."""

from __future__ import annotations

import csv
import uuid
from pathlib import Path

from habitt.core.storage import load_json, save_json
from habitt.tico.models import TodoItem


class TodoManager:
    def __init__(self) -> None:
        self.items: list[TodoItem] = []
        self._load()

    def _filepath(self) -> Path:
        from habitt.core.config import get_tico_file

        return get_tico_file()

    def _load(self) -> None:
        data = load_json(self._filepath())
        self.items = [TodoItem.from_dict(item) for item in data]

    def _save(self) -> None:
        save_json(self._filepath(), [item.to_dict() for item in self.items])

    def add(
        self, title: str, tag: str | None = None, date: str | None = None
    ) -> TodoItem:
        item = TodoItem(title=title, tag=tag)
        if date:
            item.date = date
        item.id = uuid.uuid4().hex[:6]
        self.items.append(item)
        self._save()
        return item

    def remove(self, item_id: str) -> bool:
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                self._save()
                return True
        return False

    def toggle(self, item_id: str) -> TodoItem | None:
        for item in self.items:
            if item.id == item_id:
                item.done = not item.done
                self._save()
                return item
        return None

    def list_all(
        self, tag: str | None = None, include_done: bool = True, date: str | None = None
    ) -> list[TodoItem]:
        result = self.items
        if date is not None:
            result = [item for item in result if item.date == date]
        if tag is not None:
            result = [item for item in result if item.tag == tag]
        if not include_done:
            result = [item for item in result if not item.done]
        return result

    def get_by_id(self, item_id: str) -> TodoItem | None:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def available_dates(self) -> list[str]:
        """Return sorted list of unique dates having tasks."""
        dates = sorted({item.date for item in self.items if item.date})
        return dates

    def export_data(self, directory: Path, format: str = "json") -> Path:
        """Export all tasks."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tico_export.{format}"
        filepath = directory / filename
        items = self.list_all()
        if format == "json":
            save_json(filepath, [item.to_dict() for item in items])
        elif format == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Done", "Tag", "Date"])
                for item in items:
                    writer.writerow(
                        [item.id, item.title, item.done, item.tag, item.date]
                    )
        elif format == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("TICO - All Tasks\n")
                f.write("=" * 30 + "\n")
                for item in items:
                    status = "[x]" if item.done else "[ ]"
                    tag_str = f" #{item.tag}" if item.tag else ""
                    f.write(f"{status} {item.title}{tag_str}  ({item.date})\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
        return filepath

    def export_date_data(self, directory: Path, date_str: str, fmt: str) -> Path:
        """Export tasks of a specific date."""
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"tico_{date_str.replace('/', '-')}.{fmt}"
        filepath = directory / filename
        items = self.list_all(date=date_str)
        if fmt == "json":
            save_json(filepath, [item.to_dict() for item in items])
        elif fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Done", "Tag"])
                for item in items:
                    writer.writerow([item.id, item.title, item.done, item.tag])
        elif fmt == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"TICO TASKS - {date_str}\n")
                f.write("=" * 30 + "\n")
                if not items:
                    f.write("No tasks.\n")
                else:
                    for item in items:
                        status = "[x]" if item.done else "[ ]"
                        tag_str = f" #{item.tag}" if item.tag else ""
                        f.write(f"{status} {item.title}{tag_str}\n")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        return filepath
