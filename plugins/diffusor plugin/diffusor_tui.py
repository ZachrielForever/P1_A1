#!/usr/bin/env python
# plugins/diffusor_plugin/diffusor_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog

class DiffusorPane(Container):
    """The TUI pane for generating images with a diffusion model."""

    def compose(self):
        """Create the layout for the Diffusor pane."""

        # Add a class to scope the overall theme for this pane.
        self.add_class("diffusor_pane")

        # Top row for title and model info
        with Container(id="info_box", classes="info-box"):
            yield Static("[b]Image Diffusion[/b]\nModel: Stable-Diffusion-v1.5", id="info_content")

        # Middle row with three main columns
        with Horizontal(id="main_content_area"):
            # Left column for component settings
            with Container(id="component_settings_box", classes="settings-box"):
                yield Static("[b]Components[/b]", classes="box_header")
                yield Static("VAE: default\nScheduler: DPM++ 2M\nLoRAs: my_character (0.7)", id="component_settings_content")

            # Center box for status log and final image display
            yield RichLog(id="image_display_box", classes="output-box", highlight=True)

            # Right column for numerical settings
            with Container(id="numerical_settings_box", classes="settings-box"):
                yield Static("[b]Parameters[/b]", classes="box_header")
                yield Static("Seed: -1\nSteps: 25\nCFG: 7.0\nSize: 1024x1024", id="numerical_settings_content")

        # Bottom row for the prompts
        with Horizontal(id="prompt_area"):
            yield Input(placeholder="Positive Prompt...", id="positive_prompt_box", classes="prompt-box")
            yield Input(placeholder="Negative Prompt...", id="negative_prompt_box", classes="prompt-box")
