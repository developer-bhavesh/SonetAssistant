"""
Utility functions and helpers.
"""
import re
from datetime import datetime
from typing import Optional

def format_timestamp(dt: datetime, format: str = "%H:%M") -> str:
    """Format datetime to string."""
    return dt.strftime(format)

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize string for use as filename."""
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')

def extract_code_blocks(text: str) -> list[tuple[Optional[str], str]]:
    """
    Extract code blocks from markdown text.
    Returns list of (language, code) tuples.
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or None, code.strip()) for lang, code in matches]
