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


class ModelSelectionOverlay(Vertical):
    """A translucent overlay for selecting a model."""

    def __init__(self, models: list[str], pane_hotkey: str):
        super().__init__(id="model_selection_overlay")
        self.models = models
        self.pane_hotkey = pane_hotkey
        self.selected_model = None

    def compose(self) -> ComposeResult:
        yield Static("[b]Select a Model[/b]", classes="box_header")
        with RadioSet():
            for model_name in self.models:
                yield RadioButton(model_name)
        with Horizontal(id="overlay_buttons"):
            yield Button("Load", variant="primary", id="load_button")
            yield Button("Cancel", variant="default", id="cancel_button")

    @on(RadioSet.Changed)
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.selected_model = event.pressed.label.plain

    @on(Button.Pressed, "#load_button")
    def on_load_button_pressed(self) -> None:
        if self.selected_model:
            self.app.action_confirm_load(self.pane_hotkey, self.selected_model)
        else:
            self.app.notify("Please select a model first.", severity="warning")

    @on(Button.Pressed, "#cancel_button")
    def on_cancel_button_pressed(self) -> None:
        self.remove()

class AI_Toolkit_App(App):
    """The main application shell for the AI Toolkit."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    PANE_CLASSES = {}

    CSS = """
    Screen { layout: vertical; }
    Header { background: purple; }
    #main_container { layout: vertical; }

    .settings-box { border: round green; padding: 0 1; }
    .prompt-box { border: round blue; }
    .output-box { border: round red; }
    .input-box { border: round cyan; }
    .info-box { border: round yellow; padding: 0 1; }
    .title-info-box { border: round white; padding: 1; text-align: center; }
    .box_header { content-align: center top; width: 100%; padding-top: 1; }
    .placeholder_text { content-align: center middle; width: 100%; height: 100%; }

    .llm_pane { padding: 1 2; }
    .llm_pane #main_layout { layout: horizontal; }
    .llm_pane #left_column { width: 2fr; padding-right: 1; layout: vertical; }
    .llm_pane #right_column { width: 1fr; layout: vertical; }
    .llm_pane #response_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #input_box { height: 3; }
    .llm_pane #settings_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #info_box { height: 1fr; }

    .diffusor_pane { layout: vertical; padding: 1 2; }
    .diffusor_pane #title_info_box { height: 3; margin-bottom: 1; }
    .diffusor_pane #main_content_area { height: 1fr; layout: horizontal; margin-bottom: 1; }
    .diffusor_pane #prompt_area { height: 3; layout: horizontal; }
    .diffusor_pane #component_settings_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #image_display_box { width: 2fr; }
    .diffusor_pane #numerical_settings_box { width: 1fr; margin-left: 1; }
    .diffusor_pane #positive_prompt_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #negative_prompt_box { width: 1fr; }

    #model_selection_overlay {
        width: 60%;
        height: 60%;
        background: $surface;
        border: thick $primary;
        align: center middle;
        text-align: center;
        margin: 0;
        padding: 2;
    }
    #model_selection_overlay Static { margin-bottom: 1; }
    #overlay_buttons { margin-top: 2; width: 100%; align-horizontal: center; }
    #overlay_buttons Button { margin-right: 2; }
    """

    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self.active_logic = None
        self.active_hotkey = None
        self.PANE_CLASSES = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            pass
        yield Footer()

    def on_mount(self) -> None:
        self.title = "AI Toolkit"
        self.sub_title = "v8.10 - CSS Fixes and Transparent Background"
        self._generate_bindings_and_panes()

        first_plugin_key = next(iter(self.plugin_manager.plugins.keys()), None)
        if first_plugin_key:
            self.action_load_pane(first_plugin_key)

    def _generate_bindings_and_panes(self):
        for hotkey, plugin_info in self.plugin_manager.plugins.items():
            pane_name = plugin_info["name"].lower().replace(' ', '_')
            description = plugin_info.get("description", pane_name)
            self.PANE_CLASSES[hotkey] = self.plugin_manager.get_plugin_tui(hotkey)
            self.bind(hotkey, f"load_pane('{hotkey}')", description=description)

    def action_load_pane(self, hotkey: str) -> None:
        if hotkey == self.active_hotkey:
            return

        self._clear_main_container()

        plugin_info = self.plugin_manager.plugins.get(hotkey)
        if plugin_info:
            model_type = plugin_info.get("model_type")
            models = self._get_available_models(model_type)

            if not models:
                self.notify(f"No models found for {model_type} in 'models/{model_type}'", severity="warning")
                self._load_and_mount_pane(hotkey)
            else:
                self.query_one("Screen").mount(ModelSelectionOverlay(models, hotkey))

    def action_confirm_load(self, hotkey: str, model_name: str) -> None:
        self.query_one(ModelSelectionOverlay).remove()

        if self.active_logic:
            self.unload_model_in_background(self.active_logic)

        self.active_hotkey = hotkey
        self.sub_title = self.plugin_manager.plugins.get(hotkey, {}).get("name", "Unknown Pane")
        self.notify(f"Switched to {self.sub_title} pane. Loading '{model_name}'...")

        self._load_and_mount_pane(hotkey)
        self.active_logic = self.plugin_manager.get_plugin_logic(hotkey)

        if self.active_logic and hasattr(self.active_logic, 'load_model'):
            self.run_worker(self.active_logic.load_model, model_name, exclusive=True, thread=True)

    def _load_and_mount_pane(self, hotkey: str) -> None:
        PaneClass = self.PANE_CLASSES.get(hotkey)
        if not PaneClass:
            self.notify(f"Error: Pane for hotkey '{hotkey}' not found.", severity="error")
            return

        self.query_one("#main_container").mount(PaneClass())

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

    @on(Input.Submitted, "#input_box")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.active_logic and hasattr(self.active_logic, 'run_inference'):
            self.run_worker(self.active_logic.run_inference, event.value, exclusive=True, thread=True)
            event.input.value = ""

def main():
    plugin_manager = PluginManager()
    _ensure_dependencies(plugin_manager)
    app = AI_Toolkit_App()
    app.run()

if __name__ == "__main__":
    main()
