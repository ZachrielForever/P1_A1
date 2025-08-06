# llm_logic.py

import os
from llama_cpp import Llama

class LlmPlugin:
    def __init__(self, plugin_path):
        self.llm = None
        self.model_path = os.path.join(plugin_path, "models", "llm_model.gguf")

    def load_model(self):
        # Load the model only once
        if self.llm is None:
            self.llm = Llama(
                model_path=self.model_path,
                n_gpu_layers=-1,
                n_ctx=4096,
            )

    def unload_model(self):
        # Gracefully handle model unloading
        if self.llm is not None:
            self.llm = None

    def run_inference(self, user_prompt: str, settings: dict) -> str:
        """
        Runs inference on the LLM with user-defined settings.

        Args:
            user_prompt (str): The text prompt from the user.
            settings (dict): A dictionary of user-defined settings (e.g., temperature, top_k).
        """
        if self.llm is None:
            return "Error: LLM model is not loaded."

        # Get settings with default values
        temperature = settings.get("temperature", 0.7)
        top_k = settings.get("top_k", 40)
        top_p = settings.get("top_p", 0.9)
        max_output_tokens = settings.get("max_output_tokens", 512)

        # Run inference with the provided settings
        output = self.llm(
            f"Question: {user_prompt} Answer:",
            max_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            echo=True,
        )
        return output['choices'][0]['text']
