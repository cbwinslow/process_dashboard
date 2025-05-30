"""
Process Dashboard - A TUI-based system process management tool.

This module implements the main application class and entry point for the process dashboard,
featuring a matrix-themed interface with configurable layouts and process monitoring capabilities.
"""

import logging
import time
from typing import ClassVar
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import (
    Header, Footer, Static, Label, DataTable,
    Tree, Button
)
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.logging import RichHandler
from rich.tree import Tree as RichTree

from config.settings import DashboardConfig, load_or_create_config
from processes.monitor import ProcessMonitor, ProcessInfo, SystemResources
from ui.matrix_splash import MatrixSplash
from ui.matrix_background import MatrixBackground
from ui.file_browser import FileBrowser
from ui.resource_monitor import ResourceMonitor
from ui.config_panel import ConfigPanel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("dashboard")

class DiskUsageWidget(Static):
    """Widget for displaying disk usage information."""

    def __init__(self):
        """Initialize the disk usage widget."""
        super().__init__()
        self.rich_tree = RichTree("Root")
        self.root_path = Path.home()  # Start from user's home directory for safety

    def on_mount(self) -> None:
        """Set up the directory tree on mount."""
        self.update_disk_usage()

    def render(self) -> RichTree:
        """Render the disk usage tree.
        
        Returns:
            RichTree: The rendered tree structure
        """
        return self.rich_tree

    def update_disk_usage(self) -> None:
        """Update the disk usage tree."""
        self.rich_tree = RichTree(f"📁 {self.root_path} (scanning...)")
        
        try:
            # Add immediate children of root path
            for entry in sorted(self.root_path.iterdir()):
                if not entry.name.startswith('.'):
                    size = self.get_size(entry)
                    icon = "📁" if entry.is_dir() else "📄"
                    label = f"{icon} {entry.name} ({size})"
                    self.rich_tree.add(label)
            
            # Update root label with total size
            root_size = self.get_size(self.root_path)
            self.rich_tree.label = f"📁 {self.root_path} ({root_size})"
        except PermissionError:
            root.label = f"📁 {self.root_path} (access denied)"
        except Exception as e:
            root.label = f"📁 {self.root_path} (error: {str(e)})"

    def get_size(self, path: Path) -> str:
        """Get human-readable size of a file or directory.

        Args:
            path: Path to get size for.

        Returns:
            str: Human-readable size string.
        """
        try:
            if path.is_file():
                size = path.stat().st_size
            else:
                total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size = total
            
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}PB"
        except (PermissionError, FileNotFoundError):
            return "N/A"
        except Exception:
            return "Error"

class ProcessListWidget(Static):
    """Widget for displaying and managing process list."""

    def __init__(self, monitor: ProcessMonitor):
        super().__init__()
        self.monitor = monitor
        self.process_table = DataTable()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield self.process_table

    def on_mount(self) -> None:
        """Set up the process table columns."""
        self.process_table.add_columns(
            "PID", "Name", "CPU %", "Memory %", "Status", "User", "Started"
        )
        self.update_process_list()

    def update_process_list(self) -> None:
        """Update the process list display."""
        try:
            processes = self.monitor.get_process_list()
            self.process_table.clear()
            for pid, process in processes.items():
                formatted = self.monitor.format_process_data(process)
                self.process_table.add_row(
                    formatted["PID"],
                    formatted["Name"],
                    formatted["CPU %"],
                    formatted["Memory %"],
                    formatted["Status"],
                    formatted["User"],
                    formatted["Started"],
                    key=str(pid)
                )
        except Exception as e:
            logger.error(f"Failed to update process list: {e}")

class ResourceMonitorWidget(Static):
    """Widget for displaying system resource usage."""

    def __init__(self, monitor: ProcessMonitor):
        super().__init__()
        self.monitor = monitor
        self.resources_display = Static()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield self.resources_display

    def update_resources(self) -> None:
        """Update the resource usage display."""
        try:
            resources = self.monitor.get_system_resources()
            formatted = self.monitor.format_resource_data(resources)
            
            content = Text()
            for key, value in formatted.items():
                content.append(f"{key}: ", style="bold green")
                content.append(f"{value}\n", style="bright_green")
            
            self.resources_display.update(content)
        except Exception as e:
            logger.error(f"Failed to update resource monitor: {e}")

