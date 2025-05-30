"""
File selection dialog for Process Dashboard.

Provides a terminal-based file browser for selecting files and directories.
"""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    DirectoryTree, Button, Input, Label, Static
)
from textual.message import Message
from textual.binding import Binding
from pathlib import Path
from typing import Optional, List

class FileDialog(ModalScreen):
    """Modal file selection dialog."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("ctrl+h", "toggle_hidden", "Toggle Hidden"),
    ]

    DEFAULT_CSS = """
    FileDialog {
        align: center middle;
    }

    #dialog-container {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $background;
    }

    #header {
        height: 3;
        padding: 1;
        background: $accent;
    }

    DirectoryTree {
        height: 100%;
        border: solid $accent;
        scrollbar-color: $accent;
    }

    #footer {
        height: 3;
        padding: 1;
    }

    Input {
        width: 100%;
        margin: 1;
    }

    Button {
        margin: 1;
    }

    #error-message {
        color: $error;
        margin: 1;
    }
    """

    class FileSelected(Message):
        """Message emitted when file is selected."""
        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    def __init__(
        self,
        title: str = "Select File",
        start_dir: Optional[Path] = None,
        file_pattern: Optional[str] = None,
        save_mode: bool = False
    ):
        """Initialize file dialog.
        
        Args:
            title: Dialog title
            start_dir: Starting directory
            file_pattern: File pattern to filter (e.g., "*.yaml")
            save_mode: Whether dialog is for saving files
        """
        super().__init__()
        self.title = title
        self.start_dir = start_dir or Path.home()
        self.file_pattern = file_pattern
        self.save_mode = save_mode
        self.show_hidden = False

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="dialog-container"):
            # Header
            with Horizontal(id="header"):
                yield Label(self.title)
            
            # Directory tree
            yield DirectoryTree(str(self.start_dir), id="file-tree")
            
            # File name input (for save mode)
            if self.save_mode:
                with Horizontal():
                    yield Label("File name:")
                    yield Input(id="file-name")
            
            # Footer
            with Horizontal(id="footer"):
                yield Button("Select", variant="primary", id="select")
                yield Button("Cancel", id="cancel")
            
            yield Static(id="error-message")

    def on_mount(self) -> None:
        """Handle dialog mount."""
        # Set up directory tree
        tree = self.query_one(DirectoryTree)
        if self.file_pattern:
            tree.filter = self.file_pattern

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        if not self.save_mode:
            self.selected_path = Path(event.path)
            self.action_select()

    def action_toggle_hidden(self) -> None:
        """Toggle display of hidden files."""
        self.show_hidden = not self.show_hidden
        tree = self.query_one(DirectoryTree)
        tree.show_hidden = self.show_hidden

    def action_select(self) -> None:
        """Handle file selection."""
        try:
            if self.save_mode:
                # Get file name from input
                file_name = self.query_one("#file-name", Input).value
                if not file_name:
                    self.show_error("File name required")
                    return
                
                # Get selected directory
                tree = self.query_one(DirectoryTree)
                if tree.selected_node:
                    directory = Path(tree.selected_node.data.path)
                    if not directory.is_dir():
                        directory = directory.parent
                else:
                    directory = self.start_dir
                
                # Create full path
                self.selected_path = directory / file_name
                
                # Check if file exists
                if self.selected_path.exists():
                    # TODO: Add overwrite confirmation
                    pass
            
            # Validate selected path
            if not self.selected_path:
                self.show_error("No file selected")
                return
            
            # Emit selection message
            self.post_message(self.FileSelected(self.selected_path))
            self.app.pop_screen()
            
        except Exception as e:
            self.show_error(f"Selection error: {e}")

    def action_cancel(self) -> None:
        """Cancel file selection."""
        self.app.pop_screen()

    def show_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message
        """
        self.query_one("#error-message").update(message)

class FileOpen(FileDialog):
    """File open dialog."""

    def __init__(
        self,
        title: str = "Open File",
        start_dir: Optional[Path] = None,
        file_pattern: Optional[str] = None
    ):
        """Initialize file open dialog.
        
        Args:
            title: Dialog title
            start_dir: Starting directory
            file_pattern: File pattern to filter
        """
        super().__init__(
            title=title,
            start_dir=start_dir,
            file_pattern=file_pattern,
            save_mode=False
        )

class FileSave(FileDialog):
    """File save dialog."""

    def __init__(
        self,
        title: str = "Save File",
        start_dir: Optional[Path] = None,
        file_pattern: Optional[str] = None
    ):
        """Initialize file save dialog.
        
        Args:
            title: Dialog title
            start_dir: Starting directory
            file_pattern: File pattern to filter
        """
        super().__init__(
            title=title,
            start_dir=start_dir,
            file_pattern=file_pattern,
            save_mode=True
        )
