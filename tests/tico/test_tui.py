"""Tests for tico TUI helper functions."""

from habitt.core.themes import get_active_theme
from habitt.tico.todo_manager import TodoManager
from habitt.tico.tui import (
    _build_task_table,
    _parse_numbers,
    _render_checkbox,
    _tag_str,
)


def test_render_checkbox_done():
    theme = get_active_theme()
    result = _render_checkbox(True, theme)
    assert "[x]" in result.plain


def test_render_checkbox_open():
    theme = get_active_theme()
    result = _render_checkbox(False, theme)
    assert "[ ]" in result.plain


def test_tag_str_with_tag():
    theme = get_active_theme()
    result = _tag_str("work", theme)
    assert "#work" in result.plain


def test_tag_str_none():
    theme = get_active_theme()
    result = _tag_str(None, theme)
    assert result.plain == ""


def test_parse_numbers_valid():
    assert _parse_numbers("1 3 5", get_active_theme()) == [1, 3, 5]


def test_parse_numbers_invalid():
    result = _parse_numbers("abc", get_active_theme())
    assert result == []


def test_build_task_table(temp_data_dir):
    manager = TodoManager()
    manager.add("Task 1", tag="work")
    manager.add("Task 2", tag="personal")
    table = _build_task_table(manager)
    assert table.row_count == 2  # two rows


def test_build_task_table_filter_by_tag(temp_data_dir):
    manager = TodoManager()
    manager.add("Task 1", tag="work")
    manager.add("Task 2", tag="personal")
    table = _build_task_table(manager, tag="work")
    assert table.row_count == 1
