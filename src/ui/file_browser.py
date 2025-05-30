"""
Matrix-themed file browser with multiple view modes and navigation capabilities.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import os
import pwd
import grp
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import (
    Static, Button, Select, Input, DataTable,
    Label, DirectoryTree, TabbedContent, TabPane
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.events import Click
from textual import on
from textual.coordinate import Coordinate

from rich.text import Text
from rich.table import Table
from rich import box
from rich.style import Style

@dataclass
class FileInfo:
    """Information about a file or directory."""
    path: Path
    name: str
    size: int
    modified: datetime
    owner: str
    group: str
    permissions: str
    is_dir: bool
    icon: str

class ViewMode(Enum):
    """Available file browser view modes."""
    DETAILS = "Details"
    ICONS = "Icons"
    LIST = "List"

class SortBy(Enum):
    """Available sort fields."""
    NAME = "Name"
    SIZE = "Size"
    MODIFIED = "Modified"
    TYPE = "Type"

class FileBrowser(Container):
    """Matrix-themed file browser widget with multiple view modes."""
    
    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "select_entry", "Select", show=False),
        Binding("backspace", "parent_directory", "Back", show=False),
    ]

    current_path = reactive(Path.home())
    view_mode = reactive(ViewMode.DETAILS)
    sort_by = reactive(SortBy.NAME)
    sort_reverse = reactive(False)
    filter_text = reactive("")
    page = reactive(0)
    items_per_page = reactive(50)
    selected_path: Optional[Path] = reactive(None)
    
    DEFAULT_CSS = """
    FileBrowser {
        height: 100%;
        width: 100%;
        background: #000000;
    }

    #toolbar {
        dock: top;
        height: 3;
        background: #001100;
        padding: 0 1;
    }

    #path-display {
        background: #001100;
        color: #00ff00;
        padding: 0 1;
        height: 1;
    }

    .file-grid {
        grid-size: 4;
        grid-gutter: 1;
        padding: 1;
    }

    .file-icon {
        width: 15;
        height: 7;
        content-align: center middle;
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    .file-icon:hover {
        background: #002200;
        border: solid #00ff00;
    }

    .file-icon.selected {
        background: #003300;
        border: solid #00ff00;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: #001100;
        color: #00ff00;
        padding: 0 1;
    }

    Select {
        width: 15;
    }

    Input {
        width: 20;
    }
    """

    def __init__(self):
        super().__init__()
        self._files: List[FileInfo] = []
        self._filtered_files: List[FileInfo] = []

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Toolbar with controls
        with Container(id="toolbar"):
            yield Horizontal(
                Button("⬆", id="parent-dir"),
                Button("🏠", id="home-dir"),
                Button("⟳", id="refresh"),
                Select(
                    ((mode.value, mode) for mode in ViewMode),
                    id="view-mode",
                    value=self.view_mode
                ),
                Select(
                    ((field.value, field) for field in SortBy),
                    id="sort-by",
                    value=self.sort_by
                ),
                Button("↕", id="sort-direction"),
                Input(placeholder="Filter...", id="filter"),
            )

        # Current path display
        yield Static("", id="path-display")

        # Main content area
        with Vertical():
            yield Container(id="content")

        # Status bar
        yield Static("Ready", id="status-bar")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self.load_directory()

    def load_directory(self) -> None:
        """Load the current directory contents."""
        try:
            self._files = []
            self._filtered_files = []
            for entry in self.current_path.iterdir():
                try:
                    stat = entry.stat()
                    self._files.append(FileInfo(
                        path=entry,
                        name=entry.name,
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        owner=pwd.getpwuid(stat.st_uid).pw_name,
                        group=grp.getgrgid(stat.st_gid).gr_name,
                        permissions=self._get_permissions(stat.st_mode),
                        is_dir=entry.is_dir(),
                        icon="📁" if entry.is_dir() else "📄"
                    ))
                except (PermissionError, FileNotFoundError):
                    continue

            self.sort_files()
            self.filter_files()
            self.refresh_view()
            self._update_status()

        except Exception as e:
            self.notify(f"Error loading directory: {e}", severity="error")

    def _get_permissions(self, mode: int) -> str:
        """Convert mode bits to string representation."""
        perms = ""
        for who in "rwx":
            perms += who if mode & getattr(os, f"S_I{who.upper()}USR") else "-"
        for who in "rwx":
            perms += who if mode & getattr(os, f"S_I{who.upper()}GRP") else "-"
        for who in "rwx":
            perms += who if mode & getattr(os, f"S_I{who.upper()}OTH") else "-"
        return perms

    def sort_files(self) -> None:
        """Sort files according to current sort settings."""
        reverse = self.sort_reverse
        if self.sort_by == SortBy.NAME:
            key = lambda f: (not f.is_dir, f.name.lower())
        elif self.sort_by == SortBy.SIZE:
            key = lambda f: (not f.is_dir, f.size)
        elif self.sort_by == SortBy.MODIFIED:
            key = lambda f: (not f.is_dir, f.modified)
        else:  # TYPE
            key = lambda f: (not f.is_dir, f.path.suffix.lower())

        self._files.sort(key=key, reverse=reverse)
        self.filter_files()

    def filter_files(self) -> None:
        """Filter files based on current filter text."""
        if not self.filter_text:
            self._filtered_files = self._files
        else:
            text = self.filter_text.lower()
            self._filtered_files = [
                f for f in self._files
                if text in f.name.lower()
            ]
        self.page = 0

    def refresh_view(self) -> None:
        """Update the display according to current view mode."""
        content = self.query_one("#content")
        content.remove_children()

        start = self.page * self.items_per_page
        files = self._filtered_files[start:start + self.items_per_page]

        if self.view_mode == ViewMode.DETAILS:
            table = DataTable()
            table.add_columns(
                "Name", "Size", "Modified", "Owner", "Group", "Permissions"
            )
            for file in files:
                table.add_row(
                    f"{file.icon} {file.name}",
                    f"{self._format_size(file.size)}",
                    file.modified.strftime("%Y-%m-%d %H:%M"),
                    file.owner,
                    file.group,
                    file.permissions,
                    key=str(file.path)
                )
            content.mount(table)
        
        elif self.view_mode == ViewMode.ICONS:
            grid = Grid(classes="file-grid")
            for file in files:
                icon = Static(
                    f"{file.icon}\n{file.name}",
                    classes="file-icon",
                    id=f"file-{hash(str(file.path))}"
                )
                grid.mount(icon)
            content.mount(grid)
        
        else:  # LIST
            for file in files:
                text = Text()
                text.append(f"{file.icon} ", "bold")
                text.append(file.name)
                if not file.is_dir:
                    text.append(f" ({self._format_size(file.size)})", "italic")
                content.mount(Static(text))

        # Update path display
        self.query_one("#path-display").update(Text(str(self.current_path), style="bold"))

    def _format_size(self, size: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"

    def _update_status(self) -> None:
        """Update the status bar."""
        total = len(self._filtered_files)
        dirs = sum(1 for f in self._filtered_files if f.is_dir)
        files = total - dirs
        self.query_one("#status-bar").update(
            f"{total} items ({dirs} directories, {files} files)"
        )

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        if self.view_mode == ViewMode.DETAILS:
            table = self.query_one(DataTable)
            table.action_cursor_up()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        if self.view_mode == ViewMode.DETAILS:
            table = self.query_one(DataTable)
            table.action_cursor_down()

    def action_select_entry(self) -> None:
        """Handle entry selection."""
        if self.selected_path and self.selected_path.is_dir():
            self.current_path = self.selected_path
            self.load_directory()

    def action_parent_directory(self) -> None:
        """Navigate to parent directory."""
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            self.load_directory()

    async def on_click(self, event: Click) -> None:
        """Handle click events."""
        if event.target.id == "parent-dir":
            self.action_parent_directory()
        elif event.target.id == "home-dir":
            self.current_path = Path.home()
            self.load_directory()
        elif event.target.id == "refresh":
            self.load_directory()
        elif event.target.id == "sort-direction":
            self.sort_reverse = not self.sort_reverse
            self.sort_files()
        elif event.target.id.startswith("file-"):
            # Handle file selection
            file_id = event.target.id
            for file in self._filtered_files:
                if f"file-{hash(str(file.path))}" == file_id:
                    self.selected_path = file.path
                    if file.is_dir:
                        self.current_path = file.path
                        self.load_directory()
                    break

    async def watch_view_mode(self, new_value: ViewMode) -> None:
        """Handle view mode changes."""
        self.refresh_view()

    async def watch_sort_by(self, new_value: SortBy) -> None:
        """Handle sort field changes."""
        self.sort_files()

    async def watch_filter_text(self, new_value: str) -> None:
        """Handle filter text changes."""
        self.filter_files()

    async def watch_current_path(self, new_value: Path) -> None:
        """Handle current path changes."""
        self.load_directory()



