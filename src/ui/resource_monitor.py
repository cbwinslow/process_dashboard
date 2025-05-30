"""
Matrix-themed system resource monitor with real-time statistics and graphs.

This module provides a Textual widget for monitoring system resources including:
- CPU usage (total and per-core)
- Memory and swap usage
- Network activity
- Disk I/O
- Process statistics

All visualizations use a matrix-inspired theme with neon green text and effects.
"""

import time
from typing import Dict, List, Optional, Deque
from datetime import datetime
from collections import deque
import psutil
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, DataTable, ProgressBar, Label, Tabs, TabPane
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style
from rich.console import Group

# Constants
MAX_HISTORY = 120  # 2 minutes at 1s intervals
MAX_PROCESSES = 50  # Maximum number of processes to display
SPARKLINE_WIDTH = 50  # Width of sparkline graphs

# Constants for time series data
MAX_HISTORY_POINTS = 120  # 2 minutes at 1s intervals
MAX_PROCESSES = 50  # Maximum number of processes to display

class TimeSeriesGraph:
    """Time series data visualization with matrix theme."""
    
    def __init__(self, max_points: int = MAX_HISTORY):
        self.max_points = max_points
        self.values: Deque[float] = deque(maxlen=max_points)
        self.timestamps: Deque[datetime] = deque(maxlen=max_points)
        
    def add_point(self, value: float) -> None:
        """Add a new data point."""
        normalized = min(1.0, max(0.0, value))  # Clamp to 0-1
        self.values.append(normalized)
        self.timestamps.append(datetime.now())
        
    def get_sparkline(self, width: int = SPARKLINE_WIDTH) -> Text:
        """Get sparkline representation of the data.
        
        Args:
            width: Width of the sparkline in characters.
            
        Returns:
            Text: Rich text object containing the styled sparkline.
        """
        if not self.values:
            return Text("▁" * width, style="rgb(0,128,0)")
        
        # Unicode blocks for different levels (8 levels)
        blocks = "▁▂▃▄▅▆▇█"
        
        # Scale values to fit width
        values = list(self.values)
        if len(values) < width:
            values.extend([0.0] * (width - len(values)))
        elif len(values) > width:
            chunk_size = len(values) // width
            values = [
                sum(values[i:i + chunk_size]) / chunk_size
                for i in range(0, len(values), chunk_size)
            ][:width]
        
        # Create sparkline with gradient colors
        result = Text()
        for val in values:
            block_idx = min(7, int(val * 8))
            green = int(128 + (127 * val))  # 128-255 range for green
            result.append(blocks[block_idx], style=f"rgb(0,{green},0)")
        
        return result

    def get_percentage(self) -> float:
        """Get the current percentage value."""
        return self.values[-1] * 100 if self.values else 0.0


