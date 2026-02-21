"""Modern sidebar navigation component."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from app.ui.theme import theme_manager

class NavButton(QPushButton):
    """Navigation button with icon and label."""
    
    def __init__(self, icon_name: str, label: str, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.icon_name = icon_name
        self.is_active = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup button UI."""
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self.label_text)
        self._update_style()
    
    def set_active(self, active: bool):
        """Set button active state."""
        self.is_active = active
        self._update_style()
    
    def _update_style(self):
        """Update button style based on state."""
        t = theme_manager.current_theme
        
        if self.is_active:
            bg = t.bg_tertiary
            color = t.accent_primary
        else:
            bg = "transparent"
            color = t.text_secondary
        
        self.setIcon(qta.icon(self.icon_name, color=color))
        self.setIconSize(Qt.Size(20, 20))
        
        self.setStyleSheet(f"""
            NavButton {{
                background-color: {bg};
                border: none;
                border-radius: 8px;
                padding: 0px 12px;
                text-align: left;
                color: {color};
                font-size: 14px;
            }}
            NavButton:hover {{
                background-color: {t.bg_hover};
            }}
        """)
        self.setText(f"  {self.label_text}")

class Sidebar(QWidget):
    """Modern sidebar with navigation."""
    
    nav_changed = Signal(str)  # Emits: "chat", "lens", "automation", "settings"
    new_chat_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_nav = "chat"
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup sidebar UI."""
        t = theme_manager.current_theme
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # New chat button
        new_chat_btn = QPushButton()
        new_chat_btn.setIcon(qta.icon('fa5s.plus', color=t.text_primary))
        new_chat_btn.setIconSize(Qt.Size(16, 16))
        new_chat_btn.setText("  New chat")
        new_chat_btn.setFixedHeight(40)
        new_chat_btn.setCursor(Qt.PointingHandCursor)
        new_chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t.bg_tertiary};
                border: 1px solid {t.border_light};
                border-radius: 8px;
                padding: 0px 12px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {t.bg_hover};
            }}
        """)
        new_chat_btn.clicked.connect(self.new_chat_clicked.emit)
        layout.addWidget(new_chat_btn)
        
        layout.addSpacing(16)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("chat", "fa5s.comment", "Chat"),
            ("lens", "fa5s.camera", "Lens"),
            ("automation", "fa5s.terminal", "Automation"),
        ]
        
        for nav_id, icon, label in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, n=nav_id: self._on_nav_clicked(n))
            self.nav_buttons[nav_id] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Settings button at bottom
        settings_btn = NavButton("fa5s.cog", "Settings")
        settings_btn.clicked.connect(lambda: self._on_nav_clicked("settings"))
        self.nav_buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)
        
        # Set initial active
        self.nav_buttons["chat"].set_active(True)
        
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {t.bg_secondary};
                border-right: 1px solid {t.border_light};
            }}
        """)
    
    def _on_nav_clicked(self, nav_id: str):
        """Handle navigation click."""
        if nav_id == self.current_nav:
            return
        
        # Update active states
        for btn_id, btn in self.nav_buttons.items():
            btn.set_active(btn_id == nav_id)
        
        self.current_nav = nav_id
        self.nav_changed.emit(nav_id)
