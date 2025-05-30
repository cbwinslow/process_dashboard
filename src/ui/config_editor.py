"""
Configuration editor UI for Process Dashboard.

Provides a terminal-based interface for viewing and modifying
dashboard configuration settings.
"""

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button, Input, Select, Static, Switch, Tree,
    Label, TextArea, OptionList
)
from textual.binding import Binding
from textual.message import Message
from textual import on

from typing import Dict, Any, Optional
import logging
from pathlib import Path

from ..config.config_manager import (
    ConfigManager, DashboardConfig,
    DisplayConfig, ProcessConfig, ResourceConfig,
    SNMPConfig, GroupConfig, LoggingConfig
)

logger = logging.getLogger("dashboard.config_editor")

class ConfigurationScreen(Screen):
    """Configuration editor screen."""

    BINDINGS = [
        Binding("escape", "close_config", "Close", show=True),
        Binding("ctrl+s", "save_config", "Save", show=True),
        Binding("ctrl+r", "reset_config", "Reset", show=True),
    ]

    DEFAULT_CSS = """
    ConfigurationScreen {
        background: $background;
    }

    #config-container {
        width: 100%;
        height: 100%;
        layout: horizontal;
    }

    #config-tree {
        width: 30%;
        dock: left;
        border: solid $accent;
        padding: 1;
    }

    #config-editor {
        width: 70%;
        dock: right;
        border: solid $accent;
        padding: 1;
    }

    .config-section {
        margin: 1;
        padding: 1;
        border: solid $accent;
    }

    .config-row {
        layout: horizontal;
        height: 3;
        margin-bottom: 1;
    }

    .config-label {
        width: 30%;
        content-align: right middle;
        padding-right: 1;
    }

    .config-input {
        width: 70%;
    }

    Button {
        margin: 1;
    }

    #error-message {
        color: $error;
        margin: 1;
    }

    #success-message {
        color: $success;
        margin: 1;
    }
    """

    class ConfigChanged(Message):
        """Message emitted when configuration changes."""
        def __init__(self, config: DashboardConfig):
            self.config = config
            super().__init__()

    def __init__(self, config_manager: ConfigManager):
        """Initialize configuration screen.
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config_manager = config_manager
        self.current_config = config_manager.get_config()
        self.current_section = "display"
        self.modified = False

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal(id="config-container"):
            # Configuration navigation tree
            with Tree("Configuration", id="config-tree"):
                yield Tree.Node("Display")
                yield Tree.Node("Process Management")
                yield Tree.Node("Resources")
                yield Tree.Node("SNMP")
                yield Tree.Node("Groups")
                yield Tree.Node("Logging")
                yield Tree.Node("Keybindings")

            # Configuration editor panel
            with VerticalScroll(id="config-editor"):
                yield Static("Select a configuration section", id="editor-title")
                yield Static("", id="error-message")
                yield Static("", id="success-message")
                
                # Display section
                with VerticalScroll(classes="config-section", id="display-section"):
                    yield Label("Display Settings", classes="section-title")
                    with Horizontal(classes="config-row"):
                        yield Label("Refresh Rate (seconds)", classes="config-label")
                        yield Input(
                            value=str(self.current_config.display.refresh_rate),
                            id="refresh-rate"
                        )
                    
                    yield Label("Theme Colors", classes="section-title")
                    for color_name, color_value in self.current_config.display.theme.items():
                        with Horizontal(classes="config-row"):
                            yield Label(color_name.title(), classes="config-label")
                            yield Input(
                                value=color_value,
                                id=f"theme-{color_name}"
                            )
                    
                    yield Label("Display Columns", classes="section-title")
                    yield OptionList(
                        *self.current_config.display.columns,
                        id="display-columns"
                    )

                # Process section
                with VerticalScroll(classes="config-section", id="process-section"):
                    yield Label("Process Management", classes="section-title")
                    with Horizontal(classes="config-row"):
                        yield Label("Default Priority", classes="config-label")
                        yield Select(
                            [(p, p) for p in ["low", "normal", "high"]],
                            value=self.current_config.process.default_priority,
                            id="default-priority"
                        )
                    
                    with Horizontal(classes="config-row"):
                        yield Label("Auto Cleanup", classes="config-label")
                        yield Switch(
                            value=self.current_config.process.auto_cleanup,
                            id="auto-cleanup"
                        )
                    
                    with Horizontal(classes="config-row"):
                        yield Label("History Size", classes="config-label")
                        yield Input(
                            value=str(self.current_config.process.history_size),
                            id="history-size"
                        )

                # Resource section
                with VerticalScroll(classes="config-section", id="resource-section"):
                    yield Label("Resource Management", classes="section-title")
                    with Horizontal(classes="config-row"):
                        yield Label("Enable Limits", classes="config-label")
                        yield Switch(
                            value=self.current_config.resources.enable_limits,
                            id="enable-limits"
                        )
                    
                    yield Label("Default Limits", classes="section-title")
                    with Horizontal(classes="config-row"):
                        yield Label("Memory (MB)", classes="config-label")
                        yield Input(
                            value=str(self.current_config.resources.default_limits["memory_mb"]),
                            id="default-memory"
                        )
                    
                    with Horizontal(classes="config-row"):
                        yield Label("CPU (%)", classes="config-label")
                        yield Input(
                            value=str(self.current_config.resources.default_limits["cpu_percent"]),
                            id="default-cpu"
                        )

                # SNMP section
                with VerticalScroll(classes="config-section", id="snmp-section"):
                    yield Label("SNMP Settings", classes="section-title")
                    with Horizontal(classes="config-row"):
                        yield Label("Enable SNMP", classes="config-label")
                        yield Switch(
                            value=self.current_config.snmp.enabled,
                            id="snmp-enabled"
                        )
                    
                    with Horizontal(classes="config-row"):
                        yield Label("Default Port", classes="config-label")
                        yield Input(
                            value=str(self.current_config.snmp.default_port),
                            id="snmp-port"
                        )
                    
                    with Horizontal(classes="config-row"):
                        yield Label("Community", classes="config-label")
                        yield Input(
                            value=self.current_config.snmp.community,
                            id="snmp-community"
                        )

                # Groups section
                with VerticalScroll(classes="config-section", id="groups-section"):
                    yield Label("Process Groups", classes="section-title")
                    for group_name, group in self.current_config.groups.items():
                        with Horizontal(classes="config-row"):
                            yield Label(group_name, classes="config-label")
                            yield Input(
                                value=group.color,
                                id=f"group-color-{group_name}"
                            )
                            yield Select(
                                [(p, p) for p in ["low", "normal", "high"]],
                                value=group.priority,
                                id=f"group-priority-{group_name}"
                            )
                    
                    yield Button("Add Group", id="add-group")

                # Save/Reset buttons
                with Horizontal(classes="button-row"):
                    yield Button("Save Changes", variant="primary", id="save")
                    yield Button("Reset", variant="error", id="reset")

    def on_mount(self) -> None:
        """Handle screen mount."""
        self.show_section("display")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection."""
        section = event.node.label.lower().replace(" ", "-")
        self.show_section(section)

    def show_section(self, section: str) -> None:
        """Show configuration section.
        
        Args:
            section: Section name
        """
        # Hide all sections
        for section_id in ["display", "process", "resource", "snmp", "groups"]:
            try:
                self.query_one(f"#{section_id}-section").display = False
            except Exception:
                pass

        # Show selected section
        try:
            self.query_one(f"#{section}-section").display = True
            self.current_section = section
        except Exception as e:
            logger.error(f"Failed to show section {section}: {e}")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        self.modified = True
        self.update_config_value(event.input.id, event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        self.modified = True
        self.update_config_value(event.select.id, event.value)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes."""
        self.modified = True
        self.update_config_value(event.switch.id, event.value)

    def update_config_value(self, field_id: str, value: Any) -> None:
        """Update configuration value.
        
        Args:
            field_id: Field identifier
            value: New value
        """
        try:
            # Update configuration based on field ID
            if field_id.startswith("theme-"):
                color_name = field_id.replace("theme-", "")
                self.current_config.display.theme[color_name] = value
            
            elif field_id == "refresh-rate":
                self.current_config.display.refresh_rate = int(value)
            
            elif field_id == "default-priority":
                self.current_config.process.default_priority = value
            
            elif field_id == "auto-cleanup":
                self.current_config.process.auto_cleanup = value
            
            elif field_id == "history-size":
                self.current_config.process.history_size = int(value)
            
            elif field_id == "enable-limits":
                self.current_config.resources.enable_limits = value
            
            elif field_id == "default-memory":
                self.current_config.resources.default_limits["memory_mb"] = int(value)
            
            elif field_id == "default-cpu":
                self.current_config.resources.default_limits["cpu_percent"] = float(value)
            
            elif field_id == "snmp-enabled":
                self.current_config.snmp.enabled = value
            
            elif field_id == "snmp-port":
                self.current_config.snmp.default_port = int(value)
            
            elif field_id == "snmp-community":
                self.current_config.snmp.community = value
            
            elif field_id.startswith("group-"):
                parts = field_id.split("-")
                group_name = parts[2]
                if parts[1] == "color":
                    self.current_config.groups[group_name].color = value
                elif parts[1] == "priority":
                    self.current_config.groups[group_name].priority = value

        except Exception as e:
            logger.error(f"Failed to update config value: {e}")
            self.show_error(f"Invalid value: {e}")

    def action_save_config(self) -> None:
        """Save configuration changes."""
        try:
            if self.modified:
                self.config_manager.update_config(self.current_config)
                self.post_message(self.ConfigChanged(self.current_config))
                self.show_success("Configuration saved successfully")
                self.modified = False
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            self.show_error(f"Failed to save: {e}")

    def action_reset_config(self) -> None:
        """Reset configuration to defaults."""
        try:
            self.current_config = self.config_manager.get_config()
            self.modified = False
            self.show_success("Configuration reset to saved values")
            self.refresh()
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            self.show_error(f"Failed to reset: {e}")

    def show_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message
        """
        self.query_one("#error-message").update(message)
        self.query_one("#success-message").update("")

    def show_success(self, message: str) -> None:
        """Show success message.
        
        Args:
            message: Success message
        """
        self.query_one("#success-message").update(message)
        self.query_one("#error-message").update("")

    def action_close_config(self) -> None:
        """Close configuration screen."""
        if self.modified:
            # TODO: Show confirmation dialog
            pass
        self.app.pop_screen()
