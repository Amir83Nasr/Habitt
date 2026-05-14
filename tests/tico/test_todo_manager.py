"""Tests for TodoManager."""

from habitt.tico.todo_manager import TodoManager


def test_add_item(temp_data_dir):
    manager = TodoManager()
    item = manager.add("Buy milk", tag="personal")
    assert item.title == "Buy milk"
    assert item.tag == "personal"
    assert item.done is False
    assert len(manager.items) == 1


def test_remove_item(temp_data_dir):
    manager = TodoManager()
    item = manager.add("Test")
    removed = manager.remove(item.id)
    assert removed is True
    assert len(manager.items) == 0


def test_remove_nonexistent(temp_data_dir):
    manager = TodoManager()
    assert manager.remove("fake") is False


def test_toggle_done(temp_data_dir):
    manager = TodoManager()
    item = manager.add("Task")
    toggled = manager.toggle(item.id)
    assert toggled is not None
    assert toggled.done is True

    toggled = manager.toggle(item.id)
    assert toggled.done is False


def test_list_all(temp_data_dir):
    manager = TodoManager()
    manager.add("Task 1", tag="work")
    manager.add("Task 2", tag="personal")
    manager.add("Task 3", tag="work")
    # Mark one done
    manager.toggle(manager.items[0].id)

    all_items = manager.list_all()
    assert len(all_items) == 3

    # Filter by tag
    work_items = manager.list_all(tag="work")
    assert len(work_items) == 2

    # Exclude done
    open_items = manager.list_all(include_done=False)
    assert len(open_items) == 2  # first one is done


def test_get_by_id(temp_data_dir):
    manager = TodoManager()
    item = manager.add("Find me")
    found = manager.get_by_id(item.id)
    assert found.title == "Find me"
    assert manager.get_by_id("nope") is None
