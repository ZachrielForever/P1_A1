#!/usr/bin/env python
# main.py

import os
import sys
import importlib.util
from functools import partial
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog, RadioSet, RadioButton

from model_manager import PluginManager

# --- TUI Pane Definitions (for demonstration purposes, these would be in plugins/*/*.py) ---
class LLMPane(Container):
    """The TUI pane for the LLM."""
    def compose(self):
        self.add_class("llm_pane")
        with Horizontal(id="main_layout"):
            with Vertical(id="left_column"):
                yield RichLog(id="response_box", classes="output-box", wrap=True, highlight=True)
                yield Input(placeholder="Type your message...", id="input_box", classes="prompt-box")
            with Vertical(id="right_column"):
                with Container(id="settings_box", classes="settings-box"):
                    yield Static("[b]Settings[/b]", classes="box_header")
                    yield Static("Model: (loading...)\nTemp: 0.7", id="settings_content")
                with Container(id="info_box", classes="info-box"):
                    yield Static("[b]Model Info[/b]", classes="box_header")
                    yield Static("Quant: (n/a)\nContext: (n/a)", id="info_content")

class DiffusorPane(Container):
    """The TUI pane for the Image Diffusor."""
    def compose(self):
        self.add_class("diffusor_pane")
        with Vertical(id="main_layout"):
            with Container(id="title_info_box", classes="title-info-box"):
                yield Static("[b]Image Diffusion[/b]\nModel: (None Loaded)")
            with Horizontal(id="main_content_area"):
                with Container(id="component_settings_box", classes="settings-box"):
                    yield Static("[b]Components[/b]", classes="box_header")
                with Container(id="image_display_box", classes="output-box"):
                    yield Static("Status updates and image will appear here.", classes="placeholder_text")
                with Container(id="numerical_settings_box", classes="settings-box"):
                    yield Static("[b]Parameters[/b]", classes="box_header")
            with Horizontal(id="prompt_area"):
                yield Input(placeholder="Positive Prompt...", id="positive_prompt_box", classes="prompt-box")
                yield Input(placeholder="Negative Prompt...", id="negative_prompt_box", classes="prompt-box")

# NOTE: The other panes are omitted here.

class AI_Toolkit_App(App):
    """The main application shell for the AI Toolkit."""

    BINDINGS = []
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

    .llm_pane { background: #282a36; padding: 1 2; }
    .llm_pane #main_layout { layout: horizontal; }
    .llm_pane #left_column { width: 2fr; padding-right: 1; layout: vertical; }
    .llm_pane #right_column { width: 1fr; layout: vertical; }
    .llm_pane #response_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #input_box { height: 3; }
    .llm_pane #settings_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #info_box { height: 1fr; }

    .diffusor_pane { layout: vertical; background: #3b4252; padding: 1 2; }
    .diffusor_pane #title_info_box { height: 3; margin-bottom: 1; }
    .diffusor_pane #main_content_area { height: 1fr; layout: horizontal; margin-bottom: 1; }
    .diffusor_pane #prompt_area { height: 3; layout: horizontal; }
    .diffusor_pane #component_settings_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #image_display_box { width: 2fr; }
    .diffusor_pane #numerical_settings_box { width: 1fr; margin-left: 1; }
    .diffusor_pane #positive_prompt_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #negative_prompt_box { width: 1fr; }
    """

    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self._generate_bindings_and_panes()

    def _generate_bindings_and_panes(self):
        self.BINDINGS = []
        self.PANE_CLASSES = {}
        for hotkey, plugin_info in self.plugin_manager.plugins.items():
            pane_name = plugin_info["name"].lower().replace(' ', '_')
            description = plugin_info.get("description", pane_name)

            self.BINDINGS.append((hotkey, f"load_pane('{hotkey}')", description))
            tui_class = self.plugin_manager.get_plugin_tui(hotkey)
            if tui_class:
                self.PANE_CLASSES[hotkey] = tui_class

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            pass
        yield Footer()

    def on_mount(self) -> None:
        self.title = "AI Toolkit"
        self.sub_title = "v8.3 - Final Fix"
        first_plugin_key = next(iter(self.plugin_manager.plugins.keys()), None)
        if first_plugin_key:
            self.action_load_pane(first_plugin_key)

    def action_load_pane(self, hotkey: str) -> None:
        PaneClass = self.PANE_CLASSES.get(hotkey)
        if not PaneClass:
            self.notify(f"Error: Pane for hotkey '{hotkey}' not found.", severity="error")
            return

        self._clear_main_container()
        self.query_one("#main_container").mount(PaneClass())
        self.sub_title = self.plugin_manager.plugins.get(hotkey, {}).get("name", "Unknown Pane")
        self.notify(f"Switched to {self.sub_title} pane.")

    # --- Other methods from the original main.py would be placed here ---
    def unload_current_model(self):
        """Unloads whatever model is currently in VRAM."""
        # Your original method logic goes here.
        pass

    def load_llm(self):
        """Loads the default LLM into VRAM and updates the UI."""
        # Your original method logic goes here.
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Your original method logic goes here.
        pass

    def _clear_main_container(self):
        container = self.query_one("#main_container")
        for child in list(container.children):
            child.remove()

def main():
    app = AI_Toolkit_App()
    app.run()

if __name__ == "__main__":
    main()
