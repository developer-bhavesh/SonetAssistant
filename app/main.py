"""
Main application entry point.
Initializes services and launches the application.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from app.config import Config
from app.services import AIClient, PromptEngine, ChatStateManager, WebSearchService, DatabaseService, UserMemoryService, AIWebScraperService, TTSService
from app.ui.modern_window import ModernMainWindow as MainWindow

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_configuration() -> bool:
    """Validate configuration before starting app."""
    errors = Config.validate()
    if errors:
        app = QApplication.instance() or QApplication(sys.argv)
        error_msg = "Configuration errors:\n\n" + "\n".join(f"• {e}" for e in errors)
        error_msg += "\n\nPlease check your .env file."
        QMessageBox.critical(None, "Configuration Error", error_msg)
        return False
    return True

def create_application() -> QApplication:
    """Create and configure QApplication."""
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.APP_VERSION)
    
    return app

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {Config.APP_NAME} v{Config.APP_VERSION}")
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Create application
    app = create_application()
    
    try:
        # Initialize services (dependency injection)
        user_memory = UserMemoryService()
        ai_scraper = AIWebScraperService()
        tts_service = TTSService(
            model_path=Config.TTS_MODEL,
            config_path=Config.TTS_CONFIG,
            enabled=Config.TTS_ENABLED
        )
        tts_service.set_volume(Config.TTS_VOLUME)
        
        ai_client = AIClient()
        prompt_engine = PromptEngine(user_memory=user_memory, ai_scraper=ai_scraper)
        state_manager = ChatStateManager()
        web_search = WebSearchService()
        database = DatabaseService()
        
        # Create main window with injected dependencies
        window = MainWindow(
            ai_client=ai_client,
            prompt_engine=prompt_engine,
            state_manager=state_manager,
            web_search=web_search,
            database=database,
            user_memory=user_memory,
            ai_scraper=ai_scraper,
            tts_service=tts_service
        )
        
        window.show()
        
        logger.info("Application started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception("Fatal error during application startup")
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
