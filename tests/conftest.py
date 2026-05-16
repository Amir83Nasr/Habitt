"""Shared fixtures that redirect all Habitt file paths to a temp directory."""

import tempfile
import warnings
from pathlib import Path

import pytest

import habitt.core.backup as backup_mod
import habitt.core.config as config_mod
import habitt.core.focus_config as focus_config_mod

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

        # Redirect focus_config
        # focus_config uses a function now; if you changed it to _focus_config_file(),
        # monkeypatch that function or setattr on focus_config_mod.get_data_dir
        monkeypatch.setattr(focus_config_mod, "get_data_dir", lambda: tmp)

        # Ensure the temp data dir exists
        tmp.mkdir(parents=True, exist_ok=True)

        yield tmp
