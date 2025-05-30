"""
Tests for the FileBrowser widget.
"""

import pytest
import pytest_asyncio
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static, Select, Button
from src.ui.file_browser import ViewMode

from src.ui.file_browser import FileBrowser

# Base test application
class TestApp(App):
    """Test application for FileBrowser widget."""
    CSS_PATH = None
    def compose(self) -> ComposeResult:
        yield FileBrowser()

@pytest.fixture
def app():
    """Create a test application instance."""
    return TestApp()

@pytest.mark.asyncio
async def test_file_browser_initialization(app):
    """Test that FileBrowser initializes correctly."""
    async with app.run_test():
        browser = app.query_one(FileBrowser)
        assert browser is not None
        assert browser.current_path is not None

@pytest.mark.asyncio
async def test_file_browser_composition(app):
    """Test that FileBrowser composes with required widgets."""
    async with app.run_test():
        browser = app.query_one(FileBrowser)
        # Check for required widgets
        assert browser.query_one("#toolbar") is not None
        assert browser.query_one("#path-display") is not None
        assert browser.query_one("#content") is not None
        assert browser.query_one("#status-bar") is not None

@pytest.mark.asyncio
async def test_file_browser_css_styling(app):
    """Test that FileBrowser CSS is valid and contains no invalid properties."""
    async with app.run_test():
        browser = app.query_one(FileBrowser)
        css = browser.DEFAULT_CSS
        
        # Verify no text-shadow in CSS
        assert "text-shadow" not in css
        
        # Verify expected valid properties are present
        assert "background:" in css
        assert "color:" in css
        assert "border:" in css

@pytest.mark.asyncio
async def test_file_browser_navigation(app):
    """Test basic navigation functionality."""
    async with app.run_test():
        browser = app.query_one(FileBrowser)
        initial_path = browser.current_path
        
        # Test parent directory navigation
        parent_button = browser.query_one("#parent-dir")
        await app.press(parent_button)
        await app._process_messages()
        assert browser.current_path == initial_path.parent

        # Test home directory navigation
        home_button = browser.query_one("#home-dir")
        await app.press(home_button)
        await app._process_messages()
        assert str(browser.current_path).startswith("/home")

@pytest.mark.asyncio
async def test_file_browser_view_modes(app):
    """Test different view modes."""
    async with app.run_test():
        browser = app.query_one(FileBrowser)
        view_mode = browser.query_one("#view-mode")
        
        # Test details view
        view_mode.value = ViewMode.DETAILS
        await view_mode.post_message(Select.Changed(view_mode, value=ViewMode.DETAILS))
        await app._process_messages()
        assert browser.view_mode == ViewMode.DETAILS
        assert browser.query_one(DataTable) is not None
        
        # Test icons view
        view_mode.value = ViewMode.ICONS
        await view_mode.post_message(Select.Changed(view_mode, value=ViewMode.ICONS))
        await app._process_messages()
        assert browser.view_mode == ViewMode.ICONS
        assert browser.query_one(".file-grid") is not None

        # Test list view
        view_mode.value = ViewMode.LIST
        await view_mode.post_message(Select.Changed(view_mode, value=ViewMode.LIST))
        await app._process_messages()
        assert browser.view_mode == ViewMode.LIST

