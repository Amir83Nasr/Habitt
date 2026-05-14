"""Core logic for todo operations."""

import uuid
from typing import List, Optional

from habitt.core.config import TICO_FILE
from habitt.core.storage import load_json, save_json
from habitt.tico.models import TodoItem


class TodoManager:
    def __init__(self) -> None:
        self.items: List[TodoItem] = []
        self._load()

    def _load(self) -> None:
        data = load_json(TICO_FILE)
        self.items = [TodoItem.from_dict(item) for item in data]

    def _save(self) -> None:
        save_json(TICO_FILE, [item.to_dict() for item in self.items])

    def add(self, title: str, tag: Optional[str] = None) -> TodoItem:
        item = TodoItem(title=title, tag=tag)
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

    def toggle(self, item_id: str) -> Optional[TodoItem]:
        for item in self.items:
            if item.id == item_id:
                item.done = not item.done
                self._save()
                return item
        return None

    def list_all(
        self, tag: Optional[str] = None, include_done: bool = True
    ) -> List[TodoItem]:
        result = self.items
        if tag is not None:
            result = [item for item in result if item.tag == tag]
        if not include_done:
            result = [item for item in result if not item.done]
        return result

    def get_by_id(self, item_id: str) -> Optional[TodoItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None
