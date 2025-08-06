#!/usr/bin/env python
# model_manager.py

import os
import json
import importlib.util
import importlib
import sys

class PluginManager:
    """Manages the discovery and loading of plugins and their dependencies."""

    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = self._discover_plugins()
        self.loaded_plugins = {}
        self.dependencies_root = os.path.join(os.path.dirname(__file__), 'dependencies')


    def _discover_plugins(self):
        plugins = {}
        if not os.path.isdir(self.plugins_dir):
            return plugins

        # Get a list of plugin directories and sort them to ensure consistent ordering
        plugin_dirs = [d for d in os.listdir(self.plugins_dir) if os.path.isdir(os.path.join(self.plugins_dir, d))]
        plugin_dirs.sort()

        for plugin_name in plugin_dirs:
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            config_file = os.path.join(plugin_path, "plugin.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)
                        hotkey = config.get("hotkey")
                        if hotkey:
                            config["plugin_path"] = plugin_path
                            plugins[hotkey] = config
                except (IOError, json.JSONDecodeError) as e:
                    print(f"Error loading plugin config from {config_file}: {e}", file=sys.stderr)

        # Sort the plugins by hotkey to ensure a predictable order
        sorted_plugins = dict(sorted(plugins.items(), key=lambda item: int(item[0]) if item[0].isdigit() else float('inf')))
        return sorted_plugins

    def _add_plugin_dependencies_to_path(self, model_type: str):
        """Adds the specific plugin's dependency path to sys.path."""
        plugin_deps_path = os.path.join(self.dependencies_root, model_type)
        if os.path.exists(plugin_deps_path) and plugin_deps_path not in sys.path:
            sys.path.insert(0, plugin_deps_path)

    def _remove_plugin_dependencies_from_path(self, model_type: str):
        """Removes the specific plugin's dependency path from sys.path."""
        plugin_deps_path = os.path.join(self.dependencies_root, model_type)
        if plugin_deps_path in sys.path:
            sys.path.remove(plugin_deps_path)

    def get_plugin_tui(self, hotkey: str):
        """Loads and returns the TUI class for a given plugin."""
        plugin_info = self.plugins.get(hotkey)
        if not plugin_info:
            return None

        tui_layout_file = plugin_info.get("tui_layout")
        class_name = plugin_info.get("class_name")
        plugin_path = plugin_info.get("plugin_path")
        model_type = plugin_info.get("model_type")

        if not tui_layout_file or not class_name or not plugin_path:
            return None

        # Add plugin-specific dependencies to path before import
        if model_type:
            self._add_plugin_dependencies_to_path(model_type)

        module_path = os.path.join(plugin_path, tui_layout_file)

        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        spec = importlib.util.spec_from_file_location(
            f"plugin_{hotkey}_tui", module_path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"plugin_{hotkey}_tui"] = module
        spec.loader.exec_module(module)

        tui_class = getattr(module, class_name, None)

        # Remove plugin-specific dependencies from path after import
        if model_type:
            self._remove_plugin_dependencies_from_path(model_type)

        return tui_class

    def get_plugin_logic(self, hotkey: str):
        """Loads and returns the logic class for a given plugin."""
        plugin_info = self.plugins.get(hotkey)
        if not plugin_info:
            return None

        if hotkey in self.loaded_plugins:
            return self.loaded_plugins[hotkey]

        logic_file = plugin_info.get("logic_file")
        logic_class = plugin_info.get("logic_class")
        plugin_path = plugin_info.get("plugin_path")
        model_type = plugin_info.get("model_type")

        if not logic_file or not logic_class or not plugin_path:
            return None

        # Add plugin-specific dependencies to path before import
        if model_type:
            self._add_plugin_dependencies_to_path(model_type)

        module_path = os.path.join(plugin_path, logic_file)

        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        spec = importlib.util.spec_from_file_location(
            f"plugin_{hotkey}_logic", module_path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"plugin_{hotkey}_logic"] = module
        spec.loader.exec_module(module)

        logic_class_instance = getattr(module, logic_class)()
        self.loaded_plugins[hotkey] = logic_class_instance

        # Remove plugin-specific dependencies from path after import
        if model_type:
            self._remove_plugin_dependencies_from_path(model_type)

        return logic_class_instance
