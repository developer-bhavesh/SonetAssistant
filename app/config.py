"""
Configuration management for Sonet Assistant.
Loads settings from environment variables with validation and defaults.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with environment-based settings."""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    ASSETS_DIR = BASE_DIR / "assets"
    
    # AI Configuration
    USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "false").lower() == "true"
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-pro")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Sonet Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # UI Configuration
    THEME: str = os.getenv("THEME", "dark")
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1200"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "800"))
    
    # System Prompt
    SYSTEM_PROMPT: str = """You are Sonet, a helpful AI assistant.

When you receive web search data:
- READ the web information carefully
- USE it to answer the user's question
- Include specific details from the web data
- Write a natural, complete answer

For technical questions:
- Provide clear examples
- Explain commands
- Give practical advice"""
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not cls.USE_OLLAMA and not cls.GEMINI_API_KEY and not cls.OPENAI_API_KEY:
            errors.append("No AI backend configured. Set USE_OLLAMA=true or provide API key")
        return errors
    
    @classmethod
    def get_app_icon_path(cls) -> Optional[Path]:
        """Get application icon path if it exists."""
        icon_path = cls.ASSETS_DIR / "appicon.png"
        return icon_path if icon_path.exists() else None
