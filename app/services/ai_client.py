"""
AI Client service for interacting with OpenAI API.
Designed with strategy pattern for future backend extensibility.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, QThread
from openai import OpenAI, OpenAIError
from app.config import Config
from app.models import Message, MessageRole

class AIBackend(ABC):
    """Abstract base class for AI backends."""
    
    @abstractmethod
    def generate_response(self, messages: list[Message]) -> str:
        """Generate response from messages."""
        pass

class OpenAIBackend(AIBackend):
    """OpenAI API backend implementation."""
    
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_response(self, messages: list[Message]) -> str:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[msg.to_dict() for msg in messages],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class AIWorker(QThread):
    """Worker thread for non-blocking AI requests."""
    
    response_ready = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, backend: AIBackend, messages: list[Message]):
        super().__init__()
        self.backend = backend
        self.messages = messages
    
    def run(self):
        """Execute AI request in background thread."""
        try:
            response = self.backend.generate_response(self.messages)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AIClient(QObject):
    """
    AI Client service managing AI interactions.
    Uses worker threads to prevent UI blocking.
    """
    
    response_received = Signal(str)
    error_occurred = Signal(str)
    request_started = Signal()
    
    def __init__(self, backend: Optional[AIBackend] = None):
        super().__init__()
        self.backend = backend or self._create_default_backend()
        self.current_worker: Optional[AIWorker] = None
    
    def _create_default_backend(self) -> AIBackend:
        """Create default backend from config."""
        from app.config import Config
        
        # Use Ollama if enabled
        if Config.USE_OLLAMA:
            from app.backends.ollama_backend import OllamaBackend
            return OllamaBackend(
                model=Config.OLLAMA_MODEL,
                base_url=Config.OLLAMA_URL
            )
        # Use Gemini if API key is set
        elif Config.GEMINI_API_KEY:
            from app.backends.gemini_backend import GeminiBackend
            return GeminiBackend(
                api_key=Config.GEMINI_API_KEY,
                model=Config.AI_MODEL
            )
        # Fall back to OpenAI
        else:
            return OpenAIBackend(
                api_key=Config.OPENAI_API_KEY,
                model=Config.AI_MODEL,
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.AI_MAX_TOKENS
            )
    
    def send_message(self, messages: list[Message]):
        """Send messages to AI backend asynchronously."""
        if self.current_worker and self.current_worker.isRunning():
            return  # Prevent concurrent requests
        
        self.request_started.emit()
        self.current_worker = AIWorker(self.backend, messages)
        self.current_worker.response_ready.connect(self.response_received.emit)
        self.current_worker.error_occurred.connect(self.error_occurred.emit)
        self.current_worker.start()
    
    def cancel_request(self):
        """Cancel ongoing request."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
