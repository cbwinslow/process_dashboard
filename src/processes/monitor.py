"""
Process monitoring module for the Process Dashboard.

This module handles system process monitoring, resource tracking,
and data formatting for display.
"""

import os
import logging
import psutil
from typing import Dict, Any, List, Optional, Set
from time import time
from datetime import datetime

logger = logging.getLogger("dashboard.monitor")

class ProcessError(Exception):
    """Base class for process-related exceptions."""
    pass

ProcessInfo = Dict[str, Any]
SystemResources = Dict[str, Any]

class ProcessMonitor:
    """Monitors system processes and resources."""

    def __init__(self, history_interval: float = 60, history_length: int = 3600):
        """Initialize the process monitor.
        
        Args:
            history_interval: Interval between history snapshots in seconds
            history_length: Length of history to maintain in seconds
        """
        self.history_interval = history_interval
        self.history_length = history_length
        self.process_history: Dict[int, List[ProcessInfo]] = {}
        self.last_history_update = time()
        
        # Process tree cache
        self._process_tree_cache: Dict[int, Set[int]] = {}
        self._last_tree_update = 0
        self._tree_cache_ttl = 5  # Cache TTL in seconds
        
        # Initialize CPU monitoring
        psutil.cpu_percent(interval=None)  # First call to initialize CPU monitoring
        
        logger.info(f"ProcessMonitor initialized with {history_interval}s history interval")

    def get_process_list(self) -> Dict[int, ProcessInfo]:
        """Get list of current processes.
        
        Returns:
            Dict mapping PIDs to process information
        """
        processes = {}
        try:
            # Use a list comprehension to handle exceptions per process
            process_iter = list(psutil.process_iter(['pid', 'name', 'username', 'status', 'create_time']))
            
            for proc in process_iter:
                try:
                    # Get basic info first
                    proc_info = proc.info
                    pid = proc_info['pid']
                    
                    # Get CPU and memory info separately with error handling
                    try:
                        cpu_percent = proc.cpu_percent(interval=0.1)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        cpu_percent = 0.0
                        
                    try:
                        memory_percent = proc.memory_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        memory_percent = 0.0
                    
                    processes[pid] = {
                        'pid': pid,
                        'name': proc_info['name'],
                        'username': proc_info.get('username', 'unknown'),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'status': proc_info.get('status', 'unknown'),
                        'create_time': datetime.fromtimestamp(
                            proc_info.get('create_time', time())
                        ).strftime('%Y-%m-%d %H:%M:%S'),
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.error(f"Error getting process info for PID {getattr(proc, 'pid', 'unknown')}: {e}")
                    continue
            
            self._update_history(processes)
            return processes
            
        except Exception as e:
            logger.error(f"Failed to get process list: {e}")
            return {}

    def get_system_resources(self) -> SystemResources:
        """Get current system resource usage.
        
        Returns:
            Dictionary containing system resource information
        """
        try:
            # Get CPU usage without blocking
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Get memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Get load average safely
            try:
                load_avg = psutil.getloadavg()
            except Exception:
                load_avg = (0.0, 0.0, 0.0)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent,
                'load_avg': load_avg
            }
        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            return {
                'cpu_percent': 0.0,
                'memory_total': 0,
                'memory_available': 0,
                'memory_percent': 0.0,
                'swap_total': 0,
                'swap_used': 0,
                'swap_percent': 0.0,
                'load_avg': (0.0, 0.0, 0.0)
            }

    def get_process_tree(self, pid: int) -> Set[int]:
        """Get all descendant process IDs for a given PID.
        
        Args:
            pid: Process ID to get children for
            
        Returns:
            Set of all descendant process IDs
            
        Raises:
            ProcessLookupError: If the process does not exist
        """
        try:
            # Check cache freshness
            now = time()
            if (pid in self._process_tree_cache and 
                now - self._last_tree_update < self._tree_cache_ttl):
                return self._process_tree_cache[pid]

            # Build process tree recursively
            children: Set[int] = set()
            process = psutil.Process(pid)
            
            if not process.is_running():
                return set()
                
            def add_children(proc: psutil.Process) -> None:
                try:
                    for child in proc.children():
                        try:
                            if child.is_running():  # Skip zombie processes
                                children.add(child.pid)
                                add_children(child)
                        except (psutil.NoSuchProcess, psutil.ZombieProcess):
                            continue
                except psutil.AccessDenied:
                    logger.warning(f"Access denied to children of PID {proc.pid}")
                except Exception as e:
                    logger.error(f"Error accessing children of PID {proc.pid}: {e}")

            add_children(process)
            
            # Update cache
            self._process_tree_cache[pid] = children
            self._last_tree_update = now
            
            return children
            
        except psutil.NoSuchProcess:
            raise ProcessLookupError(f"Process {pid} not found")
        except psutil.AccessDenied:
            logger.warning(f"Access denied to process {pid}")
            return set()
        except Exception as e:
            logger.error(f"Error building process tree for PID {pid}: {e}")
            return set()

    def _update_history(self, current_processes: Dict[int, ProcessInfo]) -> None:
        """Update process history.
        
        Args:
            current_processes: Current process information
        """
        now = time()
        
        # Only update history at specified interval
        if now - self.last_history_update < self.history_interval:
            return
            
        try:
            # Update history for each process
            for pid, proc_info in current_processes.items():
                if pid not in self.process_history:
                    self.process_history[pid] = []
                self.process_history[pid].append(proc_info)
            
            # Cleanup old history entries
            cutoff_time = now - self.history_length
            for pid in list(self.process_history.keys()):
                # Remove old entries
                self.process_history[pid] = [
                    entry for entry in self.process_history[pid]
                    if datetime.strptime(entry['create_time'], '%Y-%m-%d %H:%M:%S').timestamp() > cutoff_time
                ]
                # Remove empty histories
                if not self.process_history[pid]:
                    del self.process_history[pid]
            
            self.last_history_update = now
            
        except Exception as e:
            logger.error(f"Failed to update process history: {e}")

    def format_process_data(self, process: ProcessInfo) -> Dict[str, str]:
        """Format process data for display.
        
        Args:
            process: Process information dictionary
            
        Returns:
            Formatted process information
        """
        try:
            return {
                "PID": str(process['pid']),
                "Name": str(process['name']),
                "CPU %": f"{float(process['cpu_percent']):.1f}%",
                "Memory %": f"{float(process['memory_percent']):.1f}%",
                "Status": str(process['status']),
                "User": str(process['username']),
                "Started": str(process['create_time'])
            }
        except Exception as e:
            logger.error(f"Failed to format process data: {e}")
            return {
                "PID": "N/A",
                "Name": "Error",
                "CPU %": "0.0%",
                "Memory %": "0.0%",
                "Status": "unknown",
                "User": "unknown",
                "Started": "unknown"
            }

    def format_resource_data(self, resources: SystemResources) -> Dict[str, str]:
        """Format system resource data for display.
        
        Args:
            resources: System resource information
            
        Returns:
            Formatted resource information
        """
        def format_bytes(bytes_val: int) -> str:
            try:
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if bytes_val < 1024:
                        return f"{bytes_val:.1f}{unit}"
                    bytes_val /= 1024
                return f"{bytes_val:.1f}TB"
            except Exception:
                return "0B"

        try:
            return {
                "CPU Usage": f"{resources['cpu_percent']:.1f}%",
                "Memory": (
                    f"{format_bytes(resources['memory_total'] - resources['memory_available'])} / "
                    f"{format_bytes(resources['memory_total'])} "
                    f"({resources['memory_percent']:.1f}%)"
                ),
                "Swap": (
                    f"{format_bytes(resources['swap_used'])} / "
                    f"{format_bytes(resources['swap_total'])} "
                    f"({resources['swap_percent']:.1f}%)"
                ),
                "Load Average": (
                    f"{resources['load_avg'][0]:.2f}, "
                    f"{resources['load_avg'][1]:.2f}, "
                    f"{resources['load_avg'][2]:.2f}"
                )
            }
        except Exception as e:
            logger.error(f"Failed to format resource data: {e}")
            return {
                "CPU Usage": "0.0%",
                "Memory": "N/A",
                "Swap": "N/A",
                "Load Average": "0.00, 0.00, 0.00"
            }
