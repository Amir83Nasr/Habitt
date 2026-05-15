import importlib
import sys
from pathlib import Path
from typing import List


class PluginBase:
    name: str = ""
    description: str = ""

    def run_tui(self) -> None:
        raise NotImplementedError

    def cli(self, args: List[str]) -> None:
        pass


def _scan_directory(plugins_dir: Path) -> List[PluginBase]:
    """Scan one directory for Habitt plugins."""
    plugins = []
    if not plugins_dir.exists():
        return plugins
    for item in sorted(plugins_dir.iterdir()):
        if not item.is_dir():
            continue
        init_file = item / "__init__.py"
        if not init_file.exists():
            continue
        module_name = f"habitt_plugin_{item.name}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, init_file)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginBase)
                    and attr is not PluginBase
                ):
                    instance = attr()
                    plugins.append(instance)
                    break
        except Exception:
            continue
    return plugins


def discover_plugins(user_dir: Path, builtin_dir: Path) -> List[PluginBase]:
    """Discover plugins from both user and built-in directories."""
    plugins = _scan_directory(user_dir)
    plugins += _scan_directory(builtin_dir)
    return plugins
