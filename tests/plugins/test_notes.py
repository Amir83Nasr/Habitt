"""Tests for notes plugin."""

from habitt.plugins.notes import NotesPlugin


def test_add_note(temp_data_dir, monkeypatch):
    import habitt.plugins.notes as notes_mod

    monkeypatch.setattr(notes_mod, "NOTES_DIR", temp_data_dir / "notes_plugin")
    monkeypatch.setattr(
        notes_mod, "NOTES_FILE", temp_data_dir / "notes_plugin" / "notes.json"
    )
    plugin = NotesPlugin()
    # دستی یه یادداشت اضافه کن
    plugin.notes = [{"title": "Test", "body": "hello", "created_at": "now"}]
    plugin._save()
    # حالا یه نمونهٔ جدید بساز و ببین داده‌ها لود شدن
    plugin2 = NotesPlugin()
    assert len(plugin2.notes) == 1
    assert plugin2.notes[0]["title"] == "Test"
