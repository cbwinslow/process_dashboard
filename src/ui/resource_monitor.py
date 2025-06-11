"""
System resource monitor component for Process Dashboard.

This module implements the resource monitoring widget that displays
CPU, memory, and other system resource information.
"""

from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text
from textual.app import ComposeResult
from typing import Any

class ResourceMonitor(Widget):
    """System resource monitoring widget."""

    DEFAULT_CSS = """
    ResourceMonitor {
        height: 100%;
        border: solid green;
        background: #001100;
        color: #00ff00;
    }

    Static {
        padding: 1;
    }
    """

    def __init__(self) -> None:
        """Initialize the resource monitor."""
        super().__init__()
        self._stats = Static("")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield self._stats

    def format_bytes(self, bytes_val: int) -> str:
        """Format bytes into human readable string."""
        val = float(bytes_val)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if val < 1024:
                return f"{val:.1f}{unit}"
            val /= 1024.0
        return f"{val:.1f}TB"

    def update_resources(self, resources: dict) -> None:
        """Update displayed resource information."""
        try:
            text = Text()
            text.append("\n[System Resources]\n", style="bold green")
            text.append("─" * 30 + "\n\n", style="green")

            # CPU Usage
            text.append("CPU Usage: ", style="green")
            text.append(f"{resources.get('cpu_percent', 0):.1f}%\n\n", style="bright_green")

            # Memory Usage
            mem_total = resources.get('memory_total', 0)
            mem_available = resources.get('memory_available', 0)
            mem_used = mem_total - mem_available
            mem_percent = resources.get('memory_percent', 0)

            text.append("Memory Usage:\n", style="green")
            text.append(f"  Total: {self.format_bytes(mem_total)}\n", style="bright_green")
            text.append(f"  Used: {self.format_bytes(mem_used)}\n", style="bright_green")
            text.append(f"  Available: {self.format_bytes(mem_available)}\n", style="bright_green")
            text.append(f"  Usage: {mem_percent:.1f}%\n\n", style="bright_green")

            # Swap Usage
            swap_total = resources.get('swap_total', 0)
            swap_used = resources.get('swap_used', 0)
            swap_percent = resources.get('swap_percent', 0)

            text.append("Swap Usage:\n", style="green")
            text.append(f"  Total: {self.format_bytes(swap_total)}\n", style="bright_green")
            text.append(f"  Used: {self.format_bytes(swap_used)}\n", style="bright_green")
            text.append(f"  Usage: {swap_percent:.1f}%\n\n", style="bright_green")

            # Load Average
            load_avg = resources.get('load_avg', (0.0, 0.0, 0.0))
            text.append("Load Average:\n", style="green")
            text.append(f"  1min: {load_avg[0]:.2f}\n", style="bright_green")
            text.append(f"  5min: {load_avg[1]:.2f}\n", style="bright_green")
            text.append(f"  15min: {load_avg[2]:.2f}\n", style="bright_green")

            self._stats.update(text)
        except (ValueError, KeyError, TypeError):
            text = Text("Error updating resources", style="red")
            self._stats.update(text)

class TimeSeriesGraph:
    """Stub for TimeSeriesGraph for test compatibility."""
    def __init__(self) -> None:
        self.values: list[Any] = []
    def add_point(self, value: Any) -> None:
        self.values.append(value)
    def get_sparkline(self, width: int = 10) -> str:
        return "-" * width
