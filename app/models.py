"""
Data models for the application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class MessageRole(Enum):
    """Message role enumeration."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    """Chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API calls."""
        return {
            "role": self.role.value,
            "content": self.content
        }

@dataclass
class ChatSession:
    """Chat session model."""
    id: str
    title: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
