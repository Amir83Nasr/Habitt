"""Shared fixtures that redirect all Habitt file paths to a temp directory."""

import tempfile
import warnings
from pathlib import Path

import pytest

import habitt.core.backup as backup_mod
import habitt.core.config as config_mod

warnings.filterwarnings("ignore", category=DeprecationWarning, module="jdatetime")


@pytest.fixture
def temp_data_dir(monkeypatch):
    """
    Create a temporary directory and make habitt use it
    for data and config files during tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Redirect config
        monkeypatch.setattr(config_mod, "get_data_dir", lambda: tmp)
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp / "config.json")

        # Redirect backup
        monkeypatch.setattr(backup_mod, "get_data_dir", lambda: tmp)

        # Ensure the temp data dir exists
        tmp.mkdir(parents=True, exist_ok=True)

        yield tmp
