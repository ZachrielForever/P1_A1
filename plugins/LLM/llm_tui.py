#!/usr/bin/env python
# llm_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog

class LLMChatPane(Container):
    """The TUI pane for interacting with a Large Language Model."""

    def compose(self):
        """Create the layout for the LLM pane."""

        self.add_class("llm_pane")

        with Horizontal(id="horizontal_layout"):

            # The main chat area on the left.
            with Vertical(id="left_column"):
                yield RichLog(id="response_box", classes="output-box", wrap=True, highlight=True)
                yield Input(placeholder="Type your message...", id="input_box", classes="prompt-box")

            # The settings panel on the right.
            with Container(id="settings_column", classes="settings-box"):
                yield Static("[b]Relevant Settings[/b]", classes="box_header")
                yield Static("Model: Gemma-3-8B\nTemp: 0.7\nTop-k: 40", id="settings_content")
