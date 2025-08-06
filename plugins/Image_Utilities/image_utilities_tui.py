#!/usr/bin/env python
# image_utilities_tui.py

from textual.containers import Container, Horizontal
from textual.widgets import Static, RadioSet, RadioButton

class ImageUtilitiesPane(Container):
    """The TUI pane for upscaling or restoring images."""

    def compose(self):
        """Create the layout for the Image Utilities pane."""
        self.add_class("image_utilities_pane")
        with Horizontal(id="horizontal_layout"):
            with Container(id="input_image_box", classes="input-box"):
                yield Static("Load an image to process...", classes="placeholder_text")

            with Container(id="settings_box", classes="settings-box"):
                yield Static("[b]Process[/b]", classes="box_header")
                with RadioSet(id="process_selection"):
                    yield RadioButton("Upscale", value=True)
                    yield RadioButton("Face Restore")

                yield Static("\n[b]Parameters[/b]", classes="box_header")
                yield Static("", id="settings_content")

                yield Static("\n[b]Navigation[/b]", classes="box_header")
                yield Static("", id="navigation_content")

            with Container(id="output_image_box", classes="output-box"):
                yield Static("Result will appear here...", classes="placeholder_text")
