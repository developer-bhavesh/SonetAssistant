"""Local LLM backend using Ollama."""
from app.services.ai_client import AIBackend
from app.models import Message
import requests

class OllamaBackend(AIBackend):
    """Ollama local LLM backend."""
    
    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate_response(self, messages: list[Message]) -> str:
        """Generate response using Ollama."""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [msg.to_dict() for msg in messages],
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
