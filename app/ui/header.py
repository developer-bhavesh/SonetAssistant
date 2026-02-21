"""Modern header component."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from app.ui.theme import theme_manager

class Header(QWidget):
    """Modern header with app name and controls."""
    
    settings_clicked = Signal()
    theme_toggled = Signal()
    model_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup header UI."""
        t = theme_manager.current_theme
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # App name
        app_label = QLabel("Sonet")
        font = QFont()
        font.setPointSize(16)
        font.setWeight(QFont.DemiBold)
        app_label.setFont(font)
        layout.addWidget(app_label)
        
        layout.addStretch()
        
        # Model selector
        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen3:8b", "qwen2.5:7b", "llama3.2:3b"])
        self.model_combo.setFixedWidth(150)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {t.bg_tertiary};
                border: 1px solid {t.border_light};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                background-color: {t.bg_hover};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t.bg_tertiary};
                border: 1px solid {t.border_light};
                selection-background-color: {t.bg_hover};
            }}
        """)
        self.model_combo.currentTextChanged.connect(self.model_changed.emit)
        layout.addWidget(self.model_combo)
        
        # Theme toggle
        theme_btn = QPushButton()
        theme_btn.setIcon(qta.icon('fa5s.moon', color=t.text_secondary))
        theme_btn.setIconSize(Qt.Size(18, 18))
        theme_btn.setFixedSize(36, 36)
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setToolTip("Toggle theme")
        theme_btn.clicked.connect(self.theme_toggled.emit)
        layout.addWidget(theme_btn)
        
        # Settings button
        settings_btn = QPushButton()
        settings_btn.setIcon(qta.icon('fa5s.cog', color=t.text_secondary))
        settings_btn.setIconSize(Qt.Size(18, 18))
        settings_btn.setFixedSize(36, 36)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)
        
        self.setStyleSheet(f"""
            Header {{
                background-color: {t.bg_primary};
                border-bottom: 1px solid {t.border_light};
            }}
        """)
