"""Tests for automatic backup."""


from habitt.core.backup import MAX_BACKUPS, backup_file


def test_backup_creates_file(temp_data_dir):
    file = temp_data_dir / "test.json"
    file.write_text("data")
    backup_file(file)
    backup_dir = temp_data_dir / "backups"
    assert backup_dir.exists()
    backups = list(backup_dir.glob("test_*.json"))
    assert len(backups) == 1


def test_backup_limit(temp_data_dir):
    file = temp_data_dir / "test.json"
    file.write_text("data")
    # create more than MAX_BACKUPS
    for i in range(15):
        file.write_text(f"data{i}")
        backup_file(file)
    backup_dir = temp_data_dir / "backups"
    backups = sorted(backup_dir.glob("test_*.json"), key=lambda p: p.stat().st_mtime)
    assert len(backups) <= MAX_BACKUPS
