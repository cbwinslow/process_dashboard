#!/usr/bin/env python3
"""
Process Dashboard - Terminal-based process management and monitoring.

Main application entry point that integrates all dashboard components
into a cohesive terminal UI with configuration support.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static
from textual.screen import Screen
from textual import events, work
from textual.css.query import NoMatches

from config.config_manager import ConfigManager, DashboardConfig
from processes.process_controller import ProcessController
from processes.snmp_monitor import SNMPMonitor
from processes.group_manager import ProcessGroupManager
from processes.resource_limiter import ResourceLimiter
from ui.process_panel import ProcessManagementPanel
from ui.process_display import ProcessDisplayWidget

class DashboardApp(App):
    """Main Process Dashboard application."""

    BINDINGS = [
        # Default bindings - will be updated from config
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("f", "toggle_full_screen", "Toggle Full Screen", show=True),
        Binding("h", "toggle_help", "Help", show=True),
        Binding("c", "clear_filters", "Clear Filters", show=True),
    ]

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        *args,
        **kwargs
    ):
        """Initialize the dashboard application.
        
        Args:
            config_dir: Optional configuration directory path
        """
        super().__init__(*args, **kwargs)
        
        # Initialize configuration
        self.config_manager = ConfigManager(config_dir)
        self.config_manager.load_config()
        self.config = self.config_manager.get_config()
        
        # Configure logging
        self._setup_logging()
        
        # Initialize components with configuration
        self._init_components()
        
        # Update bindings from config
        self._update_bindings()
        
        # Apply theme
        self.dark = True  # Use dark mode as base
        self._apply_theme()

    def _setup_logging(self) -> None:
        """Configure logging based on settings."""
        log_config = self.config.logging
        logging.basicConfig(
            filename=log_config.file,
            level=getattr(logging, log_config.level.upper()),
            format=log_config.format
        )
        self.log = logging.getLogger("dashboard")

    def _init_components(self) -> None:
        """Initialize dashboard components with configuration."""
        try:
            # Initialize controllers
            self.process_controller = ProcessController(
                history_size=self.config.process.history_size,
                warning_thresholds=self.config.process.warning_thresholds,
                critical_thresholds=self.config.process.critical_thresholds
            )
            
            self.group_manager = ProcessGroupManager(
                config_path=self.config_dir / "groups.json"
            )
            
            self.resource_limiter = ResourceLimiter(
                config_path=self.config_dir / "resource_limits.json"
            )
            
            # Initialize SNMP if enabled
            self.snmp_monitor = None
            if self.config.snmp.enabled:
                self.snmp_monitor = SNMPMonitor(
                    port=self.config.snmp.default_port,
                    community=self.config.snmp.community,
                    collection_interval=self.config.snmp.collection_interval
                )
            
            # Initialize status tracking
            self.error_count = 0
            self.warning_count = 0
            self._last_status = ""
            
        except Exception as e:
            self.log.error(f"Failed to initialize components: {e}")
            raise

    def _update_bindings(self) -> None:
        """Update key bindings from configuration."""
        try:
            # Create new bindings list
            new_bindings = []
            
            # Add configured bindings
            for action, key in self.config.keybindings.items():
                new_bindings.append(
                    Binding(key, action, action.replace('_', ' ').title(), show=True)
                )
            
            # Update app bindings
            self.BINDINGS = new_bindings
            
        except Exception as e:
            self.log.error(f"Failed to update key bindings: {e}")

    def _apply_theme(self) -> None:
        """Apply configured theme."""
        try:
            theme = self.config.display.theme
            
            # Create CSS with theme colors
            self.DEFAULT_CSS = f"""
            Screen {{
                background: {theme["background"]};
                color: {theme["text"]};
            }}

            Header {{
                dock: top;
                height: 1;
                background: {theme["accent"]};
                color: {theme["text"]};
            }}

            Footer {{
                dock: bottom;
                height: 1;
                background: {theme["accent"]};
                color: {theme["text"]};
            }}

            #main-container {{
                height: 100%;
                width: 100%;
            }}

            #status-bar {{
                dock: bottom;
                height: 1;
                background: {theme["accent"]};
                color: {theme["text"]};
            }}

            .error {{
                color: {theme["error"]};
            }}

            .warning {{
                color: {theme["warning"]};
            }}

            .success {{
                color: {theme["success"]};
            }}
            """
            
        except Exception as e:
            self.log.error(f"Failed to apply theme: {e}")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        try:
            # Create header
            yield Header()
            
            # Create main container
            with Container(id="main-container"):
                # Create process display with config
                yield ProcessDisplayWidget(
                    columns=self.config.display.columns,
                    refresh_rate=self.config.display.refresh_rate
                )
                
                # Create management panel with config
                yield ProcessManagementPanel(
                    process_controller=self.process_controller,
                    snmp_monitor=self.snmp_monitor,
                    enable_limits=self.config.resources.enable_limits,
                    default_limits=self.config.resources.default_limits
                )
                
                # Create status bar
                yield Static(id="status-bar")
            
            # Create footer
            yield Footer()
            
        except Exception as e:
            self.log.error(f"Failed to compose UI: {e}")
            raise

    def on_mount(self) -> None:
        """Handle application mount."""
        try:
            # Start background workers
            self.update_status_worker()
            self.monitor_resources_worker()
            
            # Initial status update
            self.update_status("Dashboard ready")
            
        except Exception as e:
            self.log.error(f"Failed to mount application: {e}")
            self.update_status(f"Error: {e}", "error")

    @work(thread=True)
    def update_status_worker(self) -> None:
        """Background worker for status updates."""
        try:
            # Get process counts
            total_processes = len(self.process_controller.get_all_processes())
            managed_processes = len(self.process_controller.get_managed_processes())
            
            # Create status message
            status = (
                f"Total: {total_processes} | "
                f"Managed: {managed_processes} | "
                f"Errors: {self.error_count} | "
                f"Warnings: {self.warning_count}"
            )
            
            # Update if changed
            if status != self._last_status:
                self._last_status = status
                self.update_status(status)
                
        except Exception as e:
            self.log.error(f"Status update failed: {e}")
            self.handle_error("Status update failed")

    @work(thread=True)
    def monitor_resources_worker(self) -> None:
        """Background worker for resource monitoring."""
        try:
            # Check resource limits
            if self.config.resources.enable_limits:
                interval = self.config.resources.check_interval
                
                for pid in self.resource_limiter.get_managed_processes():
                    try:
                        self.process_controller.check_process_limits(pid)
                    except Exception as e:
                        self.log.warning(f"Resource check failed for PID {pid}: {e}")
                        self.handle_warning(f"Resource check failed for PID {pid}")
            
            # Update SNMP metrics if enabled
            if self.snmp_monitor and self.snmp_monitor.is_connected():
                self.snmp_monitor.update_metrics()
                
        except Exception as e:
            self.log.error(f"Resource monitoring failed: {e}")
            self.handle_error("Resource monitoring failed")

    def handle_error(self, message: str) -> None:
        """Handle error conditions.
        
        Args:
            message: Error message
        """
        self.error_count += 1
        self.update_status(f"Error: {message}", "error")

    def handle_warning(self, message: str) -> None:
        """Handle warning conditions.
        
        Args:
            message: Warning message
        """
        self.warning_count += 1
        self.update_status(f"Warning: {message}", "warning")

    def update_status(self, message: str, style: str = "") -> None:
        """Update status bar message.
        
        Args:
            message: Status message
            style: Optional CSS style class
        """
        try:
            status_bar = self.query_one("#status-bar", Static)
            status_bar.update(message)
            if style:
                status_bar.set_class(True, style)
        except NoMatches:
            self.log.error("Status bar not found")
        except Exception as e:
            self.log.error(f"Failed to update status: {e}")

def main():
    """Application entry point."""
    try:
        # Get config directory
        config_dir = Path.home() / ".config" / "process-dashboard"
        
        # Create and run app
        app = DashboardApp(config_dir=config_dir)
        app.run()
        
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        raise

if __name__ == "__main__":
    main()
