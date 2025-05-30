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

from config.settings import DashboardConfig

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
                yield Switch("Matrix Theme", id="matrix_theme", value=True)
                yield Select(
                    options=[
                        ("System Default", "system"),
                        ("Dark", "dark"),
                        ("Light", "light")
                    ],
                    value="dark",
                    id="theme"
                )
                yield Input(
                    placeholder="Custom CSS Path",
                    id="css_path"
                )

            # Monitoring section
            with Vertical(classes="config-section"):
                yield Static("Monitoring", classes="config-title")
                yield Input(
                    placeholder="Update Interval (seconds)",
                    value="2",
                    id="update_interval"
                )
                yield Input(
                    placeholder="History Length (minutes)",
                    value="60",
                    id="history_length"
                )
                yield Switch("Show System Processes", id="show_system", value=True)
                yield Switch("Show Child Processes", id="show_children", value=True)

            # Control section
            with Vertical(classes="config-section"):
                yield Static("Process Control", classes="config-title")
                yield Switch("Confirm Actions", id="confirm_actions", value=True)
                yield Switch("Allow Process Kill", id="allow_kill", value=True)
                yield Switch("Allow Priority Change", id="allow_priority", value=True)

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
            setattr(self.config, event.switch.id, event.value)
            self._show_status("Setting updated")
        except Exception as e:
            logger.error(f"Failed to update switch setting: {e}")
            self._show_status("Failed to update setting", error=True)

    def on_select_changed(self, event: Select.Changed):
        """Handle select changes."""
        try:
            setattr(self.config, event.select.id, event.value)
            self._show_status("Setting updated")
        except Exception as e:
            logger.error(f"Failed to update select setting: {e}")
            self._show_status("Failed to update setting", error=True)

    def on_input_changed(self, event: Input.Changed):
        """Handle input changes."""
        try:
            # Convert numeric inputs
            if event.input.id in ("update_interval", "history_length"):
                value = int(event.value) if event.value.isdigit() else None
                if value is not None:
                    setattr(self.config, event.input.id, value)
                    self._show_status("Setting updated")
            else:
                setattr(self.config, event.input.id, event.value)
                self._show_status("Setting updated")
        except Exception as e:
            logger.error(f"Failed to update input setting: {e}")
            self._show_status("Invalid input value", error=True)

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        if event.button.id == "save":
            self.save_config()
        elif event.button.id == "reset":
            self.reset_config()

    def load_config(self):
        """Load configuration from file."""
        try:
            # Update widget values from config
            self.query_one("#matrix_theme", Switch).value = self.config.matrix_theme
            self.query_one("#theme", Select).value = self.config.theme
            self.query_one("#css_path", Input).value = self.config.css_path or ""
            self.query_one("#update_interval", Input).value = str(self.config.update_interval)
            self.query_one("#history_length", Input).value = str(self.config.history_length)
            self.query_one("#show_system", Switch).value = self.config.show_system
            self.query_one("#show_children", Switch).value = self.config.show_children
            self.query_one("#confirm_actions", Switch).value = self.config.confirm_actions
            self.query_one("#allow_kill", Switch).value = self.config.allow_kill
            self.query_one("#allow_priority", Switch).value = self.config.allow_priority
            
            self._show_status("Configuration loaded")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._show_status("Failed to load configuration", error=True)

    def save_config(self):
        """Save configuration to file."""
        try:
            self.config.save()
            self.post_message(self.ConfigChanged(self.config))
            self._show_status("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            self._show_status("Failed to save configuration", error=True)

    def reset_config(self):
        """Reset configuration to defaults."""
        try:
            self.config = DashboardConfig()
            self.load_config()
            self._show_status("Configuration reset to defaults")
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            self._show_status("Failed to reset configuration", error=True)

    def _show_status(self, message: str, error: bool = False):
        """Show status message."""
        if self._status:
            style = "red" if error else "green"
            self._status.update(f"[{style}]{message}[/]")
