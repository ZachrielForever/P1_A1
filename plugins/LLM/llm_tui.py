#!/usr/bin/env python
# llm_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog, Label

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
                yield Static("[b]LLM Settings[/b]", classes="box_header")

                # Model info (will be set dynamically)
                yield Label("Model:")
                yield Static("", id="model_info_content", classes="setting-info")

                # Temperature setting
                yield Label("Temperature:")
                yield Input(value="0.7", id="temperature_input", classes="setting-input")

                # Top-k setting
                yield Label("Top-k:")
                yield Input(value="40", id="top_k_input", classes="setting-input")

                # Top-p setting
                yield Label("Top-p:")
                yield Input(value="0.9", id="top_p_input", classes="setting-input")

                # Max Output Tokens setting
                yield Label("Max Output Tokens:")
                yield Input(value="512", id="max_output_tokens_input", classes="setting-input")
