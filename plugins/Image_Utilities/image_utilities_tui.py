# image_utilities_tui.py

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, RadioSet, RadioButton, Button, Input, Select
from textual.app import ComposeResult
from textual import on
import os
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .image_utilities_logic import ImageUtilitiesLogic

class ImageUtilitiesPane(Container):
    """The TUI pane for upscaling or restoring images."""

    DEFAULT_CSS = """
    #horizontal_layout {
        height: 1fr;
    }
    #input_column, #settings_box, #output_image_box {
        width: 1fr;
        padding: 1;
    }
    #input_image_box {
        height: 1fr;
        border: solid dodgerblue;
    }
    #result_image_placeholder {
        height: 1fr;
        border: solid dodgerblue;
    }
    .box_header {
        margin-bottom: 1;
    }
    .setting_label {
        margin-top: 1;
    }
    .action_button {
        margin-top: 1;
    }
    """

    def __init__(self, logic: "ImageUtilitiesLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """Create the layout for the Image Utilities pane."""
        self.add_class("image_utilities_pane")

        with Horizontal(id="horizontal_layout"):
            with Vertical(id="input_column"):
                yield Static("[b]Input Image[/b]", classes="box_header")

                yield Static("Directory Path:", classes="setting_label")
                yield Input(placeholder="e.g. /home/user/images", id="directory_path_input", classes="setting_input")
                yield Button("Load Directory", id="load_directory_button", classes="action_button")

                yield Static("Select Image:", classes="setting_label")
                yield Select([], id="image_select_list", classes="setting_input")

                yield Container(id="input_image_box", classes="image_box")

            with Vertical(id="settings_box", classes="settings-box"):
                yield Static("[b]Process[/b]", classes="box_header")
                with RadioSet(id="upscale_type_radio"):
                    yield RadioButton("Upscale", value=True)
                    yield RadioButton("Face Restore")

                yield Static("[b]Parameters[/b]", classes="box_header")
                yield Static("Scale Factor:", classes="setting_label")
                yield Input(value="4", id="scale_factor_input", classes="setting_input")

                yield Static("\n[b]Navigation[/b]", classes="box_header")
                yield Static("1: Return to LLM", id="navigation_content")

            with Vertical(id="output_image_box", classes="output-box"):
                yield Static("[b]Result[/b]", classes="box_header")
                yield Static("Result will appear here...", id="result_image_placeholder")

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
