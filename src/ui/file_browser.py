"""
File browser component for Process Dashboard.
"""

from textual.widget import Widget
from textual.widgets import Static
from pathlib import Path

class FileBrowser(Widget):
    """Simple file browser widget."""

    DEFAULT_CSS = """
    FileBrowser {
        height: 100%;
        border: solid green;
        background: #001100;
        color: #00ff00;
    }
    """

    def __init__(self):
        """Initialize file browser."""
        super().__init__()
        self._content = Static("File Browser\n(Coming soon...)")

    def compose(self):
        """Create child widgets."""
        yield self._content

