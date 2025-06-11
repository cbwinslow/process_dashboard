"""
Configuration panel widget for Process Dashboard.

This module implements a configuration panel that allows users to
customize dashboard settings and appearance.
"""

from textual.widget import Widget
from textual.containers import Vertical
from textual.widgets import Switch, Select, Input, Button, Static
from textual.message import Message
from typing import Optional
import logging

from src.config.settings import DashboardConfig

logger = logging.getLogger("dashboard.config")

class ConfigPanel(Widget):
    """Configuration panel widget."""

    DEFAULT_CSS = """
    ConfigPanel {
        layout: vertical;
        background: #001100;
        height: 100%;
        padding: 1;
    }

    .config-section {
        margin: 1 0;
    }

    .config-title {
        color: #00ff00;
        text-style: bold;
        margin-bottom: 1;
    }

    Switch {
        margin: 1 0;
    }

    Select {
        width: 100%;
        margin: 1 0;
    }

    Input {
        width: 100%;
        margin: 1 0;
    }

    Button {
        margin: 1 0;
        width: 100%;
        background: #002200;
        color: #00ff00;
        border: solid green;
    }

    .status {
        color: #00ff00;
        text-align: center;
        padding: 1;
    }
    """

    class ConfigChanged(Message):
        """Message emitted when configuration changes."""
        def __init__(self, config: DashboardConfig):
            self.config = config
            super().__init__()

    def __init__(self):
        """Initialize the configuration panel."""
        super().__init__()
        self.config = DashboardConfig()
        self._status: Optional[Static] = None

    def compose(self):
        """Create child widgets."""
        with Vertical():
            # Appearance section
            with Vertical(classes="config-section"):
                yield Static("Appearance", classes="config-title")
                yield Switch("Matrix Theme", id="matrix_theme", value=self.config.theme.matrix_effect)
                # Only background color for now
                yield Input(
                    placeholder="Background Color",
                    value=self.config.theme.background_color,
                    id="background_color"
                )

            # Monitoring section
            with Vertical(classes="config-section"):
                yield Static("Monitoring", classes="config-title")
                yield Input(
                    placeholder="Process Update Interval (seconds)",
                    value=str(self.config.updates.process_update_interval),
                    id="process_update_interval"
                )
                yield Input(
                    placeholder="Resource Update Interval (seconds)",
                    value=str(self.config.updates.resource_update_interval),
                    id="resource_update_interval"
                )
                yield Input(
                    placeholder="Disk Update Interval (seconds)",
                    value=str(self.config.updates.disk_update_interval),
                    id="disk_update_interval"
                )
                yield Switch(value=self.config.display.show_process_tree, id="show_process_tree")
                yield Switch(value=self.config.display.show_system_resources, id="show_system_resources")
                yield Switch(value=self.config.display.show_disk_usage, id="show_disk_usage")
                yield Switch(value=self.config.display.show_network_stats, id="show_network_stats")

            # Action buttons
            yield Button("Save Configuration", id="save")
            yield Button("Reset to Defaults", id="reset")
            # Status message
            self._status = Static("", classes="status")
            yield self._status

    def on_mount(self):
        """Handle widget mount."""
        self.load_config()

    def on_switch_changed(self, event: Switch.Changed):
        """Handle switch changes."""
        try:
            if event.switch.id == "matrix_theme":
                self.config.theme.matrix_effect = event.value
            elif event.switch.id == "show_process_tree":
                self.config.display.show_process_tree = event.value
            elif event.switch.id == "show_system_resources":
                self.config.display.show_system_resources = event.value
            elif event.switch.id == "show_disk_usage":
                self.config.display.show_disk_usage = event.value
            elif event.switch.id == "show_network_stats":
                self.config.display.show_network_stats = event.value
            self._show_status("Setting updated")
        except Exception as e:
            logger.error("Failed to update switch setting: %s", e)
            self._show_status("Failed to update setting", error=True)

    def on_input_changed(self, event: Input.Changed):
        """Handle input changes."""
        try:
            if event.input.id == "background_color":
                self.config.theme.background_color = event.value
            elif event.input.id == "process_update_interval":
                self.config.updates.process_update_interval = float(event.value)
            elif event.input.id == "resource_update_interval":
                self.config.updates.resource_update_interval = float(event.value)
            elif event.input.id == "disk_update_interval":
                self.config.updates.disk_update_interval = float(event.value)
            self._show_status("Setting updated")
        except Exception as e:
            logger.error("Failed to update input setting: %s", e)
            self._show_status("Invalid input value", error=True)

    def load_config(self):
        """Load configuration from file."""
        try:
            self.query_one("#matrix_theme", Switch).value = self.config.theme.matrix_effect
            self.query_one("#background_color", Input).value = self.config.theme.background_color
            self.query_one("#process_update_interval", Input).value = str(self.config.updates.process_update_interval)
            self.query_one("#resource_update_interval", Input).value = str(self.config.updates.resource_update_interval)
            self.query_one("#disk_update_interval", Input).value = str(self.config.updates.disk_update_interval)
            self.query_one("#show_process_tree", Switch).value = self.config.display.show_process_tree
            self.query_one("#show_system_resources", Switch).value = self.config.display.show_system_resources
            self.query_one("#show_disk_usage", Switch).value = self.config.display.show_disk_usage
            self.query_one("#show_network_stats", Switch).value = self.config.display.show_network_stats
            self._show_status("Configuration loaded")
        except Exception as e:
            logger.error("Failed to load configuration: %s", e)
            self._show_status("Failed to load configuration", error=True)

    def save_config(self):
        """Save configuration to file."""
        try:
            # Use save_config from settings
            from src.config.settings import save_config
            save_config(self.config)
            self.post_message(self.ConfigChanged(self.config))
            self._show_status("Configuration saved")
        except Exception as e:
            logger.error("Failed to save configuration: %s", e)
            self._show_status("Failed to save configuration", error=True)

    def reset_config(self):
        """Reset configuration to defaults."""
        try:
            from src.config.settings import create_default_config
            self.config = create_default_config()
            self.load_config()
            self._show_status("Configuration reset to defaults")
        except Exception as e:
            logger.error("Failed to reset configuration: %s", e)
            self._show_status("Failed to reset configuration", error=True)

    def _show_status(self, message: str, error: bool = False):
        """Show status message."""
        if self._status:
            style = "red" if error else "green"
            self._status.update(f"[{style}]{message}[/]")
