# plugins/diffusor_plugin/image_diffusor_tui.py

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, RichLog, Select
from textual.app import ComposeResult
from textual import on
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .image_diffusor_logic import ImageDiffusorLogic

class ImageDiffusorPane(Container):
    """
    The TUI pane for interacting with the image diffusion model.
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
    """

    MODEL_DIMENSIONS = {
        "runwayml/stable-diffusion-v1-5": (512, 512),
        "stabilityai/stable-diffusion-xl-base-1.0": (1024, 1024),
        "stabilityai/stable-diffusion-3-5": (2048, 2048),
    }

    def __init__(self, logic: "ImageDiffusorLogic", **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def compose(self) -> ComposeResult:
        """
        Create the new layout for the image diffusor pane.
        """
        self.add_class("image_diffusor_pane")

        # Top section: Parameters
        with Vertical(id="top_parameters_container"):
            yield Static("[b]Parameters[/b]", classes="box_header")
            with Horizontal(classes="param-row"):
                with Vertical(classes="param-group"):
                    yield Static("Guidance Scale:", classes="setting_label")
                    yield Input(value="7.5", id="guidance_scale_input", classes="setting_input_small")
                with Vertical(classes="param-group"):
                    yield Static("Inference Steps:", classes="setting_label")
                    yield Input(value="50", id="inference_steps_input", classes="setting_input_small")
                with Vertical(classes="param-group"):
                    yield Static("Seed:", classes="setting_label")
                    yield Input(value="-1", id="seed_input", classes="setting_input_small")

            with Horizontal(classes="param-row"):
                with Vertical(classes="param-group"):
                    yield Static("Aspect Ratio:", classes="setting_label")
                    yield Select(
                        [
                            ("Custom", "custom"),
                            ("1:1 (Square)", "1:1"),
                            ("4:3 (Landscape)", "4:3"),
                            ("3:2 (Landscape)", "3:2"),
                            ("16:9 (Widescreen)", "16:9"),
                            ("3:4 (Portrait)", "3:4"),
                            ("2:3 (Portrait)", "2:3"),
                            ("9:16 (Tallscreen)", "9:16"),
                        ],
                        value="custom",
                        id="aspect_ratio_select"
                    )
                with Vertical(classes="param-group"):
                    yield Static("Width:", classes="setting_label")
                    yield Input(value="512", id="width_input", classes="setting_input_small")
                with Vertical(classes="param-group"):
                    yield Static("Height:", classes="setting_label")
                    yield Input(value="512", id="height_input", classes="setting_input_small")

        # Middle section: Left (Output), Center (Log), Right (Model Info)
        with Horizontal(id="middle_content_area"):
            # Left panel for output settings
            with Vertical(id="left_panel", classes="settings-box"):
                yield Static("[b]Output[/b]", classes="box_header")
                yield Static("Save Directory:", classes="setting_label")
                yield Input(value="output/images", id="output_dir_input", classes="setting_input")

            # Center area for the output log/image display
            yield RichLog(id="image_display_box", classes="output-box", highlight=True)

            # Right panel for model information
            with Vertical(id="right_panel", classes="settings-box"):
                yield Static("[b]Model Info[/b]", classes="box_header")
                # These Static widgets will be updated by your application logic
                yield Static("Model: [i]Not Loaded[/i]", id="model_info_static")
                yield Static("LoRA: [i]Not Loaded[/i]", id="lora_info_static")
                yield Static("VAE: [i]Not Loaded[/i]", id="vae_info_static")

        # Bottom section: Prompts
        with Horizontal(id="bottom_prompts"):
            # Each prompt is in a container to enforce the half-width split
            with Vertical(classes="prompt-container-half"):
                yield Static("Positive Prompt:", classes="prompt_label")
                yield Input(id="positive_prompt_input", classes="prompt-box")
            with Vertical(classes="prompt-container-half"):
                yield Static("Negative Prompt:", classes="prompt_label")
                yield Input(id="negative_prompt_input", classes="prompt-box")

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        # Only try to set dimensions if the logic object is available and has the method
        if self.logic and hasattr(self.logic, 'get_model_id'):
            self._set_default_dimensions_from_model()
        else:
            # Set a default size if the model isn't ready yet
            self.query_one("#width_input", Input).value = "512"
            self.query_one("#height_input", Input).value = "512"
            self.query_one("#aspect_ratio_select", Select).value = "1:1"
            self.query_one("#width_input", Input).disabled = True
            self.query_one("#height_input", Input).disabled = True

    def _set_default_dimensions_from_model(self) -> None:
        """Sets the default dimensions based on the loaded model ID."""
        model_id = self.logic.get_model_id()
        default_size = self.MODEL_DIMENSIONS.get(model_id, (512, 512))
        width, height = default_size

        # Update the inputs and set aspect ratio to square
        self.query_one("#width_input", Input).value = str(width)
        self.query_one("#height_input", Input).value = str(height)
        self.query_one("#aspect_ratio_select", Select).value = "1:1"
        self.query_one("#width_input", Input).disabled = True
        self.query_one("#height_input", Input).disabled = True


    @on(Select.Changed)
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle when the Aspect Ratio Select widget is changed."""
        width_input = self.query_one("#width_input", Input)
        height_input = self.query_one("#height_input", Input)

        # Handle the "Select" or "NoSelection" state
        if event.value is None or event.value == Select.BLANK:
            width_input.disabled = False
            height_input.disabled = False
            return

        if event.value == "custom":
            width_input.disabled = False
            height_input.disabled = False
        else:
            width_input.disabled = True
            height_input.disabled = True

            aspect_ratio_parts = event.value.split(':')
            if len(aspect_ratio_parts) == 2:
                w, h = map(int, aspect_ratio_parts)

                # Assume a fixed base dimension for calculation.
                base_dimension = 512

                # Correct logic: always fix the larger dimension of the ratio to the base dimension
                if w > h: # Landscape ratios
                    new_height = base_dimension
                    new_width = int(base_dimension * (w / h))
                elif h > w: # Portrait ratios
                    new_width = base_dimension
                    new_height = int(base_dimension * (h / w))
                else: # Square ratio
                    new_width = base_dimension
                    new_height = base_dimension

                # Correct the dimensions to be multiples of 8, which is often a requirement
                # for Stable Diffusion models.
                new_width = int(new_width / 8) * 8
                new_height = int(new_height / 8) * 8

                width_input.value = str(new_width)
                height_input.value = str(new_height)
