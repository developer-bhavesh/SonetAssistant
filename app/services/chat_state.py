"""
Chat state management service.
Manages conversation history and session state.
"""
from PySide6.QtCore import QObject, Signal
from app.models import Message, ChatSession, MessageRole
from datetime import datetime
import uuid

class ChatStateManager(QObject):
    """
    Centralized state management for chat sessions.
    Emits signals for state changes to update UI reactively.
    """
    
    message_added = Signal(Message)
    session_changed = Signal(ChatSession)
    state_cleared = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_session = self._create_new_session()
    
    def _create_new_session(self) -> ChatSession:
        """Create a new chat session."""
        return ChatSession(
            id=str(uuid.uuid4()),
            title="New Conversation"
        )
    
    def add_message(self, role: MessageRole, content: str) -> Message:
        """Add message to current session."""
        message = Message(
            role=role,
            content=content,
            id=str(uuid.uuid4())
        )
        self.current_session.messages.append(message)
        self.current_session.updated_at = datetime.now()
        self.message_added.emit(message)
        return message
    
    def get_conversation_history(self) -> list[Message]:
        """Get current conversation messages."""
        return self.current_session.messages.copy()
    
    def clear_conversation(self):
        """Clear current conversation."""
        self.current_session = self._create_new_session()
        self.state_cleared.emit()
    
    def get_current_session(self) -> ChatSession:
        """Get current session."""
        return self.current_session
