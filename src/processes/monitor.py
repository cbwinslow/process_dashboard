"""
Process monitoring module for Linux systems.

This module provides classes and functions for monitoring system processes
and resources using psutil. It includes support for real-time updates
and formatted output suitable for display in the dashboard.
"""

import psutil
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("monitor")

@dataclass
class ProcessInfo:
    """Information about a single process."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    create_time: datetime
    username: str
    cmdline: str
    num_threads: int
    nice: int

@dataclass
class SystemResources:
    """System-wide resource information."""
    cpu_percent: float
    cpu_count: int
    memory_total: int
    memory_available: int
    memory_used: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    disk_usage: Dict[str, Dict[str, int]]
    io_counters: Dict[str, int]

class ProcessMonitor:
    """Monitor system processes and resources."""

    def __init__(self, process_interval: float = 1.0, resource_interval: float = 2.0):
        """
        Initialize the process monitor.

        Args:
            process_interval: Update interval for process information in seconds
            resource_interval: Update interval for system resources in seconds
        """
        self.process_interval = process_interval
        self.resource_interval = resource_interval
        self.last_process_update = 0.0
        self.last_resource_update = 0.0
        self._cached_processes: Dict[int, ProcessInfo] = {}
        self._cached_resources: Optional[SystemResources] = None

    def get_process_list(self, force_update: bool = False) -> Dict[int, ProcessInfo]:
        """
        Get information about all running processes.

        Args:
            force_update: Force update regardless of update interval

        Returns:
            Dictionary mapping PIDs to ProcessInfo objects
        """
        current_time = time.time()
        if not force_update and current_time - self.last_process_update < self.process_interval:
            return self._cached_processes

        try:
            processes: Dict[int, ProcessInfo] = {}
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent',
                                           'status', 'create_time', 'username', 'cmdline',
                                           'num_threads', 'nice']):
                try:
                    pinfo = proc.info
                    processes[pinfo['pid']] = ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        cpu_percent=pinfo.get('cpu_percent', 0.0) or 0.0,
                        memory_percent=pinfo.get('memory_percent', 0.0) or 0.0,
                        status=pinfo['status'],
                        create_time=datetime.fromtimestamp(pinfo['create_time']),
                        username=pinfo['username'],
                        cmdline=' '.join(pinfo.get('cmdline', [])),
                        num_threads=pinfo.get('num_threads', 0),
                        nice=pinfo.get('nice', 0)
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logger.debug(f"Skipping process: {str(e)}")
                    continue

            self._cached_processes = processes
            self.last_process_update = current_time
            return processes

        except Exception as e:
            logger.error(f"Failed to get process list: {e}")
            return self._cached_processes

    def get_system_resources(self, force_update: bool = False) -> SystemResources:
        """
        Get system-wide resource usage information.

        Args:
            force_update: Force update regardless of update interval

        Returns:
            SystemResources object containing current system metrics
        """
        current_time = time.time()
        if not force_update and current_time - self.last_resource_update < self.resource_interval:
            return self._cached_resources or self._get_resources()

        return self._get_resources()

    def _get_resources(self) -> SystemResources:
        """
        Internal method to fetch system resource information.

        Returns:
            SystemResources object containing current system metrics
        """
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk information
            disk_usage = {}
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except (PermissionError, FileNotFoundError) as e:
                    logger.debug(f"Skipping disk {partition.mountpoint}: {e}")
                    continue

            # I/O information
            try:
                io = psutil.disk_io_counters()
                io_stats = {
                    'read_bytes': io.read_bytes,
                    'write_bytes': io.write_bytes,
                    'read_count': io.read_count,
                    'write_count': io.write_count
                }
            except Exception as e:
                logger.debug(f"Failed to get I/O stats: {e}")
                io_stats = {'read_bytes': 0, 'write_bytes': 0, 'read_count': 0, 'write_count': 0}

            resources = SystemResources(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total=memory.total,
                memory_available=memory.available,
                memory_used=memory.used,
                memory_percent=memory.percent,
                swap_total=swap.total,
                swap_used=swap.used,
                swap_percent=swap.percent,
                disk_usage=disk_usage,
                io_counters=io_stats
            )

            self._cached_resources = resources
            self.last_resource_update = current_time
            return resources

        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            if self._cached_resources:
                return self._cached_resources
            return SystemResources(0.0, 0, 0, 0, 0, 0.0, 0, 0, 0.0, {}, {})

    def format_process_data(self, process: ProcessInfo) -> Dict[str, str]:
        """
        Format process information for display.

        Args:
            process: ProcessInfo object to format

        Returns:
            Dictionary with formatted process information
        """
        return {
            "PID": str(process.pid),
            "Name": process.name,
            "CPU %": f"{process.cpu_percent:.1f}%",
            "Memory %": f"{process.memory_percent:.1f}%",
            "Status": process.status,
            "Started": process.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "User": process.username,
            "Command": (process.cmdline[:50] + "...") if len(process.cmdline) > 50 else process.cmdline,
            "Threads": str(process.num_threads),
            "Nice": str(process.nice)
        }

    def format_resource_data(self, resources: SystemResources) -> Dict[str, str]:
        """
        Format system resource information for display.

        Args:
            resources: SystemResources object to format

        Returns:
            Dictionary with formatted resource information
        """
        def format_bytes(bytes_: int) -> str:
            """Format bytes to human readable string."""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_ < 1024:
                    return f"{bytes_:.1f}{unit}"
                bytes_ /= 1024
            return f"{bytes_:.1f}PB"

        memory_used = format_bytes(resources.memory_used)
        memory_total = format_bytes(resources.memory_total)
        swap_used = format_bytes(resources.swap_used)
        swap_total = format_bytes(resources.swap_total)

        formatted = {
            "CPU Usage": f"{resources.cpu_percent:.1f}% (of {resources.cpu_count} CPUs)",
            "Memory": f"{memory_used} / {memory_total} ({resources.memory_percent:.1f}%)",
            "Swap": f"{swap_used} / {swap_total} ({resources.swap_percent:.1f}%)",
        }

        # Add disk usage information
        for mount_point, usage in resources.disk_usage.items():
            used = format_bytes(usage['used'])
            total = format_bytes(usage['total'])
            formatted[f"Disk {mount_point}"] = f"{used} / {total} ({usage['percent']}%)"

        # Add I/O statistics
        formatted["Disk I/O"] = (
            f"Read: {format_bytes(resources.io_counters['read_bytes'])} "
            f"Write: {format_bytes(resources.io_counters['write_bytes'])}"
        )

        return formatted


