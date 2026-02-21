"""
Prompt Engine for managing system prompts and context.
"""
from app.config import Config
from app.models import Message, MessageRole

class PromptEngine:
    """Manages system prompts and message context."""
    
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt or Config.SYSTEM_PROMPT
    
    def build_messages(self, conversation: list[Message]) -> list[Message]:
        """Build complete message list with system prompt."""
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=self.system_prompt
        )
        return [system_message] + conversation
    
    def set_system_prompt(self, prompt: str):
        """Update system prompt."""
        self.system_prompt = prompt
