# sound_tui.py

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog, Button
from textual.app import ComposeResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sound_logic import SoundLogic

class SoundPane(Container):
    """
    The TUI pane for sound-related functions.
    """
    def __init__(self, logic: "SoundLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """Create the layout for the Sound pane."""
        self.add_class("sound_pane")

        with Vertical(id="main_layout"):
            with Horizontal(id="settings_area"):
                with Vertical(classes="settings-group"):
                    yield Static("[b]Settings[/b]", classes="box_header")
                    yield Static("Duration (s):", classes="setting_label")
                    yield Input(value="5", id="duration_input", classes="setting_input_small")
                    yield Static("Sampling Rate:", classes="setting_label")
                    yield Input(value="44100", id="sampling_rate_input", classes="setting_input_small")

            with Container(id="status_area", classes="output-box"):
                yield RichLog(id="status_log", highlight=True, markup=True)

            yield Input(placeholder="Describe the sound you want to generate...", id="input_box", classes="prompt-box")
