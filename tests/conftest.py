"""Shared fixtures for all tests."""

import tempfile
from pathlib import Path

import pytest

import habitt.core.config as config


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Redirect DATA_DIR to a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        monkeypatch.setattr(config, "DATA_DIR", tmp)
        monkeypatch.setattr(config, "TICO_FILE", tmp / "tico.json")
        monkeypatch.setattr(config, "TRACKER_FILE", tmp / "tracker.json")
        yield tmp
