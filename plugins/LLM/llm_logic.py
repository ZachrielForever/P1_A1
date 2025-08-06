# llm_logic.py

import os
from llama_cpp import Llama

class LLMLogic:
    """
    Handles the core logic for the LLM plugin, including model loading,
    inference, and state management.
    """
    def __init__(self, main_app=None):
        """Initializes the logic class with a reference to the main app."""
        self.main_app = main_app
        self.model = None
        self.model_path = os.getenv("LLM_MODEL_PATH", "./models/gemma-3-8b.gguf")

    def load_model(self):
        """Loads the LLM into memory."""
        if self.model:
            print("Model already loaded. Unloading first...")
            self.unload_model()

        if not os.path.exists(self.model_path):
            print(f"Error: Model not found at {self.model_path}")
            return False

        try:
            print(f"Loading model from {self.model_path}...")
            # Initialize the Llama model
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # You can adjust this
                n_gpu_layers=-1, # -1 to offload all layers to GPU
                verbose=False
            )
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
            return False

    def unload_model(self):
        """Unloads the LLM from memory."""
        if self.model:
            print("Unloading model...")
            self.model = None
            print("Model unloaded.")
            # Explicitly call gc.collect() to help with memory cleanup
            import gc
            gc.collect()

    def run_inference(self, prompt: str):
        """Runs inference on the loaded model."""
        if not self.model:
            print("Error: No model loaded.")
            return "No model is currently loaded."

        print(f"Running inference with prompt: '{prompt}'")
        try:
            stream = self.model.create_completion(prompt, stream=True)
            response = ""
            for output in stream:
                token = output["choices"][0]["text"]
                response += token
                # Here you would typically send the token back to the TUI
                # For now, we'll just print it.
            return response
        except Exception as e:
            return f"An error occurred during inference: {e}"
