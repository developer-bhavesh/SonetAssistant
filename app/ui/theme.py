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

# Dark theme (default)
DARK_THEME = Theme(
    bg_primary="#0D0D0D",
    bg_secondary="#1A1A1A",
    bg_tertiary="#2A2A2A",
    bg_input="#2F2F2F",
    bg_hover="#3A3A3A",
    
    text_primary="#ECECEC",
    text_secondary="#B4B4B4",
    text_tertiary="#8E8E8E",
    
    accent_primary="#10A37F",
    accent_hover="#1A9B7F",
    accent_pressed="#0E8B6F",
    
    border_light="#3A3A3A",
    border_medium="#4A4A4A",
    
    bubble_user="#2F2F2F",
    bubble_assistant="#1A1A1A",
    
    success="#10A37F",
    warning="#FFA500",
    error="#EF4444"
)

# Light theme
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
        self.current_theme = DARK_THEME
        self.is_dark = True
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.is_dark = not self.is_dark
        self.current_theme = DARK_THEME if self.is_dark else LIGHT_THEME
    
    def get_stylesheet(self) -> str:
        """Get complete application stylesheet."""
        t = self.current_theme
        return f"""
            QMainWindow {{
                background-color: {t.bg_primary};
            }}
            
            QWidget {{
                color: {t.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
                width: 8px;
                border: none;
            }}
            
            QScrollBar::handle:vertical {{
                background: {t.border_medium};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {t.text_tertiary};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """

theme_manager = ThemeManager()
