# interregator_tui.py

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, RichLog, Button, Select
from textual.app import ComposeResult
from textual import on
import os
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .interregator_logic import InterregatorLogic

class InterrogatorPane(Container):
    """The TUI pane for the Image-to-Text Interrogator."""
    DEFAULT_CSS = """
    #main_layout {
        height: 1fr;
    }
    #content_area {
        height: 1fr;
    }
    #file_path_area {
        height: auto;
        padding: 1;
    }
    #output_box {
        width: 2fr;
        height: 1fr;
    }
    #settings_box {
        width: 1fr;
        height: 1fr;
    }
    #image_select_list {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }
    """
    def __init__(self, logic: "InterregatorLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """Create the layout for the Interrogator pane."""
        self.add_class("interrogator_pane")

        with Vertical(id="main_layout"):
            with Horizontal(id="file_path_area"):
                with Vertical(classes="input-group"):
                    yield Static("Directory Path:", classes="setting_label")
                    yield Input(placeholder="e.g. /home/user/images", id="directory_path_input", classes="file_path_input")
                yield Button("Load Directory", id="load_directory_button", classes="action_button")

            with Horizontal(id="content_area"):
                with Vertical(id="output_box", classes="output-box"):
                    yield Static("[b]Generated Caption[/b]", classes="box_header")
                    yield RichLog(id="text_output", wrap=True)

                with Vertical(id="settings_box", classes="settings-box"):
                    yield Static("[b]Select Image[/b]", classes="box_header")
                    yield Select([], id="image_select_list", classes="setting_input")

                    yield Static("\n[b]Settings[/b]", classes="box_header")
                    yield Static("Max New Tokens:", classes="setting_label")
                    yield Input(value="128", id="max_new_tokens_input", classes="setting_input")
                    yield Static("Beam Size:", classes="setting_label")
                    yield Input(value="1", id="beam_size_input", classes="setting_input")

            yield Input(placeholder="Prompt (optional, for conditional interrogation)...", id="input_box", classes="prompt-box")

    @on(Button.Pressed, "#load_directory_button")
    def on_load_directory_button_pressed(self, event: Button.Pressed) -> None:
        """Loads a list of image files from the specified directory and populates the Select widget."""
        directory_path = self.query_one("#directory_path_input", Input).value

        if not os.path.isdir(directory_path):
            self.notify(f"Error: Directory not found: {directory_path}", severity="error")
            return

        try:
            image_extensions = (".png", ".jpg", ".jpeg")
            image_files: List[str] = [
                f for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f)) and f.lower().endswith(image_extensions)
            ]

            options = [(file, file) for file in image_files]

            self.query_one("#image_select_list", Select).set_options(options)
            self.notify(f"Loaded {len(image_files)} image(s) from {directory_path}", severity="information")

        except Exception as e:
            self.notify(f"Failed to read directory: {e}", severity="error")

    @on(Select.Changed, "#image_select_list")
    def on_image_selected(self, event: Select.Changed) -> None:
        """Placeholder for handling when a file is selected from the list."""
        self.notify(f"Image selected: {event.value}")
