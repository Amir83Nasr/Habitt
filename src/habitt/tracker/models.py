"""Data model for a logged activity."""

from dataclasses import dataclass, field
from habitt.core.jalali_helper import now_shamsi_str


@dataclass
class Activity:
    title: str
    start_time: str  # Shamsi datetime string
    end_time: str  # Shamsi datetime string
    date: str = ""  # Shamsi date extracted from start_time
    id: str = ""

    def __post_init__(self):
        if not self.date:
            # date part is YYYY/MM/DD
            self.date = self.start_time.split()[0]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Activity":
        return cls(
            id=data.get("id", ""),
            title=data["title"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            date=data.get("date", ""),
        )
