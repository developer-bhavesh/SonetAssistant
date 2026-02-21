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
from app.services import AIClient, PromptEngine, ChatStateManager, WebSearchService, DatabaseService
from app.models import MessageRole, Message

class ModernMainWindow(QMainWindow):
    """Modern main window with ChatGPT-inspired design."""
    
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
        self._apply_theme()
    
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
        content_layout.addWidget(self.chat_view, stretch=1)
        
        # Input bar
        self.input_bar = InputBar()
        content_layout.addWidget(self.input_bar)
        
        main_layout.addWidget(content, stretch=1)
        self.setCentralWidget(central)
    
    def _connect_signals(self):
        """Connect signals."""
        # Input bar
        self.input_bar.message_sent.connect(self._on_message_sent)
        
        # Header
        self.header.theme_toggled.connect(self._toggle_theme)
        self.header.model_changed.connect(self._on_model_changed)
        
        # Sidebar
        self.sidebar.new_chat_clicked.connect(self._on_new_chat)
        
        # AI client
        self.ai_client.request_started.connect(self._on_request_started)
        self.ai_client.response_received.connect(self._on_response_received)
        self.ai_client.error_occurred.connect(self._on_error)
        
        # State manager
        self.state_manager.message_added.connect(self._on_message_added)
        self.state_manager.state_cleared.connect(self._on_state_cleared)
    
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
        
        # Normal chat
        self.state_manager.add_message(MessageRole.USER, text)
        conversation = self.state_manager.get_conversation_history()
        messages = self.prompt_engine.build_messages(conversation)
        self.ai_client.send_message(messages)
    
    def _handle_search(self, query: str):
        """Handle web search."""
        results, source_urls = self.web_search.search(query)
        self.state_manager.set_search_context(results, source_urls)
        self.state_manager.add_message(MessageRole.USER, query)
        
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
        
        # Add sources
        if self.state_manager.source_urls:
            response += "\\n\\n📚 **Sources:** "
            links = []
            for url in self.state_manager.source_urls:
                try:
                    domain = url.split('/')[2].replace('www.', '')
                    links.append(f"[{domain}]({url})")
                except:
                    links.append(f"[link]({url})")
            response += " • ".join(links)
        
        self.state_manager.add_message(MessageRole.ASSISTANT, response)
        self.state_manager.clear_search_context()
    
    def _on_error(self, error: str):
        """Handle error."""
        self.chat_view.hide_loading()
        self.input_bar.set_enabled(True)
        QMessageBox.critical(self, "Error", f"AI Error: {error}")
    
    def _on_message_added(self, message):
        """Handle message added."""
        if message.role in (MessageRole.USER, MessageRole.ASSISTANT):
            self.chat_view.add_message(message)
    
    def _on_state_cleared(self):
        """Handle state cleared."""
        self.chat_view.clear_messages()
    
    def _on_new_chat(self):
        """Handle new chat."""
        self.state_manager.clear_conversation()
    
    def _on_model_changed(self, model: str):
        """Handle model change."""
        # Update config and restart AI client
        pass
    
    def _toggle_theme(self):
        """Toggle theme."""
        theme_manager.toggle_theme()
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(theme_manager.get_stylesheet())
        # Force refresh all widgets
        self.update()
