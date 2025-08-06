#!/usr/bin/env python
# interrogator_tui.py

from textual.containers import Container, Horizontal
from textual.widgets import Static, RichLog

class InterrogatorPane(Container):
    """The TUI pane for the Image-to-Text Interrogator."""

    def compose(self):
        """Create the layout for the Interrogator pane."""
        self.add_class("interrogator_pane")
        with Horizontal(id="main_layout"):
            with Container(id="input_box", classes="input-box"):
                yield Static("", classes="placeholder_text")

            with Container(id="output_box", classes="output-box"):
                yield RichLog(id="text_output", wrap=True)

            with Container(id="settings_box", classes="settings-box"):
                yield Static("[b]Settings[/b]", classes="box_header")
