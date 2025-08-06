# plugins/diffusor_plugin/image_diffusor_logic.py

import os
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

class ImageDiffusorLogic:
    """
    Handles the backend logic for interacting with the image diffusion model.
    """

    def __init__(self, plugin_path):
        self.pipeline = None
        self.plugin_path = plugin_path
        # Hardcoding the model ID for demonstration
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Define the base output path relative to the program's root
        self.output_dir = os.path.abspath(os.path.join(self.plugin_path, '../../output/images'))

    def load_model(self):
        print("Attempting to load image diffusion model...")
        try:
            self.pipeline = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float16)
            self.pipeline = self.pipeline.to(self.device)
            print("Image diffusion model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def get_model_id(self):
        """Returns the ID of the currently loaded model."""
        return self.model_id

    def run_inference(self, prompt: str):
        # ... (rest of the run_inference method remains the same)
        if not self.pipeline:
            print("Error: No model loaded. Please load a model first.")
            return None

        print(f"Running inference for prompt: '{prompt}'")
        try:
            image = self.pipeline(prompt).images[0]
            print("Image generated successfully.")
            return image
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return None

    def save_image(self, image: Image, filename: str):
        # ... (rest of the save_image method remains the same)
        if not image:
            return False
        try:
            full_path = os.path.join(self.output_dir, filename)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                print(f"Created directory: {self.output_dir}")

            image.save(full_path)
            print(f"Image saved to {full_path}")
            return True
        except Exception as e:
            print(f"Failed to save image: {e}")
            return False
