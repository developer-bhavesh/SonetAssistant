"""
Reusable UI components for chat interface.
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from app.models import Message, MessageRole

class MessageBubble(QWidget):
    """Individual message bubble component."""
    
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup message bubble UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Role label
        role_label = QLabel(self._get_role_display())
        role_font = QFont()
        role_font.setBold(True)
        role_font.setPointSize(9)
        role_label.setFont(role_font)
        role_label.setStyleSheet(self._get_role_color())
        
        # Message content with rich text support
        content_label = QLabel()
        content_label.setText(self.message.content)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.MarkdownText)
        content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse
        )
        content_label.setOpenExternalLinks(True)
        content_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                line-height: 1.5;
                font-size: 13px;
            }
        """)
        
        layout.addWidget(role_label)
        layout.addWidget(content_label)
        
        # Styling based on role
        self.setStyleSheet(self._get_bubble_style())
    
    def _get_role_display(self) -> str:
        """Get display name for role."""
        return {
            MessageRole.USER: "You",
            MessageRole.ASSISTANT: "Sonet",
            MessageRole.SYSTEM: "System"
        }.get(self.message.role, "Unknown")
    
    def _get_role_color(self) -> str:
        """Get color for role label."""
        return {
            MessageRole.USER: "color: #4A9EFF;",
            MessageRole.ASSISTANT: "color: #50C878;",
            MessageRole.SYSTEM: "color: #FFA500;"
        }.get(self.message.role, "color: #FFFFFF;")
    
    def _get_bubble_style(self) -> str:
        """Get bubble background style."""
        if self.message.role == MessageRole.USER:
            return """
                MessageBubble {
                    background-color: #2C3E50;
                    border-radius: 8px;
                    border-left: 3px solid #4A9EFF;
                }
            """
        else:
            return """
                MessageBubble {
                    background-color: #1E2A38;
                    border-radius: 8px;
                    border-left: 3px solid #50C878;
                }
            """

class LoadingIndicator(QWidget):
    """Loading indicator for AI responses."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup loading indicator UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel("Sonet is thinking...")
        label.setStyleSheet("color: #50C878; font-style: italic;")
        layout.addWidget(label)
        
        self.setStyleSheet("""
            LoadingIndicator {
                background-color: #1E2A38;
                border-radius: 8px;
                border-left: 3px solid #50C878;
            }
        """)
