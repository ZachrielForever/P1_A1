# llm_logic.py

import os
from llama_cpp import Llama

class LLMLogic:
    """Handles the backend logic for interacting with the LLM."""

    def __init__(self, plugin_path):
        self.llm = None
        self.plugin_path = plugin_path
        self.model_path = os.path.join(self.plugin_path, "llama-2-7b-chat.Q4_K_M.gguf")

    def load_model(self):
        """Loads the Llama model from the specified path."""
        print("Attempting to load model...")
        if not os.path.exists(self.model_path):
            print(f"Error: Model file not found at {self.model_path}")
            return False

        try:
            self.llm = Llama(model_path=self.model_path)
            print("Model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def run_inference(self, prompt: str, settings: dict):
        """Runs inference on the loaded model using the provided settings."""
        if not self.llm:
            return "Error: No model loaded. Please load a model first."

        print(f"Running inference with prompt: '{prompt}'")
        try:
            # Extract settings from the dictionary, providing default values
            temperature = float(settings.get("temperature_input", 0.7))
            top_k = int(settings.get("top_k_input", 40))
            top_p = float(settings.get("top_p_input", 0.9))
            max_tokens = int(settings.get("max_output_tokens_input", 512))

            stream = self.llm.create_completion(
                prompt,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=True
            )

            response = ""
            for output in stream:
                token = output["choices"][0]["text"]
                response += token
            return response
        except Exception as e:
            return f"An error occurred during inference: {e}"
