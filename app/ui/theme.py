"""Centralized theme system for light and dark modes."""
from dataclasses import dataclass
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

@dataclass
class Theme:
    """Theme configuration."""
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_input: str
    bg_hover: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_tertiary: str
    
    # Accent colors
    accent_primary: str
    accent_hover: str
    accent_pressed: str
    
    # Border colors
    border_light: str
    border_medium: str
    
    # Message bubble colors
    bubble_user: str
    bubble_assistant: str
    
    # Semantic colors
    success: str
    warning: str
    error: str

# Light theme (default)
LIGHT_THEME = Theme(
    bg_primary="#FFFFFF",
    bg_secondary="#F7F7F8",
    bg_tertiary="#ECECF1",
    bg_input="#FFFFFF",
    bg_hover="#F0F0F0",
    
    text_primary="#0D0D0D",
    text_secondary="#565869",
    text_tertiary="#8E8EA0",
    
    accent_primary="#10A37F",
    accent_hover="#1A9B7F",
    accent_pressed="#0E8B6F",
    
    border_light="#D1D5DB",
    border_medium="#9CA3AF",
    
    bubble_user="#F7F7F8",
    bubble_assistant="#FFFFFF",
    
    success="#10A37F",
    warning="#F59E0B",
    error="#EF4444"
)

class ThemeManager:
    """Manages application theme."""
    
    def __init__(self):
        self.current_theme = LIGHT_THEME
        self.is_dark = False
        self._observers = []
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        # Only light theme available
        pass
    
    def add_observer(self, callback):
        """Add theme change observer."""
        self._observers.append(callback)
    
    def _notify_observers(self):
        """Notify all observers of theme change."""
        for callback in self._observers:
            callback()
    
    def get_stylesheet(self) -> str:
        """Get complete application stylesheet."""
        t = self.current_theme
        return f"""
            * {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            }}
            
            QMainWindow {{
                background-color: {t.bg_primary};
            }}
            
            QWidget {{
                color: {t.text_primary};
            }}
            
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 6px;
                color: {t.text_primary};
            }}
            
            QPushButton:hover {{
                background-color: {t.bg_hover};
            }}
            
            QPushButton:pressed {{
                background-color: {t.bg_tertiary};
            }}
            
            QScrollBar:vertical {{
                background: {t.bg_primary};
                width: 10px;
                border: none;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {t.border_medium};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {t.text_tertiary};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

theme_manager = ThemeManager()