class ProcessDashboard(App):
    """Main application class for the Process Dashboard TUI."""
    
    TITLE = "Matrix Process Dashboard"
    SUB_TITLE = "System Monitor"

    # Reactive attributes for pane sizes
    left_pane_width = reactive(0.5)  # 50% of total width
    top_pane_height = reactive(0.5)  # 50% of total height

    # CSS for matrix theme styling
    CSS = """
    Screen {
        layers: base overlay splash;
        background: #000000;
    }

    MatrixSplash {
        layer: splash;
        dock: top;
        width: 100%;
        height: 100%;
    }

    Header {
        background: #001100;
        color: #00ff00;
        border: none;
    }

    Footer {
        background: #001100;
        color: #00ff00;
        border: none;
    }

    #menu-container {
        dock: top;
        height: 3;
        background: #001100;
        border-bottom: solid #003300;
    }

    .menu-item {
        padding: 0 2;
        color: #00ff00;
        text-style: bold;
        background: #001100;
        border: tall transparent;
    }

    .menu-item:hover {
        background: #002200;
        border: tall #00ff00;
    }

    #main-container {
        layout: grid;
        grid-size: 2 1;
        grid-gutter: 0 1;
        padding: 1;
    }

    .pane-section {
        width: 1fr;
        height: 100%;
        layout: grid;
        grid-rows: 1fr auto 1fr;
    }

    .dashboard-pane {
        height: 100%;
        border: solid #003300;
        background: #000000;
    }

    .dashboard-pane:focus-within {
        border: double #00ff00;
        background: #001100;
    }

    .pane-title {
        background: #001100;
        color: #00ff00;
        text-style: bold;
        padding: 0 1;
        text-align: center;
        border-bottom: solid #003300;
    }

    .resize-handle {
        background: #001100;
        color: #003300;
        width: 100%;
        height: 100%;
        content-align: center middle;
        border: none;
    }

    .resize-handle:hover {
        background: #002200;
        color: #00ff00;
        border: solid #00ff00;
    }

    #vertical-resize {
        width: 1;
        height: 100%;
        background: #001100;
    }

    #horizontal-resize, #horizontal-resize-right {
        height: 1;
        background: #001100;
    }

    DataTable {
        height: 100%;
        color: #00ff00;
        background: #000000;
        border: solid #003300;
    }

    DataTable > .header {
        background: #001100;
        color: #00ff00;
        text-style: bold;
        border-bottom: solid #003300;
    }

    DataTable > .row {
        background: transparent;
        color: #00ff00;
    }

    DataTable > .row:hover {
        background: #001100;
        border: solid #00ff00;
    }

    DataTable > .row-highlighted {
        background: #002200;
        border: solid #00ff00;
        color: #00ff00;
        text-style: bold;
    }

    Label {
        color: #00ff00;
        text-style: bold;
    }

    Input {
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    Input:focus {
        border: double #00ff00;
        background: #002200;
    }

    Select {
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    Select:focus {
        border: double #00ff00;
        background: #002200;
    }

    Button {
        background: #001100;
        color: #00ff00;
        border: solid #003300;
        min-width: 8;
    }

    Button:hover {
        background: #002200;
        border: double #00ff00;
    }

    ScrollBar {
        background: #000000;
        color: #003300;
        border: none;
    }

    ScrollBar:hover {
        color: #00ff00;
        background: #001100;
    }

    ProgressBar {
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    ProgressBar > .bar {
        color: #00ff00;
        background: #008800;
    }

    Static {
        background: transparent;
        color: #00ff00;
    }

    .graph-container {
        border: solid #003300;
        background: #000000;
        padding: 0 1;
    }

    .graph-container:focus-within {
        border: double #00ff00;
        background: #001100;
    }
    """

    # Keyboard bindings
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "toggle_config", "Config", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the ProcessDashboard application."""
        super().__init__()
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        self.dark = True
        self.splash_shown = False
        
        # Load configuration
        try:
            self.config = load_or_create_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = DashboardConfig()
        
        # Initialize process monitor
        self.monitor = ProcessMonitor(
            process_interval=self.config.updates.process_update_interval,
            resource_interval=self.config.updates.resource_update_interval
        )
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Background matrix rain effect
        yield MatrixBackground()
        
        yield Header()
        
        # Menu container
        with Container(id="menu-container"):
            yield Horizontal(
                Button("File", classes="menu-item"),
                Button("View", classes="menu-item"),
                Button("Processes", classes="menu-item"),
                Button("Configuration", classes="menu-item"),
                Button("Help", classes="menu-item"),
            )
        
        # Main dashboard container with resizable panes
        with Container(id="main-container"):
            with Grid():
                # Left side (Process List and File Browser)
                with Vertical(id="left-pane", classes="pane-section"):
                    # Process List
                    with Container(id="process-pane", classes="dashboard-pane"):
                        yield Label("Process Monitor", classes="pane-title")
                        yield ProcessListWidget(self.monitor)
                    
                    yield Button("⣿", id="horizontal-resize", classes="resize-handle")
                    
                    # File Browser
                    with Container(id="file-pane", classes="dashboard-pane"):
                        yield Label("File Browser", classes="pane-title")
                        yield FileBrowser()
                
                yield Button("⋮", id="vertical-resize", classes="resize-handle")
                
                # Right side (System Resources and Configuration)
                with Vertical(id="right-pane", classes="pane-section"):
                    # Resource Monitor
                    with Container(id="resource-pane", classes="dashboard-pane"):
                        yield Label("System Resources", classes="pane-title")
                        yield ResourceMonitor()
                    
                    yield Button("⣿", id="horizontal-resize-right", classes="resize-handle")
                    
                    # Configuration
                    with Container(id="config-pane", classes="dashboard-pane"):
                        yield Label("Configuration", classes="pane-title")
                        yield ConfigPanel()

        yield Footer()

    async def on_mount(self) -> None:
        """Handle the application start-up after mounting."""
        try:
            if not self.splash_shown:
                # Show splash screen
                splash = MatrixSplash()
                self.mount(splash)
                await self.wait_for_message(MatrixSplash.Completed)
                await splash.remove()
                self.splash_shown = True

            # Start process monitoring updates
            self.set_interval(
                self.config.updates.process_update_interval,
                self.update_process_list
            )
            
            # Start resource monitoring updates
            self.set_interval(
                self.config.updates.resource_update_interval,
                self.update_resource_monitor
            )
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")

    def format_config_display(self) -> Text:
        """Format the configuration display.
        
        Returns:
            Text: Rich text object containing formatted configuration.
        """
        try:
            content = Text()
            content.append("Theme Settings\n", style="bold green")
            content.append(f"Matrix Effect: {self.config.theme.matrix_effect}\n")
            content.append("\nUpdate Intervals\n", style="bold green")
            content.append(f"Process Update: {self.config.updates.process_update_interval}s\n")
            content.append(f"Resource Update: {self.config.updates.resource_update_interval}s\n")
            content.append(f"Disk Update: {self.config.updates.disk_update_interval}s")
            return content
        except Exception as e:
            logger.error(f"Failed to format config display: {e}")
            return "Configuration display error"

    def update_process_list(self) -> None:
        """Update the process list display."""
        try:
            process_list = self.query_one(ProcessListWidget)
            if process_list is not None:
                process_list.update_process_list()
        except Exception as e:
            logger.error(f"Failed to update process list: {e}")

    def update_resource_monitor(self) -> None:
        """Update the resource monitor display."""
        try:
            resource_monitor = self.query_one(ResourceMonitorWidget)
            if resource_monitor is not None:
                resource_monitor.update_resources()
        except Exception as e:
            logger.error(f"Failed to update resource monitor: {e}")

    def action_toggle_config(self) -> None:
        """Toggle configuration panel visibility."""
        try:
            config_pane = self.query_one(".dashboard-pane:last-child", Static)
            if config_pane is not None:
                config_pane.toggle_class("hidden")
        except Exception as e:
            logger.error(f"Failed to toggle config panel: {e}")

    def action_refresh(self) -> None:
        """Manually refresh all dashboard components."""
        try:
            self.update_process_list()
            self.update_resource_monitor()
        except Exception as e:
            logger.error(f"Failed to refresh display: {e}")

    async def on_key(self, message) -> None:
        """Handle key events.
        
        Args:
            message: The key message event.
        """
        try:
            if message.key == "q":
                await self.action_quit()
            elif message.key == "r":
                self.action_refresh()
            elif message.key == "c":
                self.action_toggle_config()
        except Exception as e:
            logger.error(f"Failed to handle key event: {e}")
            await self.action_quit()

def main() -> None:
    """Entry point for the application."""
    app = ProcessDashboard()
    app.run()

if __name__ == "__main__":
    main()

