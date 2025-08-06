# plugins/image_utilities_plugin/image_utilities_logic.py

import os
import torch
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from facexlib.utils.face_restoration_helper import FaceRestoreHelper

class ImageUtilitiesLogic:
    """
    Handles the core logic for the Image Utilities plugin, including
    model loading, upscaling, and face restoration.
    """
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.upscaler = None
        self.face_restorer = None
        # You will need to download a RealESRGAN model and place it in the models directory.
        self.model_path = os.getenv("UPSCALER_MODEL_PATH", "./models/RealESRGAN_x4plus.pth")

    def load_upscaler(self):
        """Loads the Real-ESRGAN upscaling model into memory."""
        if self.upscaler:
            print("Upscaler model already loaded. Unloading first...")
            self.unload_upscaler()

        try:
            print(f"Loading upscaler model from {self.model_path}...")
            # Use GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"

            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4
            )
            self.upscaler = RealESRGANer(
                scale=4,
                model_path=self.model_path,
                model=model,
                device=device,
                pre_pad=0,
                half=True if device == "cuda" else False
            )
            print("Upscaler model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load upscaler model: {e}")
            self.upscaler = None
            return False

    def unload_upscaler(self):
        """Unloads the upscaler model from memory."""
        if self.upscaler:
            print("Unloading upscaler model...")
            del self.upscaler
            self.upscaler = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_upscale(self, image: np.ndarray):
        """Upscales a given image using the loaded model."""
        if not self.upscaler:
            print("Error: No upscaler model loaded.")
            return None

        print("Running image upscaling...")
        try:
            _, _, output_image = self.upscaler.enhance(image, outscale=4)
            return output_image
        except Exception as e:
            print(f"An error occurred during upscaling: {e}")
            return None

    def load_face_restorer(self):
        """Loads the face restoration model into memory."""
        if self.face_restorer:
            print("Face restoration model already loaded.")
            return True

        try:
            print("Loading face restoration model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.face_restorer = FaceRestoreHelper(
                upscale_factor=2,  # Example factor
                face_size=512,
                model_rootpath=os.getenv("FACEXLIB_MODEL_PATH", "./models")
            )
            self.face_restorer.init_detection_model(model_name="retinaface_resnet50", device=device)
            self.face_restorer.init_restoration_model(model_name="CodeFormer", device=device)
            print("Face restoration models loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load face restoration models: {e}")
            self.face_restorer = None
            return False

    def unload_face_restorer(self):
        """Unloads the face restoration models from memory."""
        if self.face_restorer:
            print("Unloading face restoration models...")
            del self.face_restorer
            self.face_restorer = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Models unloaded.")

    def run_face_restoration(self, image: np.ndarray):
        """Restores faces in a given image."""
        if not self.face_restorer:
            print("Error: No face restoration model loaded.")
            return None

        print("Running face restoration...")
        try:
            self.face_restorer.read_image(image)
            self.face_restorer.get_face_landmarks_5()
            self.face_restorer.align_warp_face()
            self.face_restorer.face_restoration()
            final_image = self.face_restorer.paste_back()
            return final_image
        except Exception as e:
            print(f"An error occurred during face restoration: {e}")
            return None
