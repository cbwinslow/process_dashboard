"""
Matrix-themed configuration panel with advanced controls.
"""

from dataclasses import dataclass
from typing import Union, Optional
import re

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import (
    Label, Switch, Select, Button, Input, Static
)
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style

@dataclass
class NumericInput:
    """Configuration for numeric input validation."""
    min_value: float
    max_value: float
    step: float
    default: float
    suffix: str = ""

class ConfigPanel(Container):
    """Configuration panel with matrix theme."""

    # Configuration constraints
    NUMERIC_CONFIGS = {
        "opacity": NumericInput(50, 100, 5, 90, "%"),
        "process_update": NumericInput(0.5, 5.0, 0.5, 1.0, "s"),
        "resource_update": NumericInput(0.5, 5.0, 0.5, 2.0, "s"),
        "network_update": NumericInput(0.5, 5.0, 0.5, 1.0, "s"),
    }

    DEFAULT_CSS = """
    ConfigPanel {
        height: 100%;
        border: solid #003300;
        background: #000000 90%;
    }

    .config-section {
        padding: 1;
        margin-bottom: 1;
        border: solid #003300;
    }

    .config-section:focus-within {
        border: solid #00ff00;
        background: #001100;
    }

    .section-title {
        text-align: center;
        color: #00ff00;
        text-style: bold;
        margin-bottom: 1;
    }

    .config-row {
        height: 3;
        margin-bottom: 1;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        align: center middle;
    }

    .input-group {
        width: 100%;
        height: 100%;
        layout: horizontal;
        align: right middle;
    }

    Input {
        width: 10;
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    Input:focus {
        border: solid #00ff00;
    }

    Input.-invalid {
        border: solid red;
    }

    Static.input-suffix {
        width: 2;
        color: #00ff00;
        text-align: left;
        padding-left: 1;
    }

    Switch {
        background: #001100;
        margin-right: 1;
    }

    Switch.-on {
        background: #00ff00 50%;
    }

    Select {
        width: 30;
        background: #001100;
        color: #00ff00;
        border: solid #003300;
    }

    Select:focus {
        border: solid #00ff00;
    }

    Button {
        border: solid #003300;
        background: #001100;
        min-width: 15;
    }

    Button:hover {
        border: solid #00ff00;
        background: #002200;
    }

    #action-buttons {
        height: 3;
        align: center middle;
        background: #001100;
        padding: 0 1;
    }
    """

    def validate_numeric(self, value: str, config: NumericInput) -> Optional[float]:
        """Validate numeric input against constraints.
        
        Args:
            value: The input value to validate
            config: The configuration constraints

        Returns:
            The validated float value or None if invalid
        """
        try:
            num = float(value)
            if config.min_value <= num <= config.max_value:
                # Round to nearest step
                steps = round((num - config.min_value) / config.step)
                return config.min_value + (steps * config.step)
            return None
        except ValueError:
            return None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Display Settings
        with Vertical(classes="config-section"):
            yield Label("Display Settings", classes="section-title")
            with Container(classes="config-row"):
                yield Label("Matrix Effect")
                yield Switch(value=True)
            with Container(classes="config-row"):
                yield Label("Theme")
                yield Select(
                    [(name, name) for name in ["Matrix", "Matrix Light", "Matrix Dark"]],
                    value="Matrix"
                )
            with Container(classes="config-row"):
                yield Label("Opacity")
                with Horizontal(classes="input-group"):
                    yield Input(
                        value=str(self.NUMERIC_CONFIGS["opacity"].default),
                        id="opacity"
                    )
                    yield Static("%", classes="input-suffix")

        # Update Intervals
        with Vertical(classes="config-section"):
            yield Label("Update Intervals", classes="section-title")
            with Container(classes="config-row"):
                yield Label("Process Update")
                with Horizontal(classes="input-group"):
                    yield Input(
                        value=str(self.NUMERIC_CONFIGS["process_update"].default),
                        id="process_update"
                    )
                    yield Static("s", classes="input-suffix")
            with Container(classes="config-row"):
                yield Label("Resource Update")
                with Horizontal(classes="input-group"):
                    yield Input(
                        value=str(self.NUMERIC_CONFIGS["resource_update"].default),
                        id="resource_update"
                    )
                    yield Static("s", classes="input-suffix")
            with Container(classes="config-row"):
                yield Label("Network Update")
                with Horizontal(classes="input-group"):
                    yield Input(
                        value=str(self.NUMERIC_CONFIGS["network_update"].default),
                        id="network_update"
                    )
                    yield Static("s", classes="input-suffix")

        # Display Components
        with Vertical(classes="config-section"):
            yield Label("Components", classes="section-title")
            with Container(classes="config-row"):
                yield Label("Process List")
                yield Switch(value=True)
            with Container(classes="config-row"):
                yield Label("Resource Monitor")
                yield Switch(value=True)
            with Container(classes="config-row"):
                yield Label("Network Stats")
                yield Switch(value=True)
            with Container(classes="config-row"):
                yield Label("File Browser")
                yield Switch(value=True)

        # Actions
        with Horizontal(id="action-buttons"):
            yield Button("Apply", variant="primary")
            yield Button("Reset", variant="default")

    @on(Input.Changed)
    def validate_input(self, event: Input.Changed) -> None:
        """Validate numeric input fields."""
        if event.input.id in self.NUMERIC_CONFIGS:
            config = self.NUMERIC_CONFIGS[event.input.id]
            if valid_value := self.validate_numeric(event.value, config):
                event.input.remove_class("-invalid")
                if event.value != str(valid_value):
                    event.input.value = str(valid_value)
            else:
                event.input.add_class("-invalid")

    @on(Button.Pressed, "#apply-config")
    def apply_config(self) -> None:
        """Apply the current configuration."""
        # Validate all inputs first
        for input_id in self.NUMERIC_CONFIGS:
            input_widget = self.query_one(f"#{input_id}", Input)
            if "-invalid" in input_widget.classes:
                self.notify("Please fix invalid values before applying", severity="error")
                return

        self.notify("Configuration applied", severity="information")

    @on(Button.Pressed, "#reset-config")
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        # Reset numeric inputs
        for input_id, config in self.NUMERIC_CONFIGS.items():
            input_widget = self.query_one(f"#{input_id}", Input)
            input_widget.value = str(config.default)
            input_widget.remove_class("-invalid")

        # Reset switches
        for switch in self.query(Switch):
            switch.value = True

        # Reset theme
        theme_select = self.query_one(Select)
        theme_select.value = "Matrix"

        self.notify("Configuration reset to defaults", severity="information")

