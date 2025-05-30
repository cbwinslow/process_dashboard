"""
Tests for the ResourceMonitor widget.
"""

import pytest
import pytest_asyncio
from textual.app import App, ComposeResult
from textual.widgets import DataTable, ProgressBar, Label
from textual.message import Message
import asyncio

from src.ui.resource_monitor import ResourceMonitor, TimeSeriesGraph

class TestApp(App):
    """Test application for ResourceMonitor widget."""
    CSS_PATH = None
    def compose(self) -> ComposeResult:
        yield ResourceMonitor()

@pytest.fixture
def app():
    """Create a test application instance."""
    return TestApp()

@pytest.mark.asyncio
async def test_resource_monitor_initialization(app):
    """Test that ResourceMonitor initializes correctly."""
    async with app.run_test():
        monitor = app.query_one(ResourceMonitor)
        assert monitor is not None
        assert monitor.cpu_total is not None
        assert isinstance(monitor.cpu_cores, dict)
        assert monitor.memory_usage is not None
        assert monitor.swap_usage is not None

@pytest.mark.asyncio
async def test_resource_monitor_composition(app):
    """Test that ResourceMonitor composes with required widgets."""
    async with app.run_test():
        monitor = app.query_one(ResourceMonitor)
        # Check for required sections
        assert monitor.query_one("#cpu-total") is not None
        assert monitor.query_one("#cpu-cores") is not None
        assert monitor.query_one("#memory-usage") is not None
        assert monitor.query_one("#swap-usage") is not None
        assert monitor.query_one("#network-stats") is not None
        assert monitor.query_one("#disk-stats") is not None
        assert monitor.query_one("#process-table") is not None

@pytest.mark.asyncio
async def test_resource_monitor_css_styling(app):
    """Test that ResourceMonitor CSS is valid and contains no invalid properties."""
    async with app.run_test():
        monitor = app.query_one(ResourceMonitor)
        css = monitor.DEFAULT_CSS
        
        # Verify no text-shadow in CSS
        assert "text-shadow" not in css
        
        # Verify expected valid properties are present
        assert "background:" in css
        assert "color:" in css
        assert "border:" in css

@pytest.mark.asyncio
async def test_time_series_graph():
    """Test TimeSeriesGraph functionality."""
    graph = TimeSeriesGraph(max_points=10)
    
    # Test adding points
    graph.add_point(0.5)
    assert len(graph.values) == 1
    assert graph.values[0] == 0.5
    
    # Test max points limit
    for i in range(15):
        graph.add_point(i / 15)
    assert len(graph.values) == 10  # Should be limited to max_points
    
    # Test sparkline generation
    sparkline = graph.get_sparkline(width=10)
    assert len(sparkline.plain) == 10

@pytest.mark.asyncio
async def test_resource_monitor_updates(app):
    """Test that monitor updates work correctly."""
    async with app.run_test():
        monitor = app.query_one(ResourceMonitor)
        
        # Let the monitor initialize
        await asyncio.sleep(0.1)
        
        # Test CPU update
        monitor.cpu_interval = 0.1
        await app._process_messages()
        await asyncio.sleep(0.2)  # Wait for update
        
        cpu_progress = monitor.query_one("#cpu-total ProgressBar")
        assert isinstance(cpu_progress, ProgressBar)
        assert hasattr(cpu_progress, "progress")
        assert 0 <= cpu_progress.progress <= 100
        
        # Test memory update
        monitor.memory_interval = 0.1
        await app._process_messages()
        await asyncio.sleep(0.2)  # Wait for update
        
        mem_progress = monitor.query_one("#memory-usage ProgressBar")
        assert isinstance(mem_progress, ProgressBar)
        assert hasattr(mem_progress, "progress")
        assert 0 <= mem_progress.progress <= 100

