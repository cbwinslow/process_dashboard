"""
Tests for the ConfigPanel widget.
"""

import pytest
import pytest_asyncio
from textual.app import App, ComposeResult
from textual.widgets import Switch, Select, Input, Button

from src.ui.config_panel import ConfigPanel, NumericInput

class TestApp(App):
    CSS_PATH = None
    """Test application for ConfigPanel widget."""
    def compose(self) -> ComposeResult:
        yield ConfigPanel()

@pytest.fixture
def app():
    """Create a test application instance."""
    return TestApp()

@pytest.mark.asyncio
async def test_config_panel_initialization(app):
    """Test that ConfigPanel initializes correctly."""
    async with app.run_test():
        panel = app.query_one(ConfigPanel)
        assert panel is not None
        assert isinstance(panel.NUMERIC_CONFIGS, dict)
        for config in panel.NUMERIC_CONFIGS.values():
            assert isinstance(config, NumericInput)

@pytest.mark.asyncio
async def test_config_panel_composition(app):
    """Test that ConfigPanel composes with required widgets."""
    async with app.run_test():
        panel = app.query_one(ConfigPanel)
        
        # Check for numeric input fields
        for input_id in panel.NUMERIC_CONFIGS:
            assert panel.query_one(f"#{input_id}") is not None
        
        # Check for switches
        switches = panel.query(Switch)
        assert len(list(switches)) > 0
        
        # Check for theme selector
        assert panel.query_one(Select) is not None
        
        # Check for action buttons
        assert panel.query_one("#action-buttons") is not None

@pytest.mark.asyncio
async def test_config_panel_css_styling(app):
    """Test that ConfigPanel CSS is valid and contains no invalid properties."""
    async with app.run_test():
        panel = app.query_one(ConfigPanel)
        css = panel.DEFAULT_CSS
        
        # Verify no text-shadow in CSS
        assert "text-shadow" not in css
        
        # Verify expected valid properties are present
        assert "background:" in css
        assert "color:" in css
        assert "border:" in css

@pytest.mark.asyncio
async def test_numeric_input_validation(app):
    """Test numeric input validation."""
    async with app.run_test():
        panel = app.query_one(ConfigPanel)
        
        # Test opacity input
        opacity_input = panel.query_one("#opacity", Input)
        
        # Test valid value
        opacity_input.value = "75"
        await panel.post_message(Input.Changed(opacity_input, value="75"))
        await app._process_messages()
        assert not "-invalid" in opacity_input.classes
        assert float(opacity_input.value) == 75
        
        # Test invalid value (too high)
        opacity_input.value = "150"
        await panel.post_message(Input.Changed(opacity_input, value="150"))
        await app._process_messages()
        assert "-invalid" in opacity_input.classes
        
        # Test invalid value (too low)
        opacity_input.value = "25"
        await panel.post_message(Input.Changed(opacity_input, value="25"))
        await app._process_messages()
        assert "-invalid" in opacity_input.classes

@pytest.mark.asyncio
async def test_config_reset(app):
    """Test configuration reset functionality."""
    async with app.run_test():
        panel = app.query_one(ConfigPanel)
        
        # Modify some values
        opacity_input = panel.query_one("#opacity", Input)
        opacity_input.value = "75"
        await panel.post_message(Input.Changed(opacity_input, value="75"))
        await app._process_messages()
        
        # Find and click reset button
        reset_button = panel.query_one("Button#reset-config")
        await app.press(reset_button)
        await app._process_messages()
        
        # Verify values are reset to defaults
        assert opacity_input.value == str(panel.NUMERIC_CONFIGS["opacity"].default)
        assert not "-invalid" in opacity_input.classes

