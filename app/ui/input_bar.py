"""Modern input bar component."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from app.ui.theme import theme_manager

class InputBar(QWidget):
    """Modern input bar with rounded text field and send button."""
    
    message_sent = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup input bar UI."""
        t = theme_manager.current_theme
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(12)
        
        # Input field
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Message Sonet...")
        self.input_field.setMaximumHeight(120)
        self.input_field.setMinimumHeight(52)
        
        font = QFont()
        font.setPointSize(14)
        self.input_field.setFont(font)
        
        self.input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {t.bg_input};
                border: 1px solid {t.border_light};
                border-radius: 12px;
                padding: 12px 16px;
                color: {t.text_primary};
            }}
            QTextEdit:focus {{
                border: 1px solid {t.accent_primary};
            }}
        """)
        
        # Send button
        self.send_btn = QPushButton()
        self.send_btn.setIcon(qta.icon('fa5s.arrow-up', color='#FFFFFF'))
        self.send_btn.setIconSize(Qt.Size(18, 18))
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setToolTip("Send message")
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t.accent_primary};
                border: none;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {t.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {t.accent_pressed};
            }}
            QPushButton:disabled {{
                background-color: {t.bg_tertiary};
            }}
        """)
        self.send_btn.clicked.connect(self._on_send)
        
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_btn, alignment=Qt.AlignBottom)
        
        self.setStyleSheet(f"""
            InputBar {{
                background-color: {t.bg_primary};
                border-top: 1px solid {t.border_light};
            }}
        """)
    
    def _on_send(self):
        """Handle send button click."""
        text = self.input_field.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.input_field.clear()
            self.input_field.setFocus()
    
    def set_enabled(self, enabled: bool):
        """Enable/disable input."""
        self.input_field.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
