# plugins/3d_model_plugin/3d_model_logic.py

import os
import torch
from transformers import pipeline

class ThreeDModelLogic:
    """
    Handles the core logic for the 3D Model plugin, including model loading,
    3D model generation, and state management.
    """
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.model = None
        self.model_path = os.getenv("THREED_MODEL_PATH", "openai/shap-e")

    def load_model(self):
        """Loads the 3D generation model into memory."""
        if self.model:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        try:
            print(f"Loading 3D model from {self.model_path}...")
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # Using the transformers pipeline for a simplified example
            self.model = pipeline("text-to-image", model=self.model_path, device=device)
            print("3D generation model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load 3D model: {e}")
            self.model = None
            return False

    def unload_model(self):
        """Unloads the 3D generation model from memory."""
        if self.model:
            print("Unloading 3D generation model...")
            del self.model
            self.model = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_inference(self, prompt: str):
        """
        Runs 3D model generation on the loaded model.
        Returns the path to the generated 3D model file.
        """
        if not self.model:
            print("Error: No model loaded.")
            return None

        print(f"Running 3D model generation with prompt: '{prompt}'")
        try:
            # This is a placeholder for actual 3D generation logic
            output_model = self.model(prompt)
            output_path = "output_model.glb"
            # Logic to save the generated model would go here
            # output_model.save(output_path)

            return output_path
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return None
