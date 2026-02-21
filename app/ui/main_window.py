"""
Main application window.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, 
    QMenu, QMessageBox, QStatusBar, QHBoxLayout, QSplitter
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
import qtawesome as qta
from app.config import Config
from app.ui.chat_widget import ChatWidget
from app.ui.session_sidebar import SessionSidebar
from app.services import AIClient, PromptEngine, ChatStateManager, WebSearchService, DatabaseService
from app.models import MessageRole, Message

class MainWindow(QMainWindow):
    """
    Main application window with dependency injection.
    Coordinates UI and services.
    """
    
    def __init__(
        self,
        ai_client: AIClient,
        prompt_engine: PromptEngine,
        state_manager: ChatStateManager,
        web_search: WebSearchService,
        database: DatabaseService
    ):
        super().__init__()
        self.ai_client = ai_client
        self.prompt_engine = prompt_engine
        self.state_manager = state_manager
        self.web_search = web_search
        self.database = database
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._load_sessions()
    
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
        
        # Central widget with splitter
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Session sidebar
        self.sidebar = SessionSidebar()
        splitter.addWidget(self.sidebar)
        
        # Chat widget
        self.chat_widget = ChatWidget()
        splitter.addWidget(self.chat_widget)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        self.setCentralWidget(central)
        
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
        
        # Sidebar signals
        self.sidebar.session_selected.connect(self._on_session_selected)
        self.sidebar.new_session_requested.connect(self._on_new_chat)
        self.sidebar.session_deleted.connect(self._on_session_deleted)
    
    def _on_message_sent(self, text: str):
        """Handle user message sent."""
        # Intelligent search detection
        search_keywords = ['how to', 'what is', 'explain', 'tutorial', 'guide', 'best way', 'latest']
        needs_search = any(keyword in text.lower() for keyword in search_keywords)
        
        # Explicit search command
        if text.startswith('/search '):
            query = text[8:].strip()
            if query:
                self._handle_search(query)
            return
        
        # Auto-search for questions
        if needs_search and '?' in text:
            self._handle_search(text)
            return
        
        # Normal chat
        self.state_manager.add_message(MessageRole.USER, text)
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        self.ai_client.send_message(messages)
    
    def _handle_search(self, query: str):
        """Handle web search command."""
        self._update_status(f"Searching: {query}...")
        
        # Perform search with content extraction
        results, source_urls = self.web_search.search(query)
        
        # Store search context
        self.state_manager.set_search_context(results, source_urls)
        
        # Add user query
        self.state_manager.add_message(MessageRole.USER, query)
        
        # Build messages with system prompt
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        
        # Add search context as a separate user message (AI will see this as additional context)
        if self.state_manager.search_context:
            search_context_msg = Message(
                role=MessageRole.USER,
                content=self.state_manager.search_context
            )
            messages.append(search_context_msg)
        
        # Send to AI
        self.ai_client.send_message(messages)
        self._update_status("Waiting for AI response...")
    
    def _on_request_started(self):
        """Handle AI request started."""
        self.chat_widget.show_loading()
        self.chat_widget.set_input_enabled(False)
        self._update_status("Waiting for response...")
    
    def _on_response_received(self, response: str):
        """Handle AI response received."""
        self.chat_widget.hide_loading()
        self.chat_widget.set_input_enabled(True)
        
        # Add compact source links at bottom
        if self.state_manager.source_urls:
            response += "\n\n---\n📚 **Sources:** "
            source_links = []
            for url in self.state_manager.source_urls:
                # Extract domain name
                try:
                    domain = url.split('/')[2].replace('www.', '')
                    source_links.append(f"[{domain}]({url})")
                except:
                    source_links.append(f"[link]({url})")
            response += " • ".join(source_links)
        
        # Add assistant message to state
        self.state_manager.add_message(MessageRole.ASSISTANT, response)
        
        # Clear search context after response
        self.state_manager.clear_search_context()
        
        # Auto-save session
        self._save_current_session()
        
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
        self._save_current_session()
        self._update_status("New conversation started")
    
    def _load_sessions(self):
        """Load sessions from database."""
        sessions = self.database.list_sessions()
        self.sidebar.update_sessions(sessions)
    
    def _save_current_session(self):
        """Save current session to database."""
        session = self.state_manager.get_current_session()
        if session.messages:  # Only save if has messages
            self.database.save_session(session)
            self._load_sessions()
    
    def _on_session_selected(self, session_id: str):
        """Handle session selection."""
        # Save current session first
        self._save_current_session()
        
        # Load selected session
        session = self.database.load_session(session_id)
        if session:
            self.state_manager.current_session = session
            self.chat_widget.clear_messages()
            for msg in session.messages:
                if msg.role in (MessageRole.USER, MessageRole.ASSISTANT):
                    self.chat_widget.add_message(msg)
            self._update_status(f"Loaded: {session.title}")
    
    def _on_session_deleted(self, session_id: str):
        """Handle session deletion."""
        self.database.delete_session(session_id)
        self._update_status("Session deleted")
    
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
