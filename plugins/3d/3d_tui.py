#!/usr/bin/env python
# 3d_model_tui.py

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog

class ThreeDModelPane(Container):
    """The TUI pane for generating 3D models."""

    def compose(self):
        """Create the layout for the 3D Model pane."""

        self.add_class("threed_model_pane")

        with Vertical(id="main_layout"):

            # Top half for input and settings
            with Horizontal(id="input_area"):
                yield Input(placeholder="Enter a 3D model description (e.g., a low-poly treasure chest)...", id="prompt_input", classes="prompt-box")

                with Container(id="settings_box", classes="settings-box"):
                    yield Static("[b]Settings[/b]", classes="box_header")
                    yield Static("Model: Shap-E\nFormat: .glb\nDetail: Medium", id="settings_content")
                    yield Static("\n[b]Navigation[/b]", classes="box_header")
                    yield Static("1: Return to LLM", id="navigation_content")

            # Bottom half for status and output
            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log", highlight=True, markup=True)
