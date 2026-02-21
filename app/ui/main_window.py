"""
Main application window.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, 
    QMenu, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
import qtawesome as qta
from app.config import Config
from app.ui.chat_widget import ChatWidget
from app.services import AIClient, PromptEngine, ChatStateManager
from app.models import MessageRole

class MainWindow(QMainWindow):
    """
    Main application window with dependency injection.
    Coordinates UI and services.
    """
    
    def __init__(
        self,
        ai_client: AIClient,
        prompt_engine: PromptEngine,
        state_manager: ChatStateManager
    ):
        super().__init__()
        self.ai_client = ai_client
        self.prompt_engine = prompt_engine
        self.state_manager = state_manager
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Set app icon if available
        icon_path = Config.get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D1B2A;
            }
            QMenuBar {
                background-color: #1E2A38;
                color: #ECF0F1;
                border-bottom: 1px solid #34495E;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #2C3E50;
                border-radius: 4px;
            }
            QMenu {
                background-color: #1E2A38;
                color: #ECF0F1;
                border: 1px solid #34495E;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #2C3E50;
            }
            QStatusBar {
                background-color: #1E2A38;
                color: #95A5A6;
                border-top: 1px solid #34495E;
            }
        """)
    
    def _setup_ui(self):
        """Setup UI components."""
        # Menu bar
        self._create_menu_bar()
        
        # Central widget
        self.chat_widget = ChatWidget()
        self.setCentralWidget(self.chat_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("Ready")
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction(qta.icon('fa5s.plus', color='#ECF0F1'), "&New Chat", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_chat)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction(qta.icon('fa5s.times', color='#ECF0F1'), "&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction(qta.icon('fa5s.info-circle', color='#ECF0F1'), "&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Chat widget signals
        self.chat_widget.message_sent.connect(self._on_message_sent)
        
        # AI client signals
        self.ai_client.request_started.connect(self._on_request_started)
        self.ai_client.response_received.connect(self._on_response_received)
        self.ai_client.error_occurred.connect(self._on_error)
        
        # State manager signals
        self.state_manager.message_added.connect(self._on_message_added)
        self.state_manager.state_cleared.connect(self._on_state_cleared)
    
    def _on_message_sent(self, text: str):
        """Handle user message sent."""
        # Add user message to state
        self.state_manager.add_message(MessageRole.USER, text)
        
        # Build messages with system prompt
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        
        # Send to AI
        self.ai_client.send_message(messages)
    
    def _on_request_started(self):
        """Handle AI request started."""
        self.chat_widget.show_loading()
        self.chat_widget.set_input_enabled(False)
        self._update_status("Waiting for response...")
    
    def _on_response_received(self, response: str):
        """Handle AI response received."""
        self.chat_widget.hide_loading()
        self.chat_widget.set_input_enabled(True)
        
        # Add assistant message to state
        self.state_manager.add_message(MessageRole.ASSISTANT, response)
        
        self._update_status("Ready")
    
    def _on_error(self, error: str):
        """Handle AI error."""
        self.chat_widget.hide_loading()
        self.chat_widget.set_input_enabled(True)
        
        QMessageBox.critical(self, "Error", f"AI Error: {error}")
        self._update_status("Error occurred")
    
    def _on_message_added(self, message):
        """Handle message added to state."""
        # Only show user and assistant messages
        if message.role in (MessageRole.USER, MessageRole.ASSISTANT):
            self.chat_widget.add_message(message)
    
    def _on_state_cleared(self):
        """Handle state cleared."""
        self.chat_widget.clear_messages()
        self._update_status("New conversation started")
    
    def _on_new_chat(self):
        """Handle new chat action."""
        reply = QMessageBox.question(
            self,
            "New Chat",
            "Start a new conversation? Current chat will be cleared.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.state_manager.clear_conversation()
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {Config.APP_NAME}",
            f"""<h3>{Config.APP_NAME}</h3>
            <p>Version {Config.APP_VERSION}</p>
            <p>A professional Linux desktop AI assistant built with Python and PySide6.</p>
            <p>Specialized in Linux system administration, troubleshooting, and development.</p>
            """
        )
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_bar.showMessage(message)
