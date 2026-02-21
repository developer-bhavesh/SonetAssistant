"""Google Gemini backend."""
from app.services.ai_client import AIBackend
from app.models import Message, MessageRole
from google import genai

class GeminiBackend(AIBackend):
    """Google Gemini backend."""
    
    def __init__(self, api_key: str, model: str = "gemini-3-flash-preview"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def generate_response(self, messages: list[Message]) -> str:
        """Generate response using Gemini."""
        # Convert to Gemini format
        contents = []
        system_instruction = None
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == MessageRole.ASSISTANT:
                contents.append({"role": "model", "parts": [{"text": msg.content}]})
        
        config = {"system_instruction": system_instruction} if system_instruction else {}
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config
        )
        
        return response.text
