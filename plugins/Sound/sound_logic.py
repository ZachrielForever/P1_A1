# plugins/sound_plugin/sound_logic.py

import os
import torch
import scipy
from transformers import pipeline

class SoundAIPlugin:
    def __init__(self, plugin_path):
        self.generator = None
        self.model_id = "facebook/musicgen-small"
        self.model_path = os.path.join(plugin_path, "models", "musicgen-small")

    def load_model(self):
        if self.generator is None:
            self.generator = pipeline(task="text-to-audio", model=self.model_id)

    def unload_model(self):
        if self.generator is not None:
            self.generator = None
            torch.cuda.empty_cache()

    def run_inference(self, user_prompt: str, settings: dict) -> str:
        """
        Runs sound generation inference with user-defined settings.

        Args:
            user_prompt (str): The text prompt for sound generation.
            settings (dict): A dictionary of user-defined settings.
        """
        if self.generator is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        # Get settings with default values
        duration = settings.get("duration", 5) # in seconds
        sampling_rate = settings.get("sampling_rate", 16000)

        # Run inference with the provided settings
        audio_output = self.generator(
            prompt=user_prompt,
            duration=duration,
            sampling_rate=sampling_rate
        )

        output_filename = "generated_sound.wav"
        scipy.io.wavfile.write(output_filename, rate=sampling_rate, data=audio_output['audio'])
        return output_filename
