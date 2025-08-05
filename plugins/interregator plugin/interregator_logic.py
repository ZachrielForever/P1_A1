# plugins/interregator_plugin/interregator_logic.py

import os
import torch
from transformers import BlipForConditionalGeneration, BlipProcessor
from PIL import Image

class InterrogatorLogic:
    """
    Handles the core logic for the Interrogator plugin, including model loading,
    and image-to-text inference.
    """
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.processor = None
        self.model = None
        self.model_path = os.getenv("INTERROGATOR_MODEL_PATH", "Salesforce/blip-image-captioning-large")

    def load_model(self):
        """Loads the image-to-text model into memory."""
        if self.model:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        try:
            print(f"Loading interrogator model from {self.model_path}...")
            # Use GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.processor = BlipProcessor.from_pretrained(self.model_path)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_path, torch_dtype=torch.float16).to(device)
            print("Interrogator model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load interrogator model: {e}")
            self.model = None
            self.processor = None
            return False

    def unload_model(self):
        """Unloads the interrogator model from memory."""
        if self.model:
            print("Unloading interrogator model...")
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_inference(self, image_path: str):
        """
        Runs image-to-text inference on the loaded model.
        Returns the generated text description.
        """
        if not self.model:
            print("Error: No model loaded.")
            return "No model is currently loaded."

        print(f"Running inference for image at {image_path}...")
        try:
            raw_image = Image.open(image_path).convert('RGB')
            # conditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt").to(self.model.device, self.model.dtype)
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return f"An error occurred during inference: {e}"
