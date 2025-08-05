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
        """Scans the plugin folder for valid plugins and sorts them by hotkey."""
        print("Scanning for plugins...")
        discovered_plugins = {}
        # Ensure the plugins directory exists before scanning
        if not os.path.isdir(self.plugin_folder):
            print(f"  - WARNING: Plugin directory '{self.plugin_folder}' not found.")
            return

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
                                # Store the plugin's path and manifest
                                manifest["path"] = plugin_path
                                discovered_plugins[hotkey] = manifest
                                print(f"  - Found plugin: {manifest['name']} (Hotkey: '{hotkey}')")
                            else:
                                print(f"  - WARNING: 'hotkey' not found in plugin.json for {item}")
                    except json.JSONDecodeError:
                        print(f"  - WARNING: Could not parse plugin.json in {plugin_path}")

        # Sort the plugins by hotkey for a consistent order in the UI and footer
        self.plugins = dict(sorted(discovered_plugins.items()))
        print("Plugin scan complete.")

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

        if not os.path.exists(tui_script_path):
            print(f"ERROR: TUI layout file not found at {tui_script_path}")
            return None

        return self._dynamic_import(tui_script_path, class_name)

    def get_plugin_logic(self, hotkey):
        """Dynamically imports and returns the logic class from a plugin."""
        plugin_info = self.plugins.get(hotkey)
        if not plugin_info:
            return None

        logic_script_path = os.path.join(plugin_info["path"], plugin_info["logic_file"])
        class_name = plugin_info.get("logic_class_name")

        if not class_name:
            print(f"ERROR: 'logic_class_name' not defined in plugin.json for {plugin_info['name']}")
            return None

        if not os.path.exists(logic_script_path):
            print(f"ERROR: Logic file not found at {logic_script_path}")
            return None

        return self._dynamic_import(logic_script_path, class_name)

    def _dynamic_import(self, file_path, class_name):
        """A helper function to dynamically import a class from a file path."""
        try:
            spec = importlib.util.spec_from_file_location(class_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
        except Exception as e:
            print(f"ERROR: Could not load class '{class_name}' from {file_path}: {e}")
            return None
