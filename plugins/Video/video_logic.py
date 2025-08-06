# plugins/video_diffusor_plugin/video_diffusor_logic.py

import os
import torch
from diffusers import DiffusionPipeline
from typing import List

class VideoDiffusorLogic:
    """
    Handles the core logic for the Video Diffusor plugin, including model loading,
    video generation, and state management.
    """
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.pipe = None
        self.model_path = os.getenv("VIDEO_DIFFUSOR_MODEL_PATH", "damo-vilab/text-to-video-ms-1.7")

    def load_model(self):
        """Loads the video diffusion model into memory."""
        if self.pipe:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        try:
            print(f"Loading video model from {self.model_path}...")
            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.pipe = DiffusionPipeline.from_pretrained(self.model_path, torch_dtype=torch.float16, variant="fp16")
            self.pipe = self.pipe.to(device)
            print("Video diffusion model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load video model: {e}")
            self.pipe = None
            return False

    def unload_model(self):
        """Unloads the video diffusion model from memory."""
        if self.pipe:
            print("Unloading video diffusion model...")
            del self.pipe
            self.pipe = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_inference(self, prompt: str, negative_prompt: str = ""):
        """
        Runs video generation on the loaded model.
        Returns the path to the generated video file.
        """
        if not self.pipe:
            print("Error: No model loaded.")
            return None

        print(f"Running video generation with prompt: '{prompt}'")
        try:
            video_frames: List[Image.Image] = self.pipe(prompt, negative_prompt=negative_prompt).frames

            # Save the frames as a video file (e.g., using imageio)
            output_path = "output_video.mp4"
            import imageio
            imageio.mimsave(output_path, video_frames, fps=8)  # fps can be adjusted

            return output_path
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return None
