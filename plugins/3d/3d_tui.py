# 3d_model_tui.py

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog
from textual.app import ComposeResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .threed_logic import ThreeDLogic

class ThreeDModelPane(Container):
    """The TUI pane for generating 3D models."""
    def __init__(self, logic: "ThreeDLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """Create the layout for the 3D Model pane."""
        self.add_class("threed_model_pane")

        with Vertical(id="main_layout"):
            # Top half for input and settings
            with Horizontal(id="input_area"):
                yield Input(placeholder="Enter a 3D model description...", id="input_box", classes="prompt-box")

                with Container(id="settings_box", classes="settings-box"):
                    yield Static("[b]Settings[/b]", classes="box_header")
                    yield Static("Steps:", classes="setting_label")
                    yield Input(value="50", id="threed_num_inference_steps_input", classes="setting_input")
                    yield Static("CFG:", classes="setting_label")
                    yield Input(value="7.5", id="threed_guidance_scale_input", classes="setting_input")

            # Bottom half for status and output
            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log", highlight=True, markup=True)
