# plugins/diffusor_plugin/diffusor_logic.py

import os
import torch
from diffusers import StableDiffusionPipeline

class DiffusorLogic:
    """
    Handles the core logic for the Diffusor plugin, including model loading,
    image generation, and state management.
    """
    def __init__(self, main_app=None):
        """Initializes the logic class with a reference to the main app."""
        self.main_app = main_app
        self.pipe = None
        # Use a default model path for the pipeline
        self.model_path = os.getenv("DIFFUSOR_MODEL_PATH", "runwayml/stable-diffusion-v1-5")

    def load_model(self):
        """Loads the diffusion model into memory."""
        if self.pipe:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        try:
            print(f"Loading model from {self.model_path}...")
            # Use GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # The pipeline automatically downloads and caches the model
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            self.pipe = self.pipe.to(device)
            print("Diffusion model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.pipe = None
            return False

    def unload_model(self):
        """Unloads the diffusion model from memory."""
        if self.pipe:
            print("Unloading diffusion model...")
            del self.pipe
            self.pipe = None
            # Explicitly call gc.collect() to help with memory cleanup
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_inference(self, prompt: str, negative_prompt: str = ""):
        """
        Runs image generation on the loaded model.
        Returns the generated image object.
        """
        if not self.pipe:
            print("Error: No model loaded.")
            return None

        print(f"Running image generation with prompt: '{prompt}'")
        try:
            # You can add more parameters here like num_inference_steps, guidance_scale, etc.
            image = self.pipe(prompt=prompt, negative_prompt=negative_prompt).images[0]
            # This returns a PIL Image object
            return image
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return None
