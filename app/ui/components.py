"""Enhanced UI components with copyable code blocks."""
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
import qtawesome as qta
from app.models import Message, MessageRole
import re

class CodeBlock(QWidget):
    """Copyable code block widget."""
    
    def __init__(self, code: str, language: str = "", parent=None):
        super().__init__(parent)
        self.code = code
        self._setup_ui(language)
    
    def _setup_ui(self, language: str):
        """Setup code block UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with copy button
        header = QWidget()
        header.setStyleSheet("background-color: #1A1A1A; padding: 4px 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        lang_label = QLabel(language or "code")
        lang_label.setStyleSheet("color: #888; font-size: 11px;")
        
        copy_btn = QPushButton()
        copy_btn.setIcon(qta.icon('fa5s.copy', color='#888'))
        copy_btn.setFixedSize(24, 24)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
                border-radius: 4px;
            }
        """)
        copy_btn.clicked.connect(self._copy_code)
        
        header_layout.addWidget(lang_label)
        header_layout.addStretch()
        header_layout.addWidget(copy_btn)
        
        # Code content
        code_edit = QTextEdit()
        code_edit.setPlainText(self.code)
        code_edit.setReadOnly(True)
        code_edit.setStyleSheet("""
            QTextEdit {
                background-color: #0D0D0D;
                color: #E0E0E0;
                border: none;
                padding: 12px;
                font-family: 'Monospace', 'Courier New';
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        code_edit.setMaximumHeight(300)
        
        layout.addWidget(header)
        layout.addWidget(code_edit)
        
        self.setStyleSheet("""
            CodeBlock {
                border: 1px solid #2A2A2A;
                border-radius: 6px;
            }
        """)
    
    def _copy_code(self):
        """Copy code to clipboard."""
        QApplication.clipboard().setText(self.code)

class MessageBubble(QWidget):
    """Enhanced message bubble with code block support."""
    
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup message bubble UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Role label
        role_label = QLabel(self._get_role_display())
        role_font = QFont()
        role_font.setBold(True)
        role_font.setPointSize(10)
        role_label.setFont(role_font)
        role_label.setStyleSheet(self._get_role_color())
        
        layout.addWidget(role_label)
        
        # Parse and render content
        self._render_content(layout)
        
        self.setStyleSheet(self._get_bubble_style())
    
    def _render_content(self, layout: QVBoxLayout):
        """Parse and render content with code blocks."""
        content = self.message.content
        
        # Extract code blocks
        code_pattern = r'```(\w*)\n(.*?)```'
        parts = []
        last_end = 0
        
        for match in re.finditer(code_pattern, content, re.DOTALL):
            # Add text before code block
            if match.start() > last_end:
                parts.append(('text', content[last_end:match.start()]))
            
            # Add code block
            language = match.group(1)
            code = match.group(2).strip()
            parts.append(('code', code, language))
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(content):
            parts.append(('text', content[last_end:]))
        
        # Render parts
        if not parts:
            parts = [('text', content)]
        
        for part in parts:
            if part[0] == 'text':
                text_label = QLabel()
                text_label.setText(part[1])
                text_label.setWordWrap(True)
                text_label.setTextFormat(Qt.MarkdownText)
                text_label.setTextInteractionFlags(
                    Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
                )
                text_label.setOpenExternalLinks(True)
                text_label.setMaximumWidth(800)  # Prevent horizontal scroll
                text_label.setStyleSheet("""
                    QLabel {
                        padding: 4px;
                        line-height: 1.6;
                        font-size: 11pt;
                    }
                    QLabel a { 
                        color: #4A9EFF;
                        word-wrap: break-word;
                    }
                """)
                layout.addWidget(text_label)
            
            elif part[0] == 'code':
                code_block = CodeBlock(part[1], part[2])
                layout.addWidget(code_block)
    
    def _get_role_display(self) -> str:
        """Get display name for role."""
        return {
            MessageRole.USER: "👤 You",
            MessageRole.ASSISTANT: "🤖 Sonet",
            MessageRole.SYSTEM: "⚙️ System"
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
                    border-radius: 12px;
                    border-left: 4px solid #4A9EFF;
                    margin: 4px 0px;
                }
            """
        else:
            return """
                MessageBubble {
                    background-color: #1E2A38;
                    border-radius: 12px;
                    border-left: 4px solid #50C878;
                    margin: 4px 0px;
                }
            """

class LoadingIndicator(QWidget):
    """Loading indicator."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup loading indicator UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        label = QLabel("🤖 Sonet is thinking...")
        label.setStyleSheet("color: #50C878; font-style: italic; font-size: 13px;")
        layout.addWidget(label)
        
        self.setStyleSheet("""
            LoadingIndicator {
                background-color: #1E2A38;
                border-radius: 12px;
                border-left: 4px solid #50C878;
                margin: 4px 0px;
            }
        """)
