# plugins/interregator_plugin/interregator_logic.py

import os
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image

class InterrogatorPlugin:
    def __init__(self, plugin_path):
        self.model = None
        self.processor = None
        self.model_path = os.path.join(plugin_path, "models", "vit-base-patch16-224")

    def load_model(self):
        if self.model is None or self.processor is None:
            self.processor = ViTImageProcessor.from_pretrained(self.model_path)
            self.model = ViTForImageClassification.from_pretrained(self.model_path)
            self.model.to("cuda")

    def unload_model(self):
        self.model = self.model.to("cpu")
        torch.cuda.empty_cache()

    def run_inference(self, image: Image.Image, settings: dict) -> str:
        """
        Runs image-to-text inference with user-defined settings.

        Args:
            image (Image.Image): The input image.
            settings (dict): A dictionary of user-defined settings.
        """
        if self.model is None or self.processor is None:
            raise ValueError("Model and processor are not loaded.")

        # Get settings with default values
        max_new_tokens = settings.get("max_new_tokens", 128)
        beam_size = settings.get("beam_size", 1)

        inputs = self.processor(images=image, return_tensors="pt").to("cuda")

        # Run inference with the provided settings
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=beam_size
        )

        caption = self.processor.decode(outputs[0], skip_special_tokens=True)
        return caption
