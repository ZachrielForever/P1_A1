#!/usr/bin/env python
# main.py

import os
import sys
from llama_cpp import Llama
import torch

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog, RadioSet, RadioButton

# --- TUI Pane Definitions ---
# All TUI layouts are now defined as classes within this single file

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

class InterrogatorPane(Container):
    """The TUI pane for the Image-to-Text Interrogator."""
    def compose(self):
        self.add_class("interrogator_pane")
        with Horizontal(id="main_layout"):
            with Container(id="input_box_container", classes="input-box"):
                yield Static("Load Image...", classes="placeholder_text")
            with Container(id="output_box_container", classes="output-box"):
                yield RichLog(id="text_output_box", wrap=True)
            with Container(id="settings_box_container", classes="settings-box"):
                yield Static("[b]Settings[/b]", classes="box_header")

class ImageUtilitiesPane(Container):
    """The TUI pane for upscaling or restoring images."""
    def compose(self):
        self.add_class("image_utilities_pane")
        with Horizontal(id="main_layout"):
            with Container(id="input_box_container", classes="input-box"):
                yield Static("Load Image...", classes="placeholder_text")
            with Container(id="settings_box_container", classes="settings-box"):
                yield Static("[b]Process[/b]", classes="box_header")
                with RadioSet():
                    yield RadioButton("Upscale", value=True)
                    yield RadioButton("Face Restore")
            with Container(id="output_box_container", classes="output-box"):
                yield Static("Result will appear here.", classes="placeholder_text")

class VideoDiffusorPane(Container):
    """The TUI pane for the Video Diffusor."""
    def compose(self):
        self.add_class("video_diffusor_pane")
        with Vertical(id="main_layout"):
            with Container(id="title_info_box", classes="title-info-box"):
                yield Static("[b]Video Diffusion[/b]\nModel: AnimateDiff")
            with Horizontal(id="main_content_area"):
                with Container(id="component_settings_box", classes="settings-box"):
                    yield Static("[b]Components[/b]", classes="box_header")
                with Container(id="image_display_box", classes="output-box"):
                    yield Static("Status updates will appear here.", classes="placeholder_text")
                with Container(id="numerical_settings_box", classes="settings-box"):
                    yield Static("[b]Parameters[/b]", classes="box_header")
            with Horizontal(id="prompt_area"):
                yield Input(placeholder="Positive Prompt...", id="positive_prompt_box", classes="prompt-box")
                yield Input(placeholder="Negative Prompt...", id="negative_prompt_box", classes="prompt-box")

class SoundAIPane(Container):
    """The TUI pane for the Sound AI."""
    def compose(self):
        self.add_class("sound_ai_pane")
        with Vertical(id="main_layout"):
            with Horizontal(id="input_area"):
                yield Input(placeholder="Enter a sound description...", id="prompt_input", classes="prompt-box")
                with Container(id="settings_box", classes="settings-box"):
                    yield Static("[b]Settings[/b]", classes="box_header")
            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log")

class ThreeDModelPane(Container):
    """The TUI pane for the 3D Model generator."""
    def compose(self):
        self.add_class("threed_model_pane")
        with Vertical(id="main_layout"):
            with Horizontal(id="input_area"):
                yield Input(placeholder="Enter a 3D model description...", id="prompt_input", classes="prompt-box")
                with Container(id="settings_box", classes="settings-box"):
                    yield Static("[b]Settings[/b]", classes="box_header")
            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log")


# --- Main Application Class ---

