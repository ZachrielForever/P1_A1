#!/usr/bin/env python
# video_diffusor_tui.py

from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, RichLog

class VideoDiffusorPane(Container):
    """The TUI pane for generating video with a diffusion model."""

    def compose(self):
        self.add_class("video_diffusor_pane")
        with Container(id="info_box", classes="title-info-box"):
            yield Static("[b]Video Diffusion[/b]\nModel: ", id="info_content")
        with Horizontal(id="main_content_area"):
            with Container(id="component_settings_box", classes="settings-box"):
                yield Static("[b]Components[/b]", classes="box_header")
                yield Static("", id="component_settings_content")
            yield RichLog(id="status_display_box", classes="output-box", highlight=True)
            with Container(id="numerical_settings_box", classes="settings-box"):
                yield Static("[b]Parameters[/b]", classes="box_header")
                yield Static("", id="numerical_settings_content")
        with Horizontal(id="prompt_area"):
            yield Input(placeholder="Positive Prompt...", id="positive_prompt_box", classes="prompt-box")
            yield Input(placeholder="Negative Prompt...", id="negative_prompt_box", classes="prompt-box")
