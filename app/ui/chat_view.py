"""Modern chat view component."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from app.ui.message_bubble import MessageBubble
from app.ui.theme import theme_manager
from app.models import Message, MessageRole

class ChatView(QWidget):
    """Modern chat view with messages."""
    
    speak_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loading_label = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup chat view UI."""
        t = theme_manager.current_theme
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {t.bg_primary};
                border: none;
            }}
        """)
        
        # Messages container
        self.messages_container = QWidget()
        self.messages_container.setStyleSheet(f"background-color: {t.bg_primary};")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(24, 24, 24, 24)
        self.messages_layout.setSpacing(16)
        self.messages_layout.addStretch()
        
        scroll.setWidget(self.messages_container)
        layout.addWidget(scroll)
        
        self.scroll_area = scroll
        
        # Empty state
        self._show_empty_state()
    
    def add_message(self, message: Message):
        """Add message to chat."""
        if message.role in (MessageRole.USER, MessageRole.ASSISTANT):
            self._hide_empty_state()
            bubble = MessageBubble(message)
            
            # Connect speak signal
            if message.role == MessageRole.ASSISTANT:
                bubble.speak_requested.connect(self.speak_requested.emit)
            
            self.messages_layout.insertWidget(
                self.messages_layout.count() - 1,
                bubble
            )
            self._scroll_to_bottom()
    
    def show_loading(self):
        """Show loading indicator."""
        if not self.loading_label:
            t = theme_manager.current_theme
            self.loading_label = QLabel("Thinking...")
            font = QFont()
            font.setItalic(True)
            font.setPointSize(13)
            self.loading_label.setFont(font)
            self.loading_label.setStyleSheet(f"""
                QLabel {{
                    color: {t.text_secondary};
                    padding: 16px;
                }}
            """)
            self.messages_layout.insertWidget(
                self.messages_layout.count() - 1,
                self.loading_label
            )
            self._scroll_to_bottom()
    
    def hide_loading(self):
        """Hide loading indicator."""
        if self.loading_label:
            self.messages_layout.removeWidget(self.loading_label)
            self.loading_label.deleteLater()
            self.loading_label = None
    
    def clear_messages(self):
        """Clear all messages."""
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.hide_loading()
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state message."""
        t = theme_manager.current_theme
        
        if not hasattr(self, 'empty_label') or self.empty_label is None:
            self.empty_label = QLabel("How can I help you today?")
            font = QFont()
            font.setPointSize(20)
            font.setWeight(QFont.DemiBold)
            self.empty_label.setFont(font)
            self.empty_label.setAlignment(Qt.AlignCenter)
        
        self.empty_label.setStyleSheet(f"color: {t.text_secondary};")
        
        try:
            if self.empty_label.parent() is None:
                self.messages_layout.insertWidget(0, self.empty_label)
        except RuntimeError:
            self.empty_label = QLabel("How can I help you today?")
            font = QFont()
            font.setPointSize(20)
            font.setWeight(QFont.DemiBold)
            self.empty_label.setFont(font)
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.empty_label.setStyleSheet(f"color: {t.text_secondary};")
            self.messages_layout.insertWidget(0, self.empty_label)
    
    def _hide_empty_state(self):
        """Hide empty state message."""
        if hasattr(self, 'empty_label') and self.empty_label is not None:
            try:
                if self.empty_label.parent():
                    self.messages_layout.removeWidget(self.empty_label)
                    self.empty_label.setParent(None)
            except RuntimeError:
                pass
            self.empty_label = None
    
    def _scroll_to_bottom(self):
        """Scroll to bottom."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def scroll_to_bottom(self):
        """Public method to scroll to bottom."""
        self._scroll_to_bottom()
