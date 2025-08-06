# plugins/image_utilities_plugin/image_utilities_logic.py

import os
import torch
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.utils import imwrite

class ImageUtilitiesPlugin:
    def __init__(self, plugin_path):
        self.upsampler = None
        self.model_path = os.path.join(plugin_path, "models", "RealESRGAN_x4plus.pth")

    def load_model(self):
        if self.upsampler is None:
            # Initialize the upsampler
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )
            self.upsampler = RealESRGANer(
                scale=4,
                model_path=self.model_path,
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=True,
                device="cuda"
            )

    def unload_model(self):
        if self.upsampler is not None:
            self.upsampler = None
            torch.cuda.empty_cache()

    def run_inference(self, image_path: str, settings: dict) -> str:
        """
        Runs image upscaling or restoration with user-defined settings.

        Args:
            image_path (str): The path to the input image.
            settings (dict): A dictionary of user-defined settings.
        """
        if self.upsampler is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        # Get settings with default values
        scale_factor = settings.get("scale_factor", 4)
        upscale_type = settings.get("upscale_type", "upscale") # or 'face_restore'

        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if upscale_type == "upscale":
            # Upscale the image
            upscaled_image, _ = self.upsampler.enhance(img, outscale=scale_factor)
        elif upscale_type == "face_restore":
            # Assuming a different model or method for face restoration
            # Placeholder for actual face restoration logic
            upscaled_image = img # This is a placeholder, replace with actual logic

        output_path = "upscaled_image.png"
        imwrite(upscaled_image, output_path)
        return output_path
