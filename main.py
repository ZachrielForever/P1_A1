#!/usr/bin/env python
# main.py

import os
import sys
import subprocess
import importlib.util

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, RichLog, Static, RadioSet, RadioButton, Button
from textual import on
from textual.worker import Worker, WorkerState

from model_manager import PluginManager

def _ensure_dependencies(plugin_manager):
    """
    Checks for and installs dependencies for each plugin into its own folder.
    This prevents dependency version conflicts between plugins.
    """
    dependencies_root = os.path.join(os.path.dirname(__file__), 'dependencies')

    print("Checking for plugin dependencies...")

    plugins = plugin_manager.plugins
    if not plugins:
        print("No plugins found. Skipping dependency check.")
        return

    # Check and install dependencies for each plugin
    for hotkey, plugin_info in plugins.items():
        plugin_path = plugin_info.get("plugin_path")
        model_type = plugin_info.get("model_type")

        # Gracefully handle missing model_type
        if not model_type:
            print(f"Skipping dependency check for plugin '{plugin_info.get('name', hotkey)}' due to missing 'model_type' in plugin.json.")
            continue

        requirements_path = os.path.join(plugin_path, 'requirements.txt')

        if os.path.exists(requirements_path):
            plugin_deps_path = os.path.join(dependencies_root, model_type)
            os.makedirs(plugin_deps_path, exist_ok=True)

            # Simple check to see if the folder is empty
            if not os.listdir(plugin_deps_path):
                print(f"Installing dependencies for '{model_type}'...")
                try:
                    command = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-t",
                        plugin_deps_path,
                        "-r",
                        requirements_path
                    ]

                    subprocess.run(command, check=True)
                    print(f"Dependencies for '{model_type}' installed successfully.")
                except Exception as e:
                    print(f"Error installing dependencies for '{model_type}': {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                print(f"Dependencies for '{model_type}' already exist. Skipping installation.")
        else:
            print(f"No requirements.txt found for '{model_type}'.")


class AI_Toolkit_App(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    PANE_CLASSES = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_manager = PluginManager()
        self.active_plugin_info = None
        self.active_logic = None
        self.active_pane_id = "llm_pane"

    def compose(self) -> ComposeResult:
        with Container(id="app_container"):
            yield Header()
            with Container(id="main_container"):
                yield RichLog() # Temporary placeholder for the log.
            yield Footer()

    def on_mount(self) -> None:
        self.title = "AI Toolkit"
        self.sub_title = "v8.10 - CSS Fixes and Transparent Background"
        self._generate_bindings_and_panes()

        first_plugin_key = next(iter(self.plugin_manager.plugins.keys()), None)
        if first_plugin_key:
            self.action_load_pane(first_plugin_key)

    def _generate_bindings_and_panes(self):
        # Clear existing bindings and panes to prevent duplicates
        self.BINDINGS = [("q", "quit", "Quit")]
        self.PANE_CLASSES = {}

        for hotkey, plugin_info in self.plugin_manager.plugins.items():
            pane_name = plugin_info["name"].lower().replace(' ', '_')
            description = plugin_info.get("description", pane_name)
            self.PANE_CLASSES[hotkey] = self.plugin_manager.get_plugin_tui(hotkey)
            self.bind(hotkey, f"load_pane('{hotkey}')", description=description)

    def action_load_pane(self, hotkey: str) -> None:
        if self.active_plugin_info and self.active_plugin_info['hotkey'] == hotkey:
            return

        PaneClass = self.PANE_CLASSES.get(hotkey)
        if not PaneClass:
            self.notify(f"Error: Pane for hotkey '{hotkey}' not found.", severity="error")
            return

        # Clean up the previous pane and logic
        self._clear_main_container()
        if self.active_logic:
            self.unload_model_in_background(self.active_logic)
            self.active_logic = None

        # Load the new pane and logic
        self.query_one("#main_container").mount(PaneClass())
        self.active_plugin_info = self.plugin_manager.plugins[hotkey]
        self.active_pane_id = self.active_plugin_info['name'].lower().replace(' ', '_').replace('-', '_') + "_pane"
        self.active_logic = self.plugin_manager.get_plugin_logic(hotkey)
        self.title = f"AI Toolkit - {self.active_plugin_info['name']}"

        # Initialize the model in the background
        if self.active_logic and hasattr(self.active_logic, 'load_model'):
            self.run_worker(self.active_logic.load_model, exclusive=True, thread=True)

    def _get_current_settings(self) -> dict:
        """
        Retrieves the current settings from the widgets in the active pane.
        Returns a dictionary of settings or an empty dictionary if no settings are found.
        """
        settings = {}
        active_pane = self.query_one(f"#{self.active_pane_id}")

        # Check for LLM settings
        if active_pane.query_one("#temperature_input", False):
            try:
                settings["temperature"] = float(active_pane.query_one("#temperature_input").value)
                settings["top_k"] = int(active_pane.query_one("#top_k_input").value)
                settings["top_p"] = float(active_pane.query_one("#top_p_input").value)
                settings["max_output_tokens"] = int(active_pane.query_one("#max_output_tokens_input").value)
            except Exception as e:
                self.notify(f"Invalid LLM settings: {e}", severity="error")

        # Check for Image Diffusor settings
        if active_pane.query_one("#num_inference_steps_input", False):
            try:
                settings["num_inference_steps"] = int(active_pane.query_one("#num_inference_steps_input").value)
                settings["guidance_scale"] = float(active_pane.query_one("#guidance_scale_input").value)
                settings["seed"] = int(active_pane.query_one("#seed_input").value)
            except Exception as e:
                self.notify(f"Invalid Image Diffusor settings: {e}", severity="error")

        # Check for Interrogator settings
        if active_pane.query_one("#max_new_tokens_input", False):
            try:
                settings["max_new_tokens"] = int(active_pane.query_one("#max_new_tokens_input").value)
                settings["beam_size"] = int(active_pane.query_one("#beam_size_input").value)
            except Exception as e:
                self.notify(f"Invalid Interrogator settings: {e}", severity="error")

        # Check for Image Utilities settings
        if active_pane.query_one("#upscale_type_radio", False):
            try:
                # Assuming `upscale_type_radio` is the ID of the RadioSet
                upscale_type = active_pane.query_one("#upscale_type_radio").pressed_button.label.plain.lower().replace(" ", "_")
                settings["upscale_type"] = upscale_type
                settings["scale_factor"] = int(active_pane.query_one("#scale_factor_input").value)
            except Exception as e:
                self.notify(f"Invalid Image Utilities settings: {e}", severity="error")

        # Check for Sound AI settings
        if active_pane.query_one("#duration_input", False):
            try:
                settings["duration"] = int(active_pane.query_one("#duration_input").value)
                settings["sampling_rate"] = int(active_pane.query_one("#sampling_rate_input").value)
            except Exception as e:
                self.notify(f"Invalid Sound AI settings: {e}", severity="error")

        # Check for 3D Model settings
        if active_pane.query_one("#3d_num_inference_steps_input", False):
            try:
                settings["num_inference_steps"] = int(active_pane.query_one("#3d_num_inference_steps_input").value)
                settings["guidance_scale"] = float(active_pane.query_one("#3d_guidance_scale_input").value)
            except Exception as e:
                self.notify(f"Invalid 3D Model settings: {e}", severity="error")

        # Check for Video Diffusor settings
        if active_pane.query_one("#video_num_frames_input", False):
            try:
                settings["num_frames"] = int(active_pane.query_one("#video_num_frames_input").value)
                settings["num_inference_steps"] = int(active_pane.query_one("#video_num_inference_steps_input").value)
                settings["guidance_scale"] = float(active_pane.query_one("#video_guidance_scale_input").value)
            except Exception as e:
                self.notify(f"Invalid Video Diffusor settings: {e}", severity="error")

        return settings

    def _get_available_models(self, model_type: str) -> list[str]:
        if not model_type:
            return []
        model_dir = os.path.join(os.getcwd(), 'models', model_type)
        if not os.path.exists(model_dir):
            return []

        models = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
        return models

    def unload_model_in_background(self, logic_instance):
        if logic_instance and hasattr(logic_instance, 'unload_model'):
            self.run_worker(logic_instance.unload_model, exclusive=True, thread=True)

    def _clear_main_container(self):
        container = self.query_one("#main_container")
        for child in list(container.children):
            child.remove()

    @on(Input.Submitted, "Input#input_box")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self.active_logic or not hasattr(self.active_logic, 'run_inference'):
            self.notify("Error: No active plugin logic or run_inference method found.", severity="error")
            return

        user_prompt = event.value
        current_settings = self._get_current_settings()

        # Now pass both the prompt and the settings to the model.
        self.run_worker(self.active_logic.run_inference, user_prompt, current_settings, exclusive=True, thread=True)
        event.input.value = ""

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            print(f"Worker succeeded with result: {event.worker.result}")
        elif event.state == WorkerState.ERROR:
            print(f"Worker failed with error: {event.worker.error}")

if __name__ == "__main__":
    _ensure_dependencies(PluginManager())
    app = AI_Toolkit_App()
    app.run()
