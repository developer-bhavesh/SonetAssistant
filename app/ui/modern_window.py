"""Modern main window with ChatGPT-inspired UI."""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from app.config import Config
from app.ui.theme import theme_manager
from app.ui.sidebar import Sidebar
from app.ui.header import Header
from app.ui.chat_view import ChatView
from app.ui.input_bar import InputBar
from app.ui.message_bubble import MessageBubble
from app.services import AIClient, PromptEngine, ChatStateManager, WebSearchService, DatabaseService, TTSService
from app.models import MessageRole, Message

class ModernMainWindow(QMainWindow):
    """Modern main window with ChatGPT-inspired design."""
    
    def __init__(
        self,
        ai_client: AIClient,
        prompt_engine: PromptEngine,
        state_manager: ChatStateManager,
        web_search: WebSearchService,
        database: DatabaseService,
        user_memory,
        ai_scraper,
        tts_service: TTSService
    ):
        super().__init__()
        self.ai_client = ai_client
        self.prompt_engine = prompt_engine
        self.state_manager = state_manager
        self.web_search = web_search
        self.database = database
        self.user_memory = user_memory
        self.ai_scraper = ai_scraper
        self.tts_service = tts_service
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()
        
        # Load chat history at startup
        self._update_chat_history()
    
    def _setup_window(self):
        """Configure window."""
        self.setWindowTitle(Config.APP_NAME)
        self.resize(1400, 900)
        
        icon_path = Config.get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _setup_ui(self):
        """Setup UI components."""
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.header = Header()
        content_layout.addWidget(self.header)
        
        # Chat view
        self.chat_view = ChatView()
        self.chat_view.speak_requested.connect(self.tts_service.speak, Qt.UniqueConnection)
        content_layout.addWidget(self.chat_view, stretch=1)
        
        # Input bar
        self.input_bar = InputBar()
        content_layout.addWidget(self.input_bar)
        
        main_layout.addWidget(content, stretch=1)
        self.setCentralWidget(central)
    
    def _connect_signals(self):
        """Connect signals."""
        from PySide6.QtCore import Qt
        
        # Input bar
        self.input_bar.message_sent.connect(self._on_message_sent, Qt.UniqueConnection)
        
        # Header
        self.header.theme_toggled.connect(self._toggle_theme, Qt.UniqueConnection)
        self.header.model_changed.connect(self._on_model_changed, Qt.UniqueConnection)
        self.header.tts_toggled.connect(self.tts_service.set_enabled, Qt.UniqueConnection)
        
        # Sidebar
        self.sidebar.new_chat_clicked.connect(self._on_new_chat, Qt.UniqueConnection)
        
        # AI client
        self.ai_client.request_started.connect(self._on_request_started, Qt.UniqueConnection)
        self.ai_client.response_received.connect(self._on_response_received, Qt.UniqueConnection)
        self.ai_client.error_occurred.connect(self._on_error, Qt.UniqueConnection)
        
        # State manager
        self.state_manager.message_added.connect(self._on_message_added, Qt.UniqueConnection)
        self.state_manager.state_cleared.connect(self._on_state_cleared, Qt.UniqueConnection)
        self.state_manager.session_changed.connect(self._update_chat_history, Qt.UniqueConnection)
        
        # TTS service
        self.tts_service.speaking_started.connect(self._on_speaking_started, Qt.UniqueConnection)
        self.tts_service.speaking_finished.connect(self._on_speaking_finished, Qt.UniqueConnection)
    
    def _update_chat_history(self):
        """Update sidebar chat history."""
        # Load sessions from database
        sessions_data = self.database.list_sessions()
        
        # Clear existing items (except stretch)
        while self.sidebar.history_layout.count() > 1:
            item = self.sidebar.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add session items
        from app.ui.sidebar import ChatHistoryItem
        for session_id, title, updated_at in sessions_data[:20]:
            item = ChatHistoryItem(title)
            item.clicked.connect(lambda sid=session_id: self._load_session(sid))
            item.delete_clicked.connect(lambda sid=session_id, w=item: self._delete_session(sid, w))
            self.sidebar.history_layout.insertWidget(self.sidebar.history_layout.count() - 1, item)
    
    def _load_session(self, session_id):
        """Load a chat session."""
        session = self.database.load_session(session_id)
        if session:
            self.chat_view.clear_messages()
            for msg in session.messages:
                self.chat_view.add_message(msg)
            self.state_manager.current_session = session
    
    def _delete_session(self, session_id, widget):
        """Delete a chat session."""
        self.database.delete_session(session_id)
        self.sidebar.history_layout.removeWidget(widget)
        widget.deleteLater()
    
    def _on_message_sent(self, text: str):
        """Handle message sent."""
        # Auto-search detection
        search_keywords = ['how to', 'what is', 'explain', 'latest', 'newest', 'recent']
        needs_search = any(kw in text.lower() for kw in search_keywords)
        
        if text.startswith('/search '):
            self._handle_search(text[8:].strip())
            return
        
        if needs_search and '?' in text:
            self._handle_search(text)
            return
        
        # Normal chat - state_manager will emit signal to add to UI
        self.state_manager.add_message(MessageRole.USER, text)
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        self.ai_client.send_message(messages)
    
    def _handle_search(self, query: str):
        """Handle web search."""
        # Add user message first
        self.state_manager.add_message(MessageRole.USER, query)
        
        # Perform search
        results, source_urls = self.web_search.search(query)
        self.state_manager.set_search_context(results, source_urls)
        
        # Build messages for AI
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        
        if self.state_manager.search_context:
            search_msg = Message(
                role=MessageRole.USER,
                content=self.state_manager.search_context
            )
            messages.append(search_msg)
        
        self.ai_client.send_message(messages)
    
    def _on_request_started(self):
        """Handle request started."""
        self.chat_view.show_loading()
        self.input_bar.set_enabled(False)
    
    def _on_response_received(self, response: str):
        """Handle response received."""
        self.chat_view.hide_loading()
        self.input_bar.set_enabled(True)
        
        # Process AI scraping tools if present
        processed_response, tools_used = self.ai_scraper.process_ai_response(response)
        
        if tools_used:
            # If tools were used, send back to AI with results
            self.state_manager.add_message(MessageRole.ASSISTANT, processed_response)
            return
        
        # Add sources
        if self.state_manager.source_urls:
            processed_response += "\n\n📚 **Sources:** "
            links = []
            for url in self.state_manager.source_urls:
                try:
                    domain = url.split('/')[2].replace('www.', '')
                    links.append(f"[{domain}]({url})")
                except:
                    links.append(f"[link]({url})")
            processed_response += " • ".join(links)
        
        # Store interaction in memory
        last_user_msg = next((m.content for m in reversed(self.state_manager.current_session.messages) if m.role == MessageRole.USER), "")
        self.user_memory.extract_and_store(last_user_msg, processed_response)
        
        # Speak response
        self.tts_service.speak(processed_response)
        
        # Add message to state (will trigger UI update via signal)
        self.state_manager.add_message(MessageRole.ASSISTANT, processed_response)
        self.state_manager.clear_search_context()
        
        # Save session after each response
        self.database.save_session(self.state_manager.current_session)
        self._update_chat_history()
    
    def _on_error(self, error: str):
        """Handle error."""
        self.chat_view.hide_loading()
        self.input_bar.set_enabled(True)
        QMessageBox.critical(self, "Error", f"AI Error: {error}")
    
    def _on_message_added(self, message):
        """Handle message added."""
        if message.role not in (MessageRole.USER, MessageRole.ASSISTANT):
            return
        
        # Check if message already exists in UI to prevent duplicates
        for i in range(self.chat_view.messages_layout.count()):
            item = self.chat_view.messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageBubble):
                if item.widget().message.id == message.id:
                    return  # Already in UI
        
        self.chat_view.add_message(message)
    
    def _on_state_cleared(self):
        """Handle state cleared."""
        self.chat_view.clear_messages()
    
    def _on_new_chat(self):
        """Handle new chat."""
        # Save current session if it has messages
        if self.state_manager.current_session.messages:
            self.database.save_session(self.state_manager.current_session)
        
        self.state_manager.clear_conversation()
        self._update_chat_history()
    
    def _on_model_changed(self, model: str):
        """Handle model change."""
        # Update config and restart AI client
        pass
    
    def _on_speaking_started(self):
        """Handle TTS speaking started."""
        self.header.set_speaking(True)
    
    def _on_speaking_finished(self):
        """Handle TTS speaking finished."""
        self.header.set_speaking(False)
    
    def _toggle_theme(self):
        """Toggle theme - disabled."""
        pass
    
    def _apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(theme_manager.get_stylesheet())
    
    def _refresh_all_components(self):
        """Refresh all UI components after theme change."""
        # Store current messages
        messages = []
        for i in range(self.chat_view.messages_layout.count() - 1):
            item = self.chat_view.messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageBubble):
                messages.append(item.widget().message)
        
        # Get central widget and layout
        central = self.centralWidget()
        main_layout = central.layout()
        
        # Remove and delete all widgets
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear references
        self.sidebar = None
        self.header = None
        self.chat_view = None
        self.input_bar = None
        
        # Recreate all components
        self.sidebar = Sidebar()
        self.header = Header()
        self.chat_view = ChatView()
        self.input_bar = InputBar()
        
        # Reconnect signals
        self._connect_signals()
        
        # Rebuild layout
        main_layout.addWidget(self.sidebar)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.header)
        content_layout.addWidget(self.chat_view, stretch=1)
        content_layout.addWidget(self.input_bar)
        
        main_layout.addWidget(content, stretch=1)
        
        # Restore messages
        if messages:
            for msg in messages:
                self.chat_view.add_message(msg)
        
        # Restore chat history
        self._update_chat_history()
