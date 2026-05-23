from dataclasses import dataclass, field
from typing import Any

from habitt.core.jalali_helper import now_shamsi_str, today_shamsi_str


@dataclass
class TodoItem:
    title: str
    done: bool = False
    tag: str | None = None
    created_at: str = field(default_factory=now_shamsi_str)
    date: str = field(default_factory=today_shamsi_str)  # جدید
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "tag": self.tag,
            "created_at": self.created_at,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TodoItem":
        item = cls(
            title=data["title"],
            done=data.get("done", False),
            tag=data.get("tag"),
            created_at=data.get("created_at", ""),
            date=data.get("date", ""),
        )
        item.id = data.get("id", "")
        # If date is missing for old tasks, fill with today (or empty)
        if not item.date:
            item.date = today_shamsi_str()
        return item
