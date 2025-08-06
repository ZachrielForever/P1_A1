# video_diffusor_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog, Button
from textual.app import ComposeResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .video_diffusor_logic import VideoDiffusorLogic

class VideoDiffusorPane(Container):
    """
    The TUI pane for the video diffusion model.
    """
    def __init__(self, logic: "VideoDiffusorLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """Create the layout for the Video Diffusor pane."""
        self.add_class("video_diffusor_pane")

        with Vertical(id="main_layout"):
            with Horizontal(id="settings_area"):
                with Vertical(classes="settings-group"):
                    yield Static("[b]Settings[/b]", classes="box_header")
                    yield Static("Frames:", classes="setting_label")
                    yield Input(value="16", id="video_num_frames_input", classes="setting_input_small")
                    yield Static("Steps:", classes="setting_label")
                    yield Input(value="50", id="video_num_inference_steps_input", classes="setting_input_small")
                    yield Static("CFG:", classes="setting_label")
                    yield Input(value="7.5", id="video_guidance_scale_input", classes="setting_input_small")

            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log", highlight=True, markup=True)

            yield Input(placeholder="Describe the video you want to generate...", id="input_box", classes="prompt-box")