class ResourceMonitor(Container):
    """Matrix-themed system resource monitor."""

    # Track update intervals
    cpu_interval = reactive(1.0)
    memory_interval = reactive(1.0)
    network_interval = reactive(1.0)
    disk_interval = reactive(1.0)
    process_interval = reactive(2.0)

    # CSS for matrix theme styling
    DEFAULT_CSS = """
    ResourceMonitor {
        layout: vertical;
        height: 100%;
        background: #000000;
    }

    .monitor-section {
        height: auto;
        border: solid #003300;
        margin: 0 1 1 1;
        padding: 1;
    }

    .monitor-section:focus-within {
        border: solid #00ff00;
        background: #001100 50%;
    }

    .section-title {
        text-align: center;
        background: #001100;
        color: #00ff00;
        text-style: bold;
        margin-bottom: 1;
    }

    .stat-label {
        color: #00ff00;
        text-style: bold;
        margin-right: 1;
    }

    .progress-bar {
        width: 100%;
        height: 1;
    }

    .progress-bar .bar {
        color: #00ff00;
        background: #003300;
    }

    DataTable {
        width: 100%;
        height: auto;
        background: #000000;
    }

    DataTable > .header {
        background: #001100;
        color: #00ff00;
        text-style: bold;
    }

    DataTable > .row {
        background: transparent;
        color: #00ff00;
    }

    DataTable > .row:hover {
        background: #001100;
    }

    DataTable > .row-highlighted {
        background: #002200;
    }

    .graph-container {
        margin: 0 1;
    }

    .graph-label {
        color: #00ff00;
        opacity: 0.8;
    }
    """

    def __init__(self):
        """Initialize the resource monitor."""
        super().__init__()
        
        # Initialize all monitoring components
        self.cpu_total = TimeSeriesGraph()
        self.cpu_cores: Dict[int, TimeSeriesGraph] = {}
        self.memory_usage = TimeSeriesGraph()
        self.swap_usage = TimeSeriesGraph()
        
        # Network monitoring
        self.net_stats: Dict[str, Dict[str, TimeSeriesGraph]] = {}
        self.prev_net_counters = None
        self.net_update_time = time.time()
        
        # Disk monitoring
        self.disk_stats: Dict[str, Dict[str, TimeSeriesGraph]] = {}
        self.prev_disk_counters = None
        self.disk_update_time = time.time()
        
        # Error handling
        self.error_count = 0
        self.last_error_time = 0.0
        self.MAX_ERRORS = 3  # Maximum consecutive errors before notification
        self.last_update = time.time()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # CPU Usage Section
        with Container(classes="monitor-section"):
            yield Label("CPU Usage", classes="section-title")
            with Vertical():
                with Container(id="cpu-total", classes="graph-container"):
                    yield Static("Total CPU", classes="stat-label")
                    yield ProgressBar(classes="progress-bar")
                yield Container(id="cpu-cores", classes="graph-container")
        
        # Memory Usage Section
        with Container(classes="monitor-section"):
            yield Label("Memory Usage", classes="section-title")
            with Vertical():
                with Container(id="memory-usage", classes="graph-container"):
                    yield Static("RAM", classes="stat-label")
                    yield ProgressBar(classes="progress-bar")
                with Container(id="swap-usage", classes="graph-container"):
                    yield Static("Swap", classes="stat-label")
                    yield ProgressBar(classes="progress-bar")
        
        # Network Activity Section
        with Container(classes="monitor-section"):
            yield Label("Network Activity", classes="section-title")
            with Tabs():
                yield TabPane("Graph View")
                with Container(id="network-stats", classes="graph-container"):
                    yield DataTable()
        
        # Disk I/O Section
        with Container(classes="monitor-section"):
            yield Label("Disk I/O", classes="section-title")
            with Tabs():
                yield TabPane("Graph View")
                with Container(id="disk-stats", classes="graph-container"):
                    yield DataTable()
        
        # Process List Section
        with Container(classes="monitor-section"):
            yield Label("Process List", classes="section-title")
            yield DataTable(
                id="process-table",
                zebra_stripes=True,
                cursor_type="row"
            )

    def on_mount(self) -> None:
        """Handle widget mount."""
        try:
            # Initialize network interface history
            for interface in psutil.net_if_stats():
                self.net_stats[interface] = {
                    'sent': TimeSeriesGraph(),
                    'received': TimeSeriesGraph()
                }
            
            # Initialize disk history
            for disk in psutil.disk_partitions():
                self.disk_stats[disk.device] = {
                    'read': TimeSeriesGraph(),
                    'write': TimeSeriesGraph()
                }
            
            # Initialize process table
            process_table = self.query_one("#process-table", DataTable)
            process_table.add_columns(
                "PID", "Name", "CPU %", "Memory %",
                "Status", "Threads", "Read/s", "Write/s"
            )
            
            # Start update timers
            self.set_interval(self.cpu_interval, self.update_cpu)
            self.set_interval(self.memory_interval, self.update_memory)
            self.set_interval(self.network_interval, self.update_network)
            self.set_interval(self.disk_interval, self.update_disk)
            self.set_interval(self.process_interval, self.update_processes)
        except Exception as e:
            self.notify(f"Failed to initialize monitors: {e}", severity="error")


    def _format_size(self, bytes_: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_ < 1024:
                return f"{bytes_:.1f}{unit}"
            bytes_ /= 1024
        return f"{bytes_:.1f}PB"

    def handle_error(self, error: Exception, component: str) -> None:
        """Handle errors with rate limiting.
        
        Args:
            error: The exception that occurred
            component: Name of the component that failed
        """
        current_time = time.time()
        if current_time - self.last_error_time > 60:  # Reset counter after 1 minute
            self.error_count = 0
        
        self.error_count += 1
        self.last_error_time = current_time
        
        if self.error_count >= self.MAX_ERRORS:
            self.notify(
                f"{component} monitoring error: {str(error)}",
                severity="error",
                timeout=10
            )
            self.error_count = 0

    def update_cpu(self) -> None:
        """Update CPU usage statistics."""
        try:
            # Get total CPU usage
            total_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_total.add_point(total_percent / 100)
            
            # Update total CPU display
            cpu_total = self.query_one("#cpu-total", Container)
            if cpu_total:
                progress = cpu_total.query_one(ProgressBar)
                if progress:
                    progress.update(total=100, progress=total_percent)
                    
                text = Text()
                text.append("Total CPU: ", style="green")
                text.append(f"{total_percent:.1f}%\n", style="bold green")
                text.append(self.cpu_total.get_sparkline())
                cpu_total.mount(Static(text))
            
            # Update per-core CPU usage
            per_core = psutil.cpu_percent(percpu=True)
            cores_container = self.query_one("#cpu-cores", Container)
            if cores_container:
                cores_container.remove_children()
                for i, usage in enumerate(per_core):
                    if i not in self.cpu_cores:
                        self.cpu_cores[i] = TimeSeriesGraph()
                    self.cpu_cores[i].add_point(usage / 100)
                    
                    text = Text()
                    text.append(f"Core {i}: ", style="green")
                    text.append(f"{usage:.1f}%\n", style="bold green")
                    text.append(self.cpu_cores[i].get_sparkline())
                    cores_container.mount(Static(text))
                    
        except Exception as e:
            self.handle_error(e, "CPU")

    def update_memory(self) -> None:
        """Update memory usage statistics."""
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Update memory graphs
            self.memory_usage.add_point(memory.percent / 100)
            self.swap_usage.add_point(swap.percent / 100)
            
            # Update RAM display
            mem_container = self.query_one("#memory-usage", Container)
            if mem_container:
                progress = mem_container.query_one(ProgressBar)
                if progress:
                    progress.update(total=100, progress=memory.percent)
                    
                text = Text()
                text.append("RAM: ", style="green")
                text.append(
                    f"{self._format_size(memory.used)} / {self._format_size(memory.total)} "
                    f"({memory.percent:.1f}%)\n",
                    style="bold green"
                )
                text.append(self.memory_usage.get_sparkline())
                mem_container.mount(Static(text))
            
            # Update swap display
            swap_container = self.query_one("#swap-usage", Container)
            if swap_container:
                progress = swap_container.query_one(ProgressBar)
                if progress:
                    progress.update(total=100, progress=swap.percent)
                    
                text = Text()
                text.append("Swap: ", style="green")
                text.append(
                    f"{self._format_size(swap.used)} / {self._format_size(swap.total)} "
                    f"({swap.percent:.1f}%)\n",
                    style="bold green"
                )
                text.append(self.swap_usage.get_sparkline())
                swap_container.mount(Static(text))
                
        except Exception as e:
            self.handle_error(e, "Memory")

    def update_network(self) -> None:
        """Update network interface statistics."""
        try:
            current_time = time.time()
            counters = psutil.net_io_counters(pernic=True)
            
            if self.prev_net_counters is None:
                self.prev_net_counters = counters
                self.net_update_time = current_time
                return
                
            interval = current_time - self.net_update_time
            if interval < 0.1:  # Minimum update interval
                return
                
            # Update network stats table
            table = DataTable()
            table.add_columns(
                "Interface", "Upload", "Download", "Total",
                "Packets Up", "Packets Down"
            )
            
            for interface, stats in counters.items():
                if interface not in self.net_stats:
                    self.net_stats[interface] = {
                        'sent': TimeSeriesGraph(),
                        'received': TimeSeriesGraph()
                    }
                
                prev_stats = self.prev_net_counters[interface]
                
                # Calculate rates
                bytes_sent = (stats.bytes_sent - prev_stats.bytes_sent) / interval
                bytes_recv = (stats.bytes_recv - prev_stats.bytes_recv) / interval
                packets_sent = (stats.packets_sent - prev_stats.packets_sent) / interval
                packets_recv = (stats.packets_recv - prev_stats.packets_recv) / interval
                
                # Update graphs
                self.net_stats[interface]['sent'].add_point(bytes_sent / 1_000_000)  # MB/s
                self.net_stats[interface]['received'].add_point(bytes_recv / 1_000_000)  # MB/s
                
                # Add table row
                table.add_row(
                    interface,
                    f"↑ {self._format_size(bytes_sent)}/s",
                    f"↓ {self._format_size(bytes_recv)}/s",
                    self._format_size(stats.bytes_sent + stats.bytes_recv),
                    f"↑ {packets_sent:.0f}/s",
                    f"↓ {packets_recv:.0f}/s"
                )
            
            # Update display
            net_stats = self.query_one("#network-stats", Container)
            if net_stats:
                net_stats.remove_children()
                net_stats.mount(table)
                
                # Add graphs for each interface
                for interface in counters.keys():
                    text = Text()
                    text.append(f"\n{interface}\n", style="bold green")
                    text.append("Upload: ", style="green")
                    text.append(self.net_stats[interface]['sent'].get_sparkline())
                    text.append("\nDownload: ", style="green")
                    text.append(self.net_stats[interface]['received'].get_sparkline())
                    net_stats.mount(Static(text))
            
            self.prev_net_counters = counters
            self.net_update_time = current_time
            
        except Exception as e:
            self.handle_error(e, "Network")

    def update_disk(self) -> None:
        """Update disk I/O statistics."""
        try:
            current_time = time.time()
            counters = psutil.disk_io_counters(perdisk=True)
            
            if self.prev_disk_counters is None:
                self.prev_disk_counters = counters
                self.disk_update_time = current_time
                return
                
            interval = current_time - self.disk_update_time
            if interval < 0.1:  # Minimum update interval
                return
                
            # Update disk stats table
            table = DataTable()
            table.add_columns("Device", "Read", "Write", "Busy Time")
            
            for device, stats in counters.items():
                if device not in self.disk_stats:
                    self.disk_stats[device] = {
                        'read': TimeSeriesGraph(),
                        'write': TimeSeriesGraph()
                    }
                
                prev_stats = self.prev_disk_counters[device]
                
                # Calculate rates
                read_rate = (stats.read_bytes - prev_stats.read_bytes) / interval
                write_rate = (stats.write_bytes - prev_stats.write_bytes) / interval
                
                # Update graphs
                self.disk_stats[device]['read'].add_point(read_rate / 1_000_000)  # MB/s
                self.disk_stats[device]['write'].add_point(write_rate / 1_000_000)  # MB/s
                
                # Calculate busy time percentage
                if hasattr(stats, 'busy_time') and hasattr(prev_stats, 'busy_time'):
                    busy_delta = stats.busy_time - prev_stats.busy_time
                    busy_percent = min(100, (busy_delta / (interval * 1000)) * 100)
                else:
                    busy_percent = 0
                
                # Add table row
                table.add_row(
                    device,
                    f"← {self._format_size(read_rate)}/s",
                    f"→ {self._format_size(write_rate)}/s",
                    f"{busy_percent:.1f}%"
                )
            
            # Update display
            disk_stats = self.query_one("#disk-stats", Container)
            if disk_stats:
                disk_stats.remove_children()
                disk_stats.mount(table)
                
                # Add graphs for each device
                for device in counters.keys():
                    text = Text()
                    text.append(f"\n{device}\n", style="bold green")
                    text.append("Read: ", style="green")
                    text.append(self.disk_stats[device]['read'].get_sparkline())
                    text.append("\nWrite: ", style="green")
                    text.append(self.disk_stats[device]['write'].get_sparkline())
                    disk_stats.mount(Static(text))
            
            self.prev_disk_counters = counters
            self.disk_update_time = current_time
            
        except Exception as e:
            self.handle_error(e, "Disk I/O")

    def update_processes(self) -> None:
        """Update process list statistics."""
        try:
            # Get process table
            table = self.query_one("#process-table", DataTable)
            if not table:
                return
                
            table.clear()
            processes = []
            
            # Collect process information
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent',
                                           'memory_percent', 'status', 'num_threads']):
                try:
                    pinfo = proc.info
                    io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
                    
                    processes.append((
                        pinfo['cpu_percent'] or 0.0,
                        [
                            str(pinfo['pid']),
                            pinfo['name'][:20],
                            f"{pinfo['cpu_percent']:.1f}%" if pinfo['cpu_percent'] else "0.0%",
                            f"{pinfo['memory_percent']:.1f}%" if pinfo['memory_percent'] else "0.0%",
                            pinfo['status'],
                            str(pinfo['num_threads']),
                            f"{self._format_size(io_counters.read_bytes)}/s" if io_counters else "N/A",
                            f"{self._format_size(io_counters.write_bytes)}/s" if io_counters else "N/A"
                        ]
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage and take top processes
            processes.sort(reverse=True, key=lambda x: x[0])
            for _, row in processes[:MAX_PROCESSES]:
                table.add_row(*row)
                
        except Exception as e:
            self.handle_error(e, "Process List")


