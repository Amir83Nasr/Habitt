"""Data model for a todo item."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from habitt.core.jalali_helper import now_shamsi_str


@dataclass
class TodoItem:
    title: str
    done: bool = False
    tag: str | None = None
    created_at: str = field(default_factory=now_shamsi_str)
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "tag": self.tag,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TodoItem:
        item = cls(
            title=data["title"],
            done=data.get("done", False),
            tag=data.get("tag"),
            created_at=data.get("created_at", ""),
        )
        item.id = data.get("id", "")
        return item
