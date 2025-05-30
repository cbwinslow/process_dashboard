#!/usr/bin/env python3
"""
Process Dashboard - A TUI-based system process management tool.

This module implements the main application class and entry point.
"""

import sys
import argparse
from typing import Optional

from textual.app import App
from textual.binding import Binding
from textual.widgets import Header, Footer
from textual.containers import Container

from config import setup_logging, load_or_create_config, get_logger
from processes.monitor import ProcessMonitor
from ui.process_list import ProcessListWidget
from ui.resource_monitor import ResourceMonitor
from ui.config_panel import ConfigPanel
from ui.matrix_splash import MatrixSplash
from ui.matrix_background import MatrixBackground
from ui.file_browser import FileBrowser

# Set up logger
logger = get_logger("main")

class ProcessDashboard(App):
    """Main application class for Process Dashboard."""

    TITLE = "Process Dashboard"
    SUB_TITLE = "System Monitor"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "toggle_config", "Config"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "focus_filter", "Filter"),
        Binding("t", "terminate_process", "Terminate"),
        Binding("k", "kill_process", "Kill"),
        Binding("ctrl+h", "toggle_hidden", "Toggle Hidden"),
    ]

    def __init__(
        self,
        config_path: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """Initialize the dashboard.
        
        Args:
            config_path: Optional path to config file
            log_level: Logging level
        """
        super().__init__()
        
        # Set up logging
        setup_logging(level=log_level)
        logger.info("Initializing Process Dashboard")
        
        # Load configuration
        try:
            self.config = load_or_create_config(config_path)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = load_or_create_config()
        
        # Initialize components
        self.monitor = ProcessMonitor(
            history_interval=self.config.update_interval,
            history_length=self.config.history_length
        )
        
        # Set theme
        self.dark = True
        if self.config.matrix_theme:
            self.background = MatrixBackground()

    def compose(self):
        """Create and arrange widgets."""
        yield Header()
        
        with Container():
            # Left side
            with Container(classes="left-pane"):
                yield ProcessListWidget(self.monitor)
                yield FileBrowser()
            
            # Right side
            with Container(classes="right-pane"):
                yield ResourceMonitor()
                yield ConfigPanel()
        
        yield Footer()

    def on_mount(self):
        """Handle application mount."""
        logger.info("Application mounted")
        # Start update timer
        self.set_interval(self.config.update_interval, self.update_displays)

    def update_displays(self):
        """Update all displays."""
        try:
            # Update process list
            process_list = self.query_one(ProcessListWidget)
            process_list.update_process_list()
            
            # Update resource monitor
            resource_monitor = self.query_one(ResourceMonitor)
            resources = self.monitor.get_system_resources()
            resource_monitor.update_resources(resources)
            
            logger.debug("Displays updated successfully")
        except Exception as e:
            logger.error(f"Failed to update displays: {e}")

    def action_toggle_config(self):
        """Toggle configuration panel."""
        logger.debug("Toggling configuration panel")
        config_panel = self.query_one(ConfigPanel)
        config_panel.toggle_visibility()

    def action_refresh(self):
        """Refresh all displays."""
        logger.debug("Refreshing displays")
        self.update_displays()

    def action_focus_filter(self):
        """Focus the process filter input."""
        logger.debug("Focusing process filter")
        process_list = self.query_one(ProcessListWidget)
        process_list.focus_filter()

def main():
    """Application entry point."""
    parser = argparse.ArgumentParser(description="Process Dashboard")
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level"
    )
    
    args = parser.parse_args()
    
    try:
        app = ProcessDashboard(
            config_path=args.config,
            log_level=args.log_level
        )
        app.run()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
