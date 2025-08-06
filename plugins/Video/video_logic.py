# plugins/video_diffusor_plugin/video_diffusor_logic.py

import os
import torch
from diffusers import DiffusionPipeline
import imageio

class VideoDiffusorPlugin:
    def __init__(self, plugin_path):
        self.pipe = None
        self.model_id = "damo-vilab/text-to-video-ms-1-7b"
        self.model_path = os.path.join(plugin_path, "models", "video_model")

    def load_model(self):
        if self.pipe is None:
            self.pipe = DiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float16)
            self.pipe.to("cuda")

    def unload_model(self):
        if self.pipe is not None:
            self.pipe = self.pipe.to("cpu")
            torch.cuda.empty_cache()

    def run_inference(self, user_prompt: str, settings: dict) -> str:
        """
        Runs video generation inference with user-defined settings.

        Args:
            user_prompt (str): The text prompt for video generation.
            settings (dict): A dictionary of user-defined settings.
        """
        if self.pipe is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        # Get settings with default values
        num_frames = settings.get("num_frames", 16)
        num_inference_steps = settings.get("num_inference_steps", 25)
        guidance_scale = settings.get("guidance_scale", 9.0)

        # Run inference with the provided settings
        video_frames = self.pipe(
            prompt=user_prompt,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).frames

        output_path = "generated_video.mp4"
        imageio.mimwrite(output_path, video_frames, fps=8)
        return output_path
