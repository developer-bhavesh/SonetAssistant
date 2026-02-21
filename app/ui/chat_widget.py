"""
Main chat widget with message display and input.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from app.ui.components import MessageBubble, LoadingIndicator
from app.models import Message, MessageRole

class ChatWidget(QWidget):
    """
    Main chat interface widget.
    Displays messages and handles user input.
    """
    
    message_sent = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loading_indicator = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup chat widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Messages area
        self.messages_area = self._create_messages_area()
        layout.addWidget(self.messages_area, stretch=1)
        
        # Input area
        input_widget = self._create_input_area()
        layout.addWidget(input_widget)
    
    def _create_messages_area(self) -> QScrollArea:
        """Create scrollable messages area."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Container for messages
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()
        
        scroll.setWidget(self.messages_container)
        return scroll
    
    def _create_input_area(self) -> QWidget:
        """Create message input area."""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #1E2A38;
                border-top: 1px solid #34495E;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Input field
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setMaximumHeight(120)
        self.input_field.setMinimumHeight(44)
        font = QFont()
        font.setPointSize(11)
        self.input_field.setFont(font)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 2px solid #34495E;
                border-radius: 8px;
                padding: 10px;
            }
            QTextEdit:focus {
                border: 2px solid #4A9EFF;
            }
        """)
        
        # Send button
        self.send_button = QPushButton()
        self.send_button.setIcon(qta.icon('fa5s.paper-plane', color='#ECF0F1'))
        self.send_button.setFixedSize(48, 48)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4A9EFF;
                border: none;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #5AAFFF;
            }
            QPushButton:pressed {
                background-color: #3A8EEF;
            }
            QPushButton:disabled {
                background-color: #34495E;
            }
        """)
        self.send_button.clicked.connect(self._on_send_clicked)
        
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button, alignment=Qt.AlignBottom)
        
        return widget
    
    def _on_send_clicked(self):
        """Handle send button click."""
        text = self.input_field.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.input_field.clear()
    
    def add_message(self, message: Message):
        """Add message bubble to chat."""
        bubble = MessageBubble(message)
        # Insert before stretch
        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1, 
            bubble
        )
        self._scroll_to_bottom()
    
    def show_loading(self):
        """Show loading indicator."""
        if not self.loading_indicator:
            self.loading_indicator = LoadingIndicator()
            self.messages_layout.insertWidget(
                self.messages_layout.count() - 1,
                self.loading_indicator
            )
            self._scroll_to_bottom()
    
    def hide_loading(self):
        """Hide loading indicator."""
        if self.loading_indicator:
            self.messages_layout.removeWidget(self.loading_indicator)
            self.loading_indicator.deleteLater()
            self.loading_indicator = None
    
    def clear_messages(self):
        """Clear all messages."""
        while self.messages_layout.count() > 1:  # Keep stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.hide_loading()
    
    def set_input_enabled(self, enabled: bool):
        """Enable/disable input controls."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
    
    def _scroll_to_bottom(self):
        """Scroll to bottom of messages."""
        scrollbar = self.messages_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
