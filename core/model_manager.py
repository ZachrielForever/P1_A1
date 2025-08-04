#!/usr/bin/env python
# core/model_manager.py

import os
import json
import importlib.util

class PluginManager:
    """Discovers, loads, and manages all available AI plugins."""

    def __init__(self, plugin_folder="plugins"):
        self.plugin_folder = plugin_folder
        self.plugins = {}
        self.scan_plugins()

    def scan_plugins(self):
        """Scans the plugin folder for valid plugins and sorts them."""
        print("Scanning for plugins...")
        discovered_plugins = {}
        for item in os.listdir(self.plugin_folder):
            plugin_path = os.path.join(self.plugin_folder, item)
            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, "plugin.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            hotkey = manifest.get("hotkey")
                            if hotkey:
                                manifest["path"] = plugin_path
                                discovered_plugins[hotkey] = manifest
                                print(f"  - Found plugin: {manifest['name']}")
                    except json.JSONDecodeError:
                        print(f"  - WARNING: Could not parse plugin.json in {plugin_path}")

        # Sort the discovered plugins by their hotkey to ensure consistent order.
        self.plugins = dict(sorted(discovered_plugins.items()))

    def get_plugin_tui(self, hotkey):
        """Dynamically imports and returns the TUI class from a plugin."""
        plugin_info = self.plugins.get(hotkey)
        if not plugin_info:
            return None

        tui_script_path = os.path.join(plugin_info["path"], plugin_info["tui_layout"])
        class_name = plugin_info.get("class_name")
        if not class_name:
            print(f"ERROR: 'class_name' not defined in plugin.json for {plugin_info['name']}")
            return None

        try:
            # This method of loading from a file path is more robust in some environments.
            spec = importlib.util.spec_from_file_location(class_name, tui_script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
        except Exception as e:
            print(f"ERROR: Could not load TUI for {plugin_info['name']}: {e}")
            return None
