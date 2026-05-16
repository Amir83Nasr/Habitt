"""Tests for plugin system."""


from habitt.core.plugin_base import PluginBase, _scan_directory, discover_plugins


class FakePlugin(PluginBase):
    name = "fake"
    description = "a fake plugin"

    def run_tui(self):
        pass


def test_scan_directory(tmp_path):
    # Create a fake plugin directory
    plugin_dir = tmp_path / "fakedir"
    plugin_dir.mkdir()
    init_file = plugin_dir / "__init__.py"
    init_file.write_text("""
from habitt.core.plugin_base import PluginBase
class TestPlugin(PluginBase):
    name = "test"
    description = "desc"
    def run_tui(self):
        pass
""")
    plugins = _scan_directory(tmp_path)
    assert len(plugins) == 1
    assert plugins[0].name == "test"


def test_scan_empty_dir(tmp_path):
    plugins = _scan_directory(tmp_path)
    assert plugins == []


def test_discover_plugins(tmp_path, monkeypatch):
    user = tmp_path / "user"
    builtin = tmp_path / "builtin"
    user.mkdir()
    builtin.mkdir()
    # Add one plugin in user dir
    (user / "pluginA").mkdir()
    (user / "pluginA" / "__init__.py").write_text("""
from habitt.core.plugin_base import PluginBase
class PluginA(PluginBase):
    name = "A"
    description = ""
    def run_tui(self):
        pass
""")
    plugins = discover_plugins(user, builtin)
    assert len(plugins) == 1
