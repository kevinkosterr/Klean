import importlib.metadata
from typing import Dict

from . import FileSystemPlugin


def discover_plugins() -> Dict[str, type[FileSystemPlugin]]:
    plugins = {}

    for entry_point in importlib.metadata.entry_points(group="klean.plugins"):
        plugin = entry_point.load()
        if not issubclass(plugin, FileSystemPlugin):
            continue

        plugins[plugin.name] = plugin

    return plugins
