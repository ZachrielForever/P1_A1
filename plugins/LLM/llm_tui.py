# llm_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog, Select
from textual.app import ComposeResult
from textual import on
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_logic import LlmPlugin

class LLMChatPane(Container):
    """
    The TUI pane for interacting with the LLM chat model.
    """

    DEFAULT_CSS = """
    .param-row {
        width: 1fr;
    }
    .param-group {
        width: 1fr;
        margin-right: 1;
    }
    .setting_label {
        width: 1fr;
        padding-left: 1;
        padding-top: 1;
    }
    .setting_input_small {
        width: 1fr;
    }
    #main_content_area {
        height: 1fr;
    }
    #chat_log_container {
        width: 2fr;
    }
    #right_panel {
        width: 1fr;
        margin-left: 1;
    }
    .box_header.with_margin {
        margin-top: 1;
    }
    """

    def __init__(self, logic: "LlmPlugin", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """
        Create the layout for the LLM chat pane.
        """
        self.add_class("llm_chat_pane")

        with Horizontal(id="main_content_area"):
            # Left side: Chat log (2/3 width)
            with Container(id="chat_log_container"):
                yield RichLog(id="chat_log", classes="output-box", highlight=True)

            # Right side: Parameters and Model Info (1/3 width)
            with Vertical(id="right_panel", classes="settings-box"):
                yield Static("[b]Parameters[/b]", classes="box_header")
                with Horizontal(classes="param-row"):
                    with Vertical(classes="param-group"):
                        yield Static("Temperature:", classes="setting_label")
                        yield Input(value="0.7", id="temperature_input", classes="setting_input_small")
                    with Vertical(classes="param-group"):
                        yield Static("Top K:", classes="setting_label")
                        yield Input(value="40", id="top_k_input", classes="setting_input_small")
                    with Vertical(classes="param-group"):
                        yield Static("Top P:", classes="setting_label")
                        yield Input(value="0.9", id="top_p_input", classes="setting_input_small")
                with Horizontal(classes="param-row"):
                    with Vertical(classes="param-group"):
                        yield Static("Max Output Tokens:", classes="setting_label")
                        yield Input(value="512", id="max_output_tokens_input", classes="setting_input_small")

                # Placeholder for model info, now with a CSS class for margin
                yield Static("[b]Model Info[/b]", classes="box_header with_margin")
                yield Static("Model: [i]Not Loaded[/i]", id="model_info_static")
                yield Static("Status: [i]Idle[/i]", id="status_static")

        # Bottom section: User input field
        yield Input(placeholder="Ask me anything...", id="input_box", classes="prompt-box")
