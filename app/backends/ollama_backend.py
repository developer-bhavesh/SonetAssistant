"""
Example: Local LLM backend using Ollama.
Install: pip install ollama
"""
from app.services.ai_client import AIBackend
from app.models import Message

class OllamaBackend(AIBackend):
    """Ollama local LLM backend."""
    
    def __init__(self, model: str = "llama2"):
        try:
            import ollama
            self.client = ollama
            self.model = model
        except ImportError:
            raise ImportError("Install ollama: pip install ollama")
    
    def generate_response(self, messages: list[Message]) -> str:
        """Generate response using Ollama."""
        response = self.client.chat(
            model=self.model,
            messages=[msg.to_dict() for msg in messages]
        )
        return response['message']['content']

# Usage in main.py:
# from app.backends.ollama_backend import OllamaBackend
# ai_client = AIClient(backend=OllamaBackend(model="llama2"))