class AI_Toolkit_App(App):
    """The main application shell for the AI Toolkit."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "load_pane('llm')", "LLM"),
        ("2", "load_pane('diffusor')", "Image"),
        ("3", "load_pane('interrogator')", "Describe"),
        ("4", "load_pane('image_utils')", "Image Utils"),
        ("5", "load_pane('video')", "Video"),
        ("6", "load_pane('sound')", "Sound"),
        ("7", "load_pane('3d')", "3D"),
    ]

    CSS = """
    Screen { layout: vertical; }
    Header { background: purple; }
    #main_container { layout: vertical; }

    /* Global Component Styles */
    .settings-box { border: round green; padding: 0 1; }
    .prompt-box { border: round blue; }
    .output-box { border: round red; }
    .input-box { border: round cyan; }
    .info-box { border: round yellow; padding: 0 1; }
    .title-info-box { border: round white; padding: 1; text-align: center; }
    .box_header { content-align: center top; width: 100%; padding-top: 1; }
    .placeholder_text { content-align: center middle; width: 100%; height: 100%; }

    /* LLM Pane */
    .llm_pane { background: #282a36; padding: 1 2; }
    .llm_pane #main_layout { layout: horizontal; }
    .llm_pane #left_column { width: 2fr; padding-right: 1; layout: vertical; }
    .llm_pane #right_column { width: 1fr; layout: vertical; }
    .llm_pane #response_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #input_box { height: 3; }
    .llm_pane #settings_box { height: 1fr; margin-bottom: 1; }
    .llm_pane #info_box { height: 1fr; }

    /* Diffusor Pane */
    .diffusor_pane { layout: vertical; background: #3b4252; padding: 1 2; }
    .diffusor_pane #title_info_box { height: 3; margin-bottom: 1; }
    .diffusor_pane #main_content_area { height: 1fr; layout: horizontal; margin-bottom: 1; }
    .diffusor_pane #prompt_area { height: 3; layout: horizontal; }
    .diffusor_pane #component_settings_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #image_display_box { width: 2fr; }
    .diffusor_pane #numerical_settings_box { width: 1fr; margin-left: 1; }
    .diffusor_pane #positive_prompt_box { width: 1fr; margin-right: 1; }
    .diffusor_pane #negative_prompt_box { width: 1fr; }

    /* Interrogator Pane */
    .interrogator_pane { background: #2E3440; padding: 1 2; }
    .interrogator_pane #main_layout { layout: horizontal; }
    .interrogator_pane #input_box_container { width: 1fr; margin-right: 1; }
    .interrogator_pane #output_box_container { width: 2fr; margin-right: 1; }
    .interrogator_pane #settings_box_container { width: 1fr; }

    /* Image Utilities Pane */
    .image_utilities_pane { background: #2E3440; padding: 1 2; }
    .image_utilities_pane #main_layout { layout: horizontal; }
    .image_utilities_pane #input_box_container { width: 2fr; margin-right: 1; }
    .image_utilities_pane #settings_box_container { width: 1fr; margin-right: 1; }
    .image_utilities_pane #output_box_container { width: 2fr; }

    /* Video Diffusor Pane */
    .video_diffusor_pane { layout: vertical; background: #3b4252; padding: 1 2; }
    .video_diffusor_pane #title_info_box { height: 3; margin-bottom: 1; }
    .video_diffusor_pane #main_content_area { height: 1fr; layout: horizontal; margin-bottom: 1; }
    .video_diffusor_pane #prompt_area { height: 3; layout: horizontal; }
    .video_diffusor_pane #component_settings_box { width: 1fr; margin-right: 1; }
    .video_diffusor_pane #image_display_box { width: 2fr; }
    .video_diffusor_pane #numerical_settings_box { width: 1fr; margin-left: 1; }
    .video_diffusor_pane #positive_prompt_box { width: 1fr; margin-right: 1; }
    .video_diffusor_pane #negative_prompt_box { width: 1fr; }

    /* Sound & 3D Panes */
    .sound_ai_pane, .threed_model_pane { background: #434C5E; padding: 1 2; layout: vertical; }
    .sound_ai_pane #input_area, .threed_model_pane #input_area { height: 3; layout: horizontal; margin-bottom: 1; }
    .sound_ai_pane #prompt_input, .threed_model_pane #prompt_input { width: 2fr; margin-right: 1; }
    .sound_ai_pane #settings_box, .threed_model_pane #settings_box { width: 1fr; }
    .sound_ai_pane #status_area, .threed_model_pane #status_area { height: 1fr; }
    """

    # A dictionary mapping pane names to their TUI classes
    PANE_MAP = {
        "llm": LLMPane,
        "diffusor": DiffusorPane,
        "interrogator": InterrogatorPane,
        "image_utils": ImageUtilitiesPane,
        "video": VideoDiffusorPane,
        "sound": SoundAIPane,
        "3d": ThreeDModelPane,
    }

    def __init__(self):
        super().__init__()
        self.current_model = None
        self.current_model_type = None
        self.default_llm_path = os.path.join(
            os.path.expanduser("~"),
            "Documents/Projects/P1-AI_Interface/models/LLM/gemma-3-1b-it-q4_0.gguf"
        )

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            pass
        yield Footer()

    def on_mount(self) -> None:
        self.title = "AI Toolkit"
        self.sub_title = "v8.3 - Final Fix"
        # Load the LLM pane and model by default on startup
        self.action_load_pane("llm")

    def unload_current_model(self):
        """Unloads whatever model is currently in VRAM."""
        if self.current_model:
            self.notify(f"Unloading {self.current_model_type} model...")
            del self.current_model
            self.current_model = None
            self.current_model_type = None
            torch.cuda.empty_cache()
            self.notify("Model unloaded.")

    def load_llm(self):
        """Loads the default LLM into VRAM and updates the UI."""
        self.unload_current_model()
        self.notify("Loading LLM... This may take a moment.")

        try:
            if not os.path.exists(self.default_llm_path):
                 self.notify(f"Error: Model file not found at {self.default_llm_path}", severity="error")
                 return

            self.current_model = Llama(
                model_path=self.default_llm_path,
                n_gpu_layers=-1,
                verbose=False
            )
            self.current_model_type = "llm"

            metadata = self.current_model.metadata
            model_name = os.path.basename(self.default_llm_path)
            quantization = metadata.get("general.quantization_version", "Unknown")
            if quantization == "Unknown":
                for key in metadata.keys():
                    if 'quantization' in key:
                        quantization = metadata[key]
                        break

            context_length = self.current_model.context_params.n_ctx

            self.call_from_thread(self.update_llm_tui, model_name, quantization, context_length)
            self.notify("LLM loaded successfully!")
        except Exception as e:
            self.notify(f"Failed to load LLM: {e}", severity="error")

    def update_llm_tui(self, model_name, quant, context):
        """Safely updates the Static widgets in the LLM pane."""
        try:
            settings_widget = self.query_one("#settings_content", Static)
            info_widget = self.query_one("#info_content", Static)

            settings_widget.update(f"Model: {model_name}\nTemp: 0.7")
            info_widget.update(f"Quant: {quant}\nContext: {context}")

            self.screen.refresh()

        except Exception as e:
            self.notify(f"Failed to update TUI: {e}", severity="error")

    def run_llm_inference(self, prompt: str):
        """Runs the LLM inference in a background worker thread."""
        if not self.current_model or self.current_model_type != "llm":
            self.notify("LLM not loaded.", severity="error")
            return

        response_box = self.query_one("#response_box", RichLog)

        self.call_from_thread(response_box.write, f"[b]You:[/b] {prompt}")

        full_response = ""
        stream = self.current_model.create_completion(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )
        for output in stream:
            token = output['choices'][0]['text']
            full_response += token
            self.call_from_thread(response_box.write, token)

        self.call_from_thread(response_box.write, "\n---")


    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses Enter in an Input widget."""
        if event.input.id == "input_box":
            prompt = event.value
            if prompt:
                event.input.value = ""
                # --- FIX for crash ---
                # This is the correct way to call a worker with arguments.
                self.run_worker(self.run_llm_inference, prompt, thread=True)


    def _clear_main_container(self):
        container = self.query_one("#main_container")
        for child in list(container.children):
            child.remove()

    def action_load_pane(self, pane_name: str) -> None:
        """Loads a TUI pane into the main container and handles model swapping."""
        PaneClass = self.PANE_MAP.get(pane_name)
        if not PaneClass:
            self.notify(f"Error: Pane '{pane_name}' not found.", severity="error")
            return

        # --- FIX for model reloading ---
        # This is the core "full swap" logic.

        # Unload any model that might be active.
        self.unload_current_model()

        # Display the new UI pane immediately.
        self._clear_main_container()
        self.query_one("#main_container").mount(PaneClass())
        self.sub_title = pane_name.capitalize()

        # Now, load the correct model for the new pane in the background.
        if pane_name == "llm":
            self.run_worker(self.load_llm, thread=True)
        # Placeholder for other models
        # elif pane_name == "diffusor":
        #     self.run_worker(self.load_diffusor, thread=True)
        else:
            # For panes without a dedicated model, just notify the user.
            self.notify(f"Switched to {pane_name.capitalize()} pane. No model loaded.")


def main():
    """Main entry point for the application."""
    app = AI_Toolkit_App()
    app.run()

if __name__ == "__main__":
    main()
