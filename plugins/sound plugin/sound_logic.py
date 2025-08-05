# plugins/sound_plugin/sound_logic.py

import os
import torch
import scipy
from transformers import AutoProcessor, MusicgenForConditionalGeneration

class SoundLogic:
    """
    Handles the core logic for the Sound AI plugin, including model loading,
    audio generation, and state management.
    """
    def __init__(self, main_app=None):
        self.main_app = main_app
        self.processor = None
        self.model = None
        self.model_path = os.getenv("SOUND_MODEL_PATH", "facebook/musicgen-small")

    def load_model(self):
        """Loads the sound generation model into memory."""
        if self.model:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        try:
            print(f"Loading sound model from {self.model_path}...")
            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.processor = AutoProcessor.from_pretrained(self.model_path)
            self.model = MusicgenForConditionalGeneration.from_pretrained(self.model_path)
            self.model = self.model.to(device)
            print("Sound generation model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load sound model: {e}")
            self.model = None
            self.processor = None
            return False

    def unload_model(self):
        """Unloads the sound generation model from memory."""
        if self.model:
            print("Unloading sound generation model...")
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            print("Model unloaded.")

    def run_inference(self, prompt: str):
        """
        Runs sound generation on the loaded model.
        Returns the path to the generated sound file.
        """
        if not self.model:
            print("Error: No model loaded.")
            return None

        print(f"Running sound generation with prompt: '{prompt}'")
        try:
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            ).to(self.model.device)

            audio_values = self.model.generate(**inputs, max_new_tokens=256)
            sampling_rate = self.model.config.audio_encoder.sampling_rate

            output_path = "output_audio.wav"
            scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())

            return output_path
        except Exception as e:
            print(f"An error occurred during inference: {e}")
            return None
