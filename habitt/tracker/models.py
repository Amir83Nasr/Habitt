from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Activity:
    title: str
    start_time: str
    end_time: str
    date: str = ""
    id: str = ""

    def __post_init__(self) -> None:  # خط ۱۶
        if not self.date:
            self.date = self.start_time.split()[0]

    def to_dict(self) -> dict[str, Any]:  # خط ۲۱
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Activity:  # خط ۳۱
        return cls(
            id=data.get("id", ""),
            title=data["title"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            date=data.get("date", ""),
        )
