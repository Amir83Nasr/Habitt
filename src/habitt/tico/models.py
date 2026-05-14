"""Data model for a todo item."""

from dataclasses import dataclass, field
from typing import Optional

from habitt.core.jalali_helper import now_shamsi_str


@dataclass
class TodoItem:
    title: str
    done: bool = False
    tag: Optional[str] = None
    created_at: str = field(default_factory=now_shamsi_str)
    id: str = ""  # will be set by manager when adding

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "tag": self.tag,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TodoItem":
        item = cls(
            title=data["title"],
            done=data.get("done", False),
            tag=data.get("tag"),
            created_at=data.get("created_at", ""),
        )
        item.id = data.get("id", "")
        return item
