"""
File browser component for Process Dashboard.
"""

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from enum import Enum
import os

class ViewMode(Enum):
    DETAILS = "details"
    ICONS = "icons"
    LIST = "list"

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

    def __init__(self) -> None:
        """Initialize file browser."""
        super().__init__()
        self.current_path = os.getcwd()
        self._content = Static("File Browser\n(Coming soon...)")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield self._content

