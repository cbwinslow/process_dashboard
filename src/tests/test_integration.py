"""
Integration tests for Process Dashboard.

Tests the interaction between components and end-to-end functionality.
"""

import pytest

try:
    from textual.testing import TextualTestCase
except ImportError:
    pytest.skip("Skipping integration tests: textual.testing not available in this version of textual.", allow_module_level=True)

from textual.app import App
from textual.widgets import DataTable, Static

from processes.monitor import ProcessMonitor
from ui.process_list import ProcessListWidget
from ui.resource_monitor import ResourceMonitor
from ui.config_panel import ConfigPanel
from src.config.settings import DashboardConfig
from .test_helpers import MockProcess, MockSystemStats, create_mock_processes

class DashboardTestApp(App):
    """Test application with all main components."""
    
    def __init__(self):
        super().__init__()
        self.config = DashboardConfig()
        self.monitor = ProcessMonitor()

    def compose(self):
        yield ProcessListWidget(self.monitor)
        yield ResourceMonitor()
        yield ConfigPanel()

class TestDashboardIntegration(TextualTestCase):
    """Integration tests for the complete dashboard."""

    async def test_component_interaction(self):
        """Test interaction between components."""
        async with self.run_test(DashboardTestApp()) as pilot:
            # Get main components
            process_list = pilot.app.query_one(ProcessListWidget)
            resource_monitor = pilot.app.query_one(ResourceMonitor)
            config_panel = pilot.app.query_one(ConfigPanel)
            
            assert all([process_list, resource_monitor, config_panel])
            
            # Change update interval
            interval_input = config_panel.query_one("#update_interval")
            await interval_input.press("5")
            await pilot.pause()
            
            # Verify monitor update interval changed
            assert pilot.app.monitor.history_interval == 5
            
            # Update process list
            table = process_list.query_one(DataTable)
            initial_count = table.row_count
            
            # Apply filter
            filter_input = process_list.query_one("#filter")
            await filter_input.press("p", "y", "t", "h", "o", "n")
            await pilot.pause()
            
            # Verify filter applied
            assert table.row_count <= initial_count
            
            # Update resources
            stats = MockSystemStats()
            resource_monitor.update_resources(stats.to_dict())
            
            # Verify resource display updated
            cpu_section = resource_monitor.query_one("CPUSection")
            assert f"{stats.cpu_percent:.1f}%" in cpu_section.render().plain

    async def test_process_control_flow(self, mock_psutil):
        """Test process control operations flow."""
        async with self.run_test(DashboardTestApp()) as pilot:
            process_list = pilot.app.query_one(ProcessListWidget)
            table = process_list.query_one(DataTable)
            
            # Select first process
            if table.row_count > 0:
                await table.press("down")
                first_pid = table.get_row_at(0)[0]
                
                # Try terminating process
                await table.press("t")
                await pilot.pause()
                
                # Verify status message
                status = process_list.query_one("#status", Static)
                assert "process" in status.render().plain.lower()
                
                # Verify process list updated
                updated_pids = [row[0] for row in table.rows]
                assert first_pid not in updated_pids

    async def test_configuration_persistence(self, temp_config_file):
        """Test configuration changes persist."""
        async with self.run_test(DashboardTestApp()) as pilot:
            config_panel = pilot.app.query_one(ConfigPanel)
            
            # Change multiple settings
            matrix_theme = config_panel.query_one("#matrix_theme")
            update_interval = config_panel.query_one("#update_interval")
            show_system = config_panel.query_one("#show_system")
            
            # Toggle settings
            await matrix_theme.press("space")
            await update_interval.press("5")
            await show_system.press("space")
            
            # Save configuration
            save_button = config_panel.query_one("#save")
            await save_button.press("enter")
            await pilot.pause()
            
            # Create new app instance
            new_app = DashboardTestApp()
            new_config = DashboardConfig(temp_config_file)
            
            # Verify settings persisted
            assert new_config.matrix_theme == matrix_theme.value
            assert new_config.update_interval == 5
            assert new_config.show_system == show_system.value

    async def test_resource_monitoring_flow(self):
        """Test resource monitoring update flow."""
        async with self.run_test(DashboardTestApp()) as pilot:
            resource_monitor = pilot.app.query_one(ResourceMonitor)
            
            # Create series of updates
            stats = MockSystemStats()
            initial_stats = stats.to_dict()
            resource_monitor.update_resources(initial_stats)
            
            # Modify stats
            stats.cpu_percent = 75.0
            stats.memory_total -= 1024 * 1024 * 1024  # Decrease by 1GB
            updated_stats = stats.to_dict()
            
            # Update display
            resource_monitor.update_resources(updated_stats)
            await pilot.pause()
            
            # Verify updates reflected
            cpu_section = resource_monitor.query_one("CPUSection")
            memory_section = resource_monitor.query_one("MemorySection")
            
            assert "75.0%" in cpu_section.render().plain
            assert "15.0GB" in memory_section.render().plain

    async def test_error_handling_integration(self):
        """Test error handling across components."""
        async with self.run_test(DashboardTestApp()) as pilot:
            process_list = pilot.app.query_one(ProcessListWidget)
            resource_monitor = pilot.app.query_one(ResourceMonitor)
            
            # Test invalid process data
            table = process_list.query_one(DataTable)
            initial_count = table.row_count
            
            # Force error in process list
            pilot.app.monitor.process_history = {"invalid": "data"}
            await pilot.pause()
            
            # Verify graceful handling
            assert table.row_count >= 0
            
            # Test invalid resource data
            invalid_resources = {"cpu_percent": "invalid"}
            resource_monitor.update_resources(invalid_resources)
            
            # Verify components still responsive
            assert process_list.query_one(DataTable) is not None
            assert resource_monitor.query_one("CPUSection") is not None

    async def test_performance_with_large_dataset(self):
        """Test performance with large number of processes."""
        async with self.run_test(DashboardTestApp()) as pilot:
            process_list = pilot.app.query_one(ProcessListWidget)
            
            # Create large dataset
            mock_processes = create_mock_processes(count=1000)
            
            # Update process list
            table = process_list.query_one(DataTable)
            initial_render_time = await pilot.measure_time(
                lambda: pilot.app.monitor._update_history(mock_processes)
            )
            
            # Verify reasonable performance
            assert initial_render_time < 1.0  # Should update within 1 second
            
            # Test filtering performance
            filter_input = process_list.query_one("#filter")
            filter_time = await pilot.measure_time(
                lambda: filter_input.press("test")
            )
            
            # Verify filter performance
            assert filter_time < 0.5  # Should filter within 0.5 seconds

    async def test_theme_integration(self):
        """Test theme changes affect all components."""
        async with self.run_test(DashboardTestApp()) as pilot:
            config_panel = pilot.app.query_one(ConfigPanel)
            process_list = pilot.app.query_one(ProcessListWidget)
            resource_monitor = pilot.app.query_one(ResourceMonitor)
            
            # Toggle matrix theme
            matrix_theme = config_panel.query_one("#matrix_theme")
            initial_state = matrix_theme.value
            await matrix_theme.press("space")
            await pilot.pause()
            
            # Verify theme applied
            assert "green" in str(process_list.render())
            assert "green" in str(resource_monitor.render())
            
            # Restore theme
            matrix_theme.value = initial_state

    async def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts work across components."""
        async with self.run_test(DashboardTestApp()) as pilot:
            # Test global shortcuts
            await pilot.press("c")  # Toggle config
            assert pilot.app.query_one(ConfigPanel).has_focus
            
            await pilot.press("f")  # Focus filter
            assert pilot.app.query_one("#filter").has_focus
            
            await pilot.press("r")  # Refresh
            assert pilot.app.query_one(ProcessListWidget) is not None
