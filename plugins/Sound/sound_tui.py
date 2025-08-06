#!/usr/bin/env python
# sound_ai_tui.py

from textual.containers import Container, Vertical
from textual.widgets import Static, Input, RichLog

class SoundAIPane(Container):
    """The TUI pane for the Sound AI."""

    def compose(self):
        """Create the layout for the Sound AI pane."""

        self.add_class("sound_ai_pane")

        # A simple vertical layout is more robust.
        with Vertical(id="main_layout"):

            with Container(id="input_area", classes="prompt-box"):
                 yield Input(placeholder="Enter a sound description...")

            with Container(id="settings_area", classes="settings-box"):
                yield Static("[b]Settings[/b]", classes="box_header")

            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log")
