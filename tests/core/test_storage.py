"""Tests for JSON storage utilities."""

from habitt.core.storage import load_json, save_json


def test_save_and_load_json(temp_data_dir):
    filepath = temp_data_dir / "test.json"
    data = [{"id": 1, "title": "Test"}]

    save_json(filepath, data)
    loaded = load_json(filepath)

    assert loaded == data


def test_load_missing_file(temp_data_dir):
    filepath = temp_data_dir / "nonexistent.json"
    assert load_json(filepath) == []


def test_load_corrupt_file(temp_data_dir):
    filepath = temp_data_dir / "bad.json"
    filepath.write_text("this is not json")
    assert load_json(filepath) == []
