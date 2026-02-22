"""Modern collapseable sidebar with chat history."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QMenu, QInputDialog
from PySide6.QtCore import Qt, Signal, QSize
import qtawesome as qta
from app.ui.theme import theme_manager

class ChatHistoryItem(QWidget):
    """Chat history item with context menu."""
    
    clicked = Signal()
    delete_clicked = Signal()
    rename_clicked = Signal(str)
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI."""
        t = theme_manager.current_theme
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        
        # Chat button
        self.chat_btn = QPushButton(self.title)
        self.chat_btn.setFixedHeight(40)
        self.chat_btn.setCursor(Qt.PointingHandCursor)
        self.chat_btn.clicked.connect(self.clicked.emit)
        self.chat_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_btn.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.chat_btn, stretch=1)
        
        self._apply_theme()
    
    def _show_context_menu(self, pos):
        """Show context menu."""
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.chat_btn.mapToGlobal(pos))
        
        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Chat", "Enter new name:", text=self.title)
            if ok and new_name:
                self.title = new_name
                self.chat_btn.setText(new_name)
                self.rename_clicked.emit(new_name)
        elif action == delete_action:
            self.delete_clicked.emit()
    
    def _apply_theme(self):
        """Apply theme to components."""
        t = theme_manager.current_theme
        
        self.setStyleSheet(f"background-color: {t.bg_secondary};")
        
        self.chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 0px 12px;
                text-align: left;
                font-size: 13px;
                color: {t.text_secondary};
            }}
            QPushButton:hover {{
                background-color: {t.bg_hover};
                border: 1px solid {t.border_light};
                color: {t.text_primary};
            }}
        """)

class Sidebar(QWidget):
    """Collapseable sidebar with chat history."""
    
    new_chat_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.chat_items = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup sidebar UI."""
        t = theme_manager.current_theme
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)
        self.main_layout.setAlignment(Qt.AlignTop)
        
        # Toggle button container
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(qta.icon('fa5s.bars', color=t.text_primary))
        self.toggle_btn.setIconSize(QSize(16, 16))
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
        
        toggle_layout.addWidget(self.toggle_btn)
        toggle_layout.addStretch()
        
        self.main_layout.addWidget(toggle_container)
        
        # Content container
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # New chat button
        self.new_chat_btn = QPushButton()
        self.new_chat_btn.setIcon(qta.icon('fa5s.plus', color=t.text_primary))
        self.new_chat_btn.setIconSize(QSize(16, 16))
        self.new_chat_btn.setText("  New chat")
        self.new_chat_btn.setFixedHeight(40)
        self.new_chat_btn.setCursor(Qt.PointingHandCursor)
        self.new_chat_btn.clicked.connect(self.new_chat_clicked.emit)
        content_layout.addWidget(self.new_chat_btn)
        
        content_layout.addSpacing(8)
        
        # Chat history scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        
        # History container
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(2)
        self.history_layout.addStretch()
        
        self.scroll.setWidget(self.history_container)
        content_layout.addWidget(self.scroll)
        
        self.main_layout.addWidget(self.content_widget)
        
        self.setFixedWidth(240)
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply theme to all components."""
        t = theme_manager.current_theme
        
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {t.bg_secondary};
                border-right: 1px solid {t.border_light};
            }}
        """)
        
        self.toggle_btn.setIcon(qta.icon('fa5s.bars', color=t.text_primary))
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {t.border_light};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {t.bg_hover};
            }}
        """)
        
        self.new_chat_btn.setIcon(qta.icon('fa5s.plus', color=t.text_primary))
        self.new_chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {t.border_light};
                border-radius: 8px;
                padding: 0px 12px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                color: {t.text_primary};
            }}
            QPushButton:hover {{
                background-color: {t.bg_hover};
            }}
        """)
        
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {t.bg_secondary};
                border: none;
            }}
        """)
        
        self.history_container.setStyleSheet(f"background-color: {t.bg_secondary};")
        
        # Update all chat items
        for item in self.chat_items:
            item._apply_theme()
    
    def _toggle_sidebar(self):
        """Toggle sidebar collapse."""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.setFixedWidth(56 if self.is_collapsed else 240)
    
    def _delete_chat(self, item):
        """Delete chat item."""
        if item in self.chat_items:
            self.chat_items.remove(item)
        self.history_layout.removeWidget(item)
        item.deleteLater()
