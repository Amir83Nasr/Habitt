"""Tests for TodoItem model."""

from habitt.tico.models import TodoItem


def test_create_todo():
    item = TodoItem(title="Test")
    assert item.title == "Test"
    assert item.done is False
    assert item.tag is None
    assert item.id == ""
    assert item.created_at  # non empty


def test_to_dict():
    item = TodoItem(title="Buy milk", tag="personal")
    item.id = "abc123"
    d = item.to_dict()
    assert d["title"] == "Buy milk"
    assert d["tag"] == "personal"
    assert d["id"] == "abc123"
    assert not d["done"]


def test_from_dict():
    data = {
        "id": "xyz",
        "title": "Read",
        "done": True,
        "tag": "study",
        "created_at": "1404/08/25",
    }
    item = TodoItem.from_dict(data)
    assert item.id == "xyz"
    assert item.title == "Read"
    assert item.done is True
    assert item.tag == "study"
