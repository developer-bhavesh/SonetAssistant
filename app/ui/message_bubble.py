"""Modern message bubble component."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication, QSizePolicy, QTextEdit
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
import qtawesome as qta
import re
from app.models import Message, MessageRole
from app.ui.theme import theme_manager

class MessageBubble(QWidget):
    """Modern message bubble."""
    
    speak_requested = Signal(str)
    
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup message bubble UI."""
        t = theme_manager.current_theme
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 16, 20, 16)
        container_layout.setSpacing(8)
        
        # Role header
        header_layout = QHBoxLayout()
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
            # Speak button
            speak_btn = QPushButton()
            speak_btn.setIcon(qta.icon('fa5s.volume-up', color=t.text_tertiary))
            speak_btn.setIconSize(QSize(14, 14))
            speak_btn.setFixedSize(28, 28)
            speak_btn.setCursor(Qt.PointingHandCursor)
            speak_btn.setToolTip("Speak")
            speak_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {t.bg_hover};
                }}
            """)
            speak_btn.clicked.connect(lambda: self.speak_requested.emit(self.message.content))
            header_layout.addWidget(speak_btn)
            
            # Copy button
            copy_btn = QPushButton()
            copy_btn.setIcon(qta.icon('fa5s.copy', color=t.text_tertiary))
            copy_btn.setIconSize(QSize(14, 14))
            copy_btn.setFixedSize(28, 28)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setToolTip("Copy")
            copy_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {t.bg_hover};
                }}
            """)
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.message.content))
            header_layout.addWidget(copy_btn)
        
        container_layout.addLayout(header_layout)
        
        # Message content
        content_label = QLabel()
        content_label.setText(self.message.content)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.MarkdownText)
        content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
        )
        content_label.setOpenExternalLinks(True)
        content_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        content_font = QFont()
        content_font.setPointSize(13)
        content_label.setFont(content_font)
        
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {t.text_primary};
                background-color: transparent;
            }}
        """)
        
        container_layout.addWidget(content_label)
        
        # Styling
        bg_color = t.bubble_user if self.message.role == MessageRole.USER else t.bubble_assistant
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
        """)
        
        main_layout.addWidget(container)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def _get_role_name(self) -> str:
        """Get role display name."""
        return {
            MessageRole.USER: "You",
            MessageRole.ASSISTANT: "Sonet",
            MessageRole.SYSTEM: "System"
        }.get(self.message.role, "Unknown")
