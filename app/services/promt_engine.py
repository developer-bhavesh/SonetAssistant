"""
Prompt Engine for managing system prompts and context.
"""
from app.config import Config
from app.models import Message, MessageRole

class PromptEngine:
    """Manages system prompts and message context."""
    
    def __init__(self, system_prompt: str = None, user_memory=None, ai_scraper=None):
        self.system_prompt = system_prompt or Config.SYSTEM_PROMPT
        self.user_memory = user_memory
        self.ai_scraper = ai_scraper
    
    def build_messages(self, conversation: list[Message]) -> list[Message]:
        """Build complete message list with system prompt, memory, and tools."""
        from datetime import datetime
        
        # Build enhanced system prompt with current date/time
        now = datetime.now()
        datetime_context = f"\n\nCurrent Date & Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\nYear: {now.year}\n"
        enhanced_prompt = self.system_prompt + datetime_context
        
        # Add user memory context
        if self.user_memory:
            memory_context = self.user_memory.get_memory_context()
            if memory_context:
                enhanced_prompt += "\n\n" + memory_context
        
        # Add AI scraping tools
        if self.ai_scraper:
            enhanced_prompt += "\n\n" + self.ai_scraper.get_scraping_tools_prompt()
        
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=enhanced_prompt
        )
        return [system_message] + conversation
    
    def set_system_prompt(self, prompt: str):
        """Update system prompt."""
        self.system_prompt = prompt
