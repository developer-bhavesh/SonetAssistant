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
        self.search_context = None
        self.source_urls = []
    
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
        
        # Auto-generate session title from first user message
        if role == MessageRole.USER and self.current_session.title == "New Conversation":
            # Extract meaningful title from query (first 50 chars)
            title = content.replace('/search ', '').strip()
            title = title[:50] + '...' if len(title) > 50 else title
            self.current_session.title = title
        
        self.message_added.emit(message)
        return message
    
    def get_conversation_history(self) -> list[Message]:
        """Get current conversation messages."""
        return self.current_session.messages.copy()
    
    def clear_conversation(self):
        """Clear current conversation."""
        self.current_session = self._create_new_session()
        self.search_context = None
        self.source_urls = []
        self.state_cleared.emit()
    
    def set_search_context(self, context: str, urls: list[str]):
        """Set search context for next AI request."""
        self.search_context = context
        self.source_urls = urls
    
    def clear_search_context(self):
        """Clear search context after AI response."""
        self.search_context = None
        self.source_urls = []
    
    def get_current_session(self) -> ChatSession:
        """Get current session."""
        return self.current_session
