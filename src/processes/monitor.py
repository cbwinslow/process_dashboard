"""
Process monitoring and management module.

This module provides comprehensive process monitoring capabilities including:
- Real-time process data collection
- CPU and memory usage tracking
- Process relationship mapping
- System resource monitoring
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Set, Tuple, TypedDict, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import psutil
from psutil._common import bytes2human

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ProcessInfo(TypedDict):
    """Type definition for process information."""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: Dict[str, int]
    username: str
    create_time: datetime
    num_threads: int
    parent_pid: Optional[int]
    children: List[int]
    cmdline: List[str]
    cwd: str

class SystemResources(TypedDict):
    """Type definition for system resource information."""
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    disk_usage: Dict[str, Dict[str, Union[int, float]]]
    io_counters: Dict[str, int]
    load_avg: Tuple[float, float, float]

@dataclass
class ProcessHistoryEntry:
    """Process history data structure."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    status: str

class ProcessMonitor:
    """
    Core process monitoring and management class.
    
    This class provides functionality for:
    - Real-time process monitoring
    - Resource usage tracking
    - Process relationship mapping
    - Historical data collection
    """

    def __init__(self, history_interval: int = 60, history_length: int = 3600):
        """
        Initialize the ProcessMonitor.

        Args:
            history_interval: Interval in seconds for collecting history data
            history_length: Maximum age in seconds for historical data
        """
        self.history_interval = history_interval
        self.history_length = history_length
        self.process_history: Dict[int, List[ProcessHistoryEntry]] = defaultdict(list)
        self.last_history_update = datetime.now()
        self._cpu_percent = psutil.cpu_percent(interval=0.1)  # Initial CPU reading
        
        # Cache for process tree relationships
        self._process_tree_cache: Dict[int, Set[int]] = {}
        self._last_tree_update = datetime.now()
        self._tree_cache_ttl = timedelta(seconds=5)  # Cache TTL
        
        logger.info("ProcessMonitor initialized with %ds history interval", history_interval)

    def get_process_list(self) -> Dict[int, ProcessInfo]:
        """
        Get a list of all current processes with detailed information.

        Returns:
            Dict mapping PIDs to process information

        Raises:
            OSError: If unable to collect process information
        """
        try:
            processes: Dict[int, ProcessInfo] = {}
            
            # Update history if needed
            self._update_history_if_needed()
            
            # Collect current CPU percentages
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    with proc.oneshot():
                        pid = proc.pid
                        processes[pid] = ProcessInfo(
                            pid=pid,
                            name=proc.name(),
                            status=proc.status(),
                            cpu_percent=proc.cpu_percent(),
                            memory_percent=proc.memory_percent(),
                            memory_info=proc.memory_info()._asdict(),
                            username=proc.username(),
                            create_time=datetime.fromtimestamp(proc.create_time()),
                            num_threads=proc.num_threads(),
                            parent_pid=proc.ppid(),
                            children=[child.pid for child in proc.children()],
                            cmdline=proc.cmdline(),
                            cwd=proc.cwd()
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logger.debug("Skipping process %d: %s", pid, str(e))
                    continue
                
            return processes
        except Exception as e:
            logger.error("Failed to get process list: %s", str(e))
            raise OSError(f"Failed to collect process information: {str(e)}")

    def get_process_tree(self, pid: int) -> Set[int]:
        """
        Get all child processes (recursively) for a given PID.

        Args:
            pid: Process ID to get children for

        Returns:
            Set of child process IDs

        Raises:
            ProcessLookupError: If the process doesn't exist
            PermissionError: If access is denied to any process in the tree
            RuntimeError: For other unexpected errors
            
        Note:
            This method uses caching to improve performance for frequently accessed
            process trees. The cache is automatically cleaned up based on TTL and
            process existence.
        """
        now = datetime.now()
        
        # Check cache first
        if pid in self._process_tree_cache:
            cache_entry = self._process_tree_cache[pid]
            if (now - self._last_tree_update) < self._tree_cache_ttl:
                return cache_entry
        
        children: Set[int] = set()
        
        def collect_children(parent_pid: int) -> None:
            """
            Recursively collect child PIDs for a given parent PID.
            
            This inner function handles process tree traversal while properly
            managing potential psutil exceptions.
            
            Args:
                parent_pid: PID of the parent process
            """
            try:
                parent = psutil.Process(parent_pid)
                
                # Use oneshot() for efficient system calls
                with parent.oneshot():
                    if not parent.is_running():
                        return
                        
                    for child in parent.children(recursive=False):
                        try:
                            if child.is_running():
                                children.add(child.pid)
                                collect_children(child.pid)
                        except psutil.NoSuchProcess:
                            logger.debug("Process %d disappeared while collecting children", child.pid)
                            continue
                        except psutil.AccessDenied:
                            logger.debug("Access denied to process %d while collecting children", child.pid)
                            continue
                        except psutil.ZombieProcess:
                            logger.debug("Process %d is zombie while collecting children", child.pid)
                            continue
                            
            except psutil.NoSuchProcess:
                logger.debug("Process %d no longer exists", parent_pid)
                return
            except psutil.AccessDenied:
                logger.debug("Access denied to process %d", parent_pid)
                return
            except psutil.ZombieProcess:
                logger.debug("Process %d is a zombie", parent_pid)
                return
            except Exception as e:
                logger.error("Unexpected error collecting children for PID %d: %s", parent_pid, str(e))
                return
        
        try:
            # Initial process existence check
            process = psutil.Process(pid)
            if not process.is_running():
                raise ProcessLookupError(f"Process {pid} is not running")
                
            collect_children(pid)
            
            # Update cache with collected children
            self._process_tree_cache[pid] = children.copy()
            self._last_tree_update = now
            
            # Clean old cache entries
            self._clean_process_tree_cache()
            
            return children
            
        except psutil.NoSuchProcess:
            raise ProcessLookupError(f"Process {pid} not found")
        except psutil.AccessDenied:
            raise PermissionError(f"Access denied to process {pid}")
        except Exception as e:
            logger.error("Failed to get process tree for PID %d: %s", pid, str(e))
            raise RuntimeError(f"Failed to get process tree: {str(e)}")
            
    def _clean_process_tree_cache(self) -> None:
        """
        Clean expired entries from the process tree cache.
        
        This method removes cache entries for processes that:
        1. No longer exist
        2. Have expired based on the cache TTL
        3. Have invalid data
        """
        now = datetime.now()
        expired = now - self._tree_cache_ttl
        
        # Create new cache with only valid entries
        valid_cache: Dict[int, Set[int]] = {}
        
        for pid, children in self._process_tree_cache.items():
            try:
                # Check if process still exists
                if not psutil.pid_exists(pid):
                    continue
                    
                # Validate children set
                valid_children = {
                    child_pid for child_pid in children
                    if psutil.pid_exists(child_pid)
                }
                
                if valid_children:  # Only keep entries with valid children
                    valid_cache[pid] = valid_children
                    
            except Exception as e:
                logger.debug("Error checking cache entry for PID %d: %s", pid, str(e))
                continue
        
        self._process_tree_cache = valid_cache

    def get_system_resources(self) -> SystemResources:
        """
        Get current system resource usage information.

        Returns:
            SystemResources object with current resource usage

        Raises:
            OSError: If unable to collect system information
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            virtual_memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk_usage = {
                disk.mountpoint: psutil.disk_usage(disk.mountpoint)._asdict()
                for disk in psutil.disk_partitions(all=False)
            }
            io_counters = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
            
            return SystemResources(
                cpu_percent=cpu_percent,
                memory_total=virtual_memory.total,
                memory_available=virtual_memory.available,
                memory_percent=virtual_memory.percent,
                swap_total=swap.total,
                swap_used=swap.used,
                swap_percent=swap.percent,
                disk_usage=disk_usage,
                io_counters=io_counters,
                load_avg=psutil.getloadavg()
            )
        except Exception as e:
            logger.error("Failed to get system resources: %s", str(e))
            raise OSError(f"Failed to collect system information: {str(e)}")

    def get_process_history(self, pid: int) -> List[ProcessHistoryEntry]:
        """
        Get historical data for a specific process.

        Args:
            pid: Process ID to get history for

        Returns:
            List of historical process data entries

        Raises:
            KeyError: If no history exists for the process
        """
        try:
            history = self.process_history.get(pid, [])
            if not history:
                raise KeyError(f"No history found for PID {pid}")
            
            # Clean old entries
            cutoff_time = datetime.now() - timedelta(seconds=self.history_length)
            history = [entry for entry in history if entry.timestamp > cutoff_time]
            self.process_history[pid] = history
            
            return history
        except Exception as e:
            logger.error("Failed to get process history for PID %d: %s", pid, str(e))
            raise

    def _update_history_if_needed(self) -> None:
        """
        Update process history if enough time has passed since last update.
        
        This method performs two main tasks:
        1. Collects current process statistics for history tracking
        2. Cleans up old history entries that exceed the history length
        
        The method uses proper exception handling and ensures atomic updates
        to prevent data corruption during concurrent access.
        """
        now = datetime.now()
        time_since_update = (now - self.last_history_update).total_seconds()
        
        if time_since_update >= self.history_interval:
            try:
                # Create temporary storage for new history entries
                new_entries: Dict[int, ProcessHistoryEntry] = {}
                
                # Collect current process information
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    try:
                        # Use oneshot() to get consistent readings
                        with proc.oneshot():
                            if not proc.is_running():
                                continue
                                
                            history_entry = ProcessHistoryEntry(
                                timestamp=now,
                                cpu_percent=proc.cpu_percent() or 0.0,  # Handle None
                                memory_percent=proc.memory_percent() or 0.0,  # Handle None
                                status=proc.status()
                            )
                            new_entries[proc.pid] = history_entry
                            
                    except psutil.NoSuchProcess:
                        logger.debug("Process disappeared while collecting history")
                        continue
                    except psutil.AccessDenied:
                        logger.debug("Access denied while collecting process history")
                        continue
                    except psutil.ZombieProcess:
                        logger.debug("Skipping zombie process in history collection")
                        continue
                    except Exception as e:
                        logger.error("Error collecting process history: %s", str(e))
                        continue
                
                # Calculate cutoff time for old entries
                cutoff_time = now - timedelta(seconds=self.history_length)
                
                # Update history with new entries and clean old ones
                for pid in list(self.process_history.keys()):
                    # Clean old entries
                    current_history = [
                        entry for entry in self.process_history[pid]
                        if entry.timestamp > cutoff_time
                    ]
                    
                    # Add new entry if it exists
                    if pid in new_entries:
                        current_history.append(new_entries[pid])
                    
                    # Update or remove history for this PID
                    if current_history:
                        self.process_history[pid] = current_history
                    else:
                        del self.process_history[pid]
                
                # Add history for new processes
                for pid, entry in new_entries.items():
                    if pid not in self.process_history:
                        self.process_history[pid] = [entry]
                
                self.last_history_update = now
                
            except Exception as e:
                logger.error("Failed to update process history: %s", str(e))
                # Don't update last_history_update on failure to ensure retry

    def format_process_data(self, process: ProcessInfo) -> Dict[str, str]:
        """
        Format process information for display.

        Args:
            process: ProcessInfo object to format

        Returns:
            Dictionary with formatted process information
        """
        try:
            return {
                "PID": str(process["pid"]),
                "Name": process["name"],
                "CPU %": f"{process['cpu_percent']:.1f}%",
                "Memory %": f"{process['memory_percent']:.1f}%",
                "Status": process["status"],
                "User": process["username"],
                "Started": process["create_time"].strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error("Failed to format process data: %s", str(e))
            return {
                "PID": str(process["pid"]),
                "Name": process["name"],
                "CPU %": "N/A",
                "Memory %": "N/A",
                "Status": "Error",
                "User": "N/A",
                "Started": "N/A"
            }

    def format_resource_data(self, resources: SystemResources) -> Dict[str, str]:
        """
        Format system resource information for display.

        Args:
            resources: SystemResources object to format

        Returns:
            Dictionary with formatted resource information
        """
        try:
            return {
                "CPU Usage": f"{resources['cpu_percent']:.1f}%",
                "Memory": (
                    f"{bytes2human(resources['memory_total'] - resources['memory_available'])} / "
                    f"{bytes2human(resources['memory_total'])} "
                    f"({resources['memory_percent']:.1f}%)"
                ),
                "Swap": (
                    f"{bytes2human(resources['swap_used'])} / "
                    f"{bytes2human(resources['swap_total'])} "
                    f"({resources['swap_percent']:.1f}%)"
                ),
                "Load Average": f"{resources['load_avg'][0]:.2f}, {resources['load_avg'][1]:.2f}, {resources['load_avg'][2]:.2f}"
            }
        except Exception as e:
            logger.error("Failed to format resource data: %s", str(e))
            return {
                "CPU Usage": "N/A",
                "Memory": "Error",
                "Swap": "Error",
                "Load Average": "N/A"
            }

class ProcessController:
    """Handles process control operations with proper error handling."""
    
    def __init__(self):
        """Initialize the process controller."""
        self.logger = logging.getLogger(__name__)
    
    def stop_process(self, pid: int, force: bool = False) -> bool:
        """
        Stop a process gracefully or forcefully.
        
        Args:
            pid: Process ID to stop
            force: If True, force kill the process
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            process = psutil.Process(pid)
            if force:
                process.kill()
            else:
                process.terminate()
            return True
        except psutil.NoSuchProcess:
            self.logger.warning(f"Process {pid} does not exist")
            return False
        except psutil.AccessDenied:
            self.logger.error(f"Access denied to stop process {pid}")
            return False
        except Exception as e:
            self.logger.error(f"Error stopping process {pid}: {e}")
            return False
    
    def set_priority(self, pid: int, priority: int) -> bool:
        """
        Set process priority/nice value.
        
        Args:
            pid: Process ID
            priority: Nice value (-20 to 19, lower is higher priority)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not -20 <= priority <= 19:
                raise ValueError("Priority must be between -20 and 19")
            
            process = psutil.Process(pid)
            process.nice(priority)
            return True
        except psutil.NoSuchProcess:
            self.logger.warning(f"Process {pid} does not exist")
            return False
        except psutil.AccessDenied:
            self.logger.error(f"Access denied to set priority for process {pid}")
            return False
        except Exception as e:
            self.logger.error(f"Error setting priority for process {pid}: {e}")
            return False

class AsyncMonitor:
    """Provides asynchronous monitoring capabilities with callbacks."""
    
    def __init__(self, monitor: ProcessMonitor, update_interval: float = 1.0):
        """
        Initialize the async monitor.
        
        Args:
            monitor: ProcessMonitor instance
            update_interval: Seconds between updates
        """
        self.monitor = monitor
        self.update_interval = update_interval
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._callbacks: List[Callable[[Dict[int, ProcessInfo], SystemResources], None]] = []
        
        # Resource usage thresholds for alerts
        self.thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 85.0,
            'swap_percent': 80.0,
            'disk_percent': 90.0
        }
    
    def add_callback(self, callback: Callable[[Dict[int, ProcessInfo], SystemResources], None]) -> None:
        """
        Add a callback for monitoring updates.
        
        Args:
            callback: Function to call with process and resource data
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[int, ProcessInfo], SystemResources], None]) -> None:
        """
        Remove a monitoring callback.
        
        Args:
            callback: Callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def start(self) -> None:
        """Start the monitoring loop."""
        if self.running:
            return
            
        self.running = True
        self._executor.submit(self._monitor_loop)
    
    def stop(self) -> None:
        """Stop the monitoring loop."""
        self.running = False
        self._executor.shutdown(wait=False)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                processes = self.monitor.get_process_list()
                resources = self.monitor.get_system_resources()
                
                # Check thresholds and generate alerts
                self._check_thresholds(processes, resources)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(processes, resources)
                    except Exception as e:
                        self.logger.error(f"Error in monitoring callback: {e}")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Prevent tight loop on persistent errors
    
    def _check_thresholds(self, processes: Dict[int, ProcessInfo], 
                         resources: SystemResources) -> None:
        """
        Check resource usage against thresholds and log alerts.
        
        Args:
            processes: Current process information
            resources: Current system resources
        """
        # System-wide checks
        if resources['cpu_percent'] > self.thresholds['cpu_percent']:
            self.logger.warning(
                f"High CPU usage: {resources['cpu_percent']:.1f}% "
                f"(threshold: {self.thresholds['cpu_percent']}%)"
            )
        
        if resources['memory_percent'] > self.thresholds['memory_percent']:
            self.logger.warning(
                f"High memory usage: {resources['memory_percent']:.1f}% "
                f"(threshold: {self.thresholds['memory_percent']}%)"
            )
        
        if resources['swap_percent'] > self.thresholds['swap_percent']:
            self.logger.warning(
                f"High swap usage: {resources['swap_percent']:.1f}% "
                f"(threshold: {self.thresholds['swap_percent']}%)"
            )
        
        # Check individual disk usage
        for mount, usage in resources['disk_usage'].items():
            if usage['percent'] > self.thresholds['disk_percent']:
                self.logger.warning(
                    f"High disk usage on {mount}: {usage['percent']:.1f}% "
                    f"(threshold: {self.thresholds['disk_percent']}%)"
                )
        
        # Process-specific checks
        for pid, proc in processes.items():
            if proc['cpu_percent'] > self.thresholds['cpu_percent']:
                self.logger.warning(
                    f"Process {pid} ({proc['name']}) high CPU usage: "
                    f"{proc['cpu_percent']:.1f}%"
                )
            
            if proc['memory_percent'] > self.thresholds['memory_percent']:
                self.logger.warning(
                    f"Process {pid} ({proc['name']}) high memory usage: "
                    f"{proc['memory_percent']:.1f}%"
                )
