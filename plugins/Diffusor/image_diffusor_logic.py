# plugins/diffusor_plugin/diffusor_logic.py

import os
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

class ImageDiffusorPlugin:
    def __init__(self, plugin_path):
        self.pipe = None
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.model_path = os.path.join(plugin_path, "models")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id, torch_dtype=torch.float16
        )

    def load_model(self):
        # Model is loaded in __init__
        self.pipe.to("cuda")

    def unload_model(self):
        self.pipe = self.pipe.to("cpu")
        torch.cuda.empty_cache()

    def run_inference(self, user_prompt: str, settings: dict) -> Image.Image:
        """
        Runs inference on the image diffusion model with user-defined settings.

        Args:
            user_prompt (str): The text prompt to generate an image from.
            settings (dict): A dictionary of user-defined settings.
        """
        if self.pipe is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        # Get settings with default values
        num_inference_steps = settings.get("num_inference_steps", 50)
        guidance_scale = settings.get("guidance_scale", 7.5)
        seed = settings.get("seed", None)

        generator = torch.Generator("cuda").manual_seed(seed) if seed is not None else None

        # Run inference with the provided settings
        image = self.pipe(
            prompt=user_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]

        return image
