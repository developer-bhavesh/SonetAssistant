"""Session sidebar for managing multiple conversations."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from datetime import datetime

class SessionSidebar(QWidget):
    """Sidebar for session management."""
    
    session_selected = Signal(str)  # session_id
    new_session_requested = Signal()
    session_deleted = Signal(str)  # session_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #1E2A38; padding: 12px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        title = QLabel("Sessions")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        
        new_btn = QPushButton()
        new_btn.setIcon(qta.icon('fa5s.plus', color='#ECF0F1'))
        new_btn.setFixedSize(32, 32)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A9EFF;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover { background-color: #5AAFFF; }
        """)
        new_btn.clicked.connect(self.new_session_requested.emit)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_btn)
        
        # Session list
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                background-color: #0D1B2A;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #1E2A38;
                color: #ECF0F1;
            }
            QListWidget::item:selected {
                background-color: #2C3E50;
            }
            QListWidget::item:hover {
                background-color: #1E2A38;
            }
        """)
        self.session_list.itemClicked.connect(self._on_item_clicked)
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(header)
        layout.addWidget(self.session_list)
        
        self.setStyleSheet("background-color: #0D1B2A;")
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
    
    def add_session(self, session_id: str, title: str, updated_at: datetime):
        """Add session to list."""
        item = QListWidgetItem(f"{title}\n{self._format_time(updated_at)}")
        item.setData(Qt.UserRole, session_id)
        self.session_list.insertItem(0, item)
    
    def update_sessions(self, sessions: list[tuple[str, str, datetime]]):
        """Update session list."""
        self.session_list.clear()
        for session_id, title, updated_at in sessions:
            self.add_session(session_id, title, updated_at)
    
    def _format_time(self, dt: datetime) -> str:
        """Format datetime for display."""
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            return dt.strftime("%H:%M")
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return dt.strftime("%A")
        else:
            return dt.strftime("%b %d")
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click."""
        session_id = item.data(Qt.UserRole)
        self.session_selected.emit(session_id)
    
    def _show_context_menu(self, pos):
        """Show context menu for session."""
        item = self.session_list.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        delete_action = menu.addAction(qta.icon('fa5s.trash', color='#E74C3C'), "Delete")
        
        action = menu.exec(self.session_list.mapToGlobal(pos))
        if action == delete_action:
            session_id = item.data(Qt.UserRole)
            self.session_deleted.emit(session_id)
            self.session_list.takeItem(self.session_list.row(item))
