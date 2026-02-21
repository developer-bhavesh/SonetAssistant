"""Modern message bubble component."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta
from app.models import Message, MessageRole
from app.ui.theme import theme_manager
import re

class MessageBubble(QWidget):
    """Modern message bubble."""
    
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup message bubble UI."""
        t = theme_manager.current_theme
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Role header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        role_label = QLabel(self._get_role_name())
        role_font = QFont()
        role_font.setWeight(QFont.DemiBold)
        role_font.setPointSize(13)
        role_label.setFont(role_font)
        role_label.setStyleSheet(f"color: {t.text_primary};")
        
        header_layout.addWidget(role_label)
        header_layout.addStretch()
        
        # Copy button for assistant messages
        if self.message.role == MessageRole.ASSISTANT:
            copy_btn = QPushButton()
            copy_btn.setIcon(qta.icon('fa5s.copy', color=t.text_tertiary))
            copy_btn.setIconSize(Qt.Size(14, 14))
            copy_btn.setFixedSize(28, 28)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setToolTip("Copy")
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.message.content))
            header_layout.addWidget(copy_btn)
        
        layout.addWidget(header)
        
        # Message content
        content_label = QLabel()
        content_label.setText(self.message.content)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.MarkdownText)
        content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
        )
        content_label.setOpenExternalLinks(True)
        
        content_font = QFont()
        content_font.setPointSize(13)
        content_label.setFont(content_font)
        
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {t.text_primary};
                line-height: 1.6;
            }}
            QLabel a {{
                color: {t.accent_primary};
            }}
        """)
        
        layout.addWidget(content_label)
        
        # Styling
        bg_color = t.bubble_user if self.message.role == MessageRole.USER else t.bubble_assistant
        self.setStyleSheet(f"""
            MessageBubble {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
    
    def _get_role_name(self) -> str:
        """Get role display name."""
        return {
            MessageRole.USER: "You",
            MessageRole.ASSISTANT: "Sonet",
            MessageRole.SYSTEM: "System"
        }.get(self.message.role, "Unknown")
