"""Tests for menu_utils."""

from unittest.mock import patch

import readchar

from habitt.core.menu_utils import select_from_options


def test_select_with_enter(monkeypatch):
    keys = [readchar.key.ENTER]
    with patch("readchar.readkey", side_effect=keys):
        result = select_from_options([("a", "Option A"), ("b", "Option B")])
    assert result == "a"  # first option


def test_select_down_enter(monkeypatch):
    keys = [readchar.key.DOWN, readchar.key.ENTER]
    with patch("readchar.readkey", side_effect=keys):
        result = select_from_options([("a", "A"), ("b", "B")])
    assert result == "b"


def test_select_direct_key(monkeypatch):
    keys = ["b"]
    with patch("readchar.readkey", side_effect=keys):
        result = select_from_options([("a", "A"), ("b", "B")])
    assert result == "b"


def test_select_cancel(monkeypatch):
    keys = ["q"]
    with patch("readchar.readkey", side_effect=keys):
        result = select_from_options([("a", "A")], cancel_key="q")
    assert result is None


def test_select_empty_list():
    assert select_from_options([]) is None
