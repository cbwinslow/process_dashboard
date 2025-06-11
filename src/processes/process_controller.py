"""
Advanced process management capabilities for Process Dashboard.

Provides process control, resource limiting, and organization features.
"""

from typing import Dict, List, Optional, Set, Any, Union
import logging
import os
import signal
import resource
import psutil
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ProcessState(Enum):
    """Process state enumeration."""
    RUNNING = "running"
    SLEEPING = "sleeping"
    DISK_SLEEP = "disk-sleep"
    STOPPED = "stopped"
    TRACING_STOP = "tracing-stop"
    ZOMBIE = "zombie"
    DEAD = "dead"
    WAKE_KILL = "wake-kill"
    WAKING = "waking"
    IDLE = "idle"
    LOCKED = "locked"
    WAITING = "waiting"
    UNKNOWN = "unknown"

class ProcessPriority(Enum):
    """Process priority levels."""
    VERY_HIGH = -20
    HIGH = -10
    NORMAL = 0
    LOW = 10
    VERY_LOW = 19

@dataclass
class ProcessGroup:
    """Process grouping information."""
    name: str
    color: str
    processes: Set[int]
    created: datetime
    metadata: Dict[str, Any]

class ProcessController:
    """Advanced process management capabilities."""
    
    # Color coding for process states
    STATE_COLORS = {
        ProcessState.RUNNING: "green",
        ProcessState.SLEEPING: "blue",
        ProcessState.STOPPED: "red",
        ProcessState.ZOMBIE: "magenta",
        ProcessState.DEAD: "red",
        ProcessState.WAITING: "yellow"
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize process controller.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or Path.home() / ".config" / "process-dashboard" / "controller.json"
        self.groups: Dict[str, ProcessGroup] = {}
        self.managed_processes: Dict[int, Dict[str, Any]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                    
                # Load process groups
                for group_data in config.get('groups', []):
                    group = ProcessGroup(
                        name=group_data['name'],
                        color=group_data['color'],
                        processes=set(group_data['processes']),
                        created=datetime.fromisoformat(group_data['created']),
                        metadata=group_data.get('metadata', {})
                    )
                    self.groups[group.name] = group
                    
                # Load process management settings
                self.managed_processes = config.get('managed_processes', {})
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'groups': [
                    {
                        'name': group.name,
                        'color': group.color,
                        'processes': list(group.processes),
                        'created': group.created.isoformat(),
                        'metadata': group.metadata
                    }
                    for group in self.groups.values()
                ],
                'managed_processes': self.managed_processes
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def set_memory_limit(self, pid: int, limit_mb: int) -> bool:
        """Set memory limit for process.
        
        Args:
            pid: Process ID
            limit_mb: Memory limit in megabytes
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            process = psutil.Process(pid)
            limit_bytes = limit_mb * 1024 * 1024
            
            # Set soft and hard limits
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
            
            self.managed_processes[pid] = {
                'memory_limit': limit_mb,
                'set_time': datetime.now().isoformat()
            }
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting memory limit for PID {pid}: {e}")
            return False

    def set_cpu_limit(self, pid: int, percent: float) -> bool:
        """Set CPU usage limit for process.
        
        Args:
            pid: Process ID
            percent: CPU usage limit (0-100)
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            process = psutil.Process(pid)
            
            # Calculate CPU affinity based on percentage
            cpu_count = psutil.cpu_count()
            cpu_limit = max(1, int(cpu_count * (percent / 100)))
            process.cpu_affinity(list(range(cpu_limit)))
            
            self.managed_processes[pid] = {
                'cpu_limit': percent,
                'set_time': datetime.now().isoformat()
            }
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting CPU limit for PID {pid}: {e}")
            return False

    def set_priority(self, pid: int, priority: Union[int, ProcessPriority]) -> bool:
        """Set process priority.
        
        Args:
            pid: Process ID
            priority: Priority level (-20 to 19) or ProcessPriority enum
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            process = psutil.Process(pid)
            
            if isinstance(priority, ProcessPriority):
                priority = priority.value
                
            # Validate priority range
            if not -20 <= priority <= 19:
                raise ValueError("Priority must be between -20 and 19")
                
            process.nice(priority)
            
            self.managed_processes[pid] = {
                'priority': priority,
                'set_time': datetime.now().isoformat()
            }
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting priority for PID {pid}: {e}")
            return False

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process.
        
        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            process = psutil.Process(pid)
            
            if force:
                process.kill()  # SIGKILL
            else:
                process.terminate()  # SIGTERM
                
            if pid in self.managed_processes:
                del self.managed_processes[pid]
                self._save_config()
                
            return True
            
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False

    def create_group(self, name: str, color: str = "white") -> Optional[ProcessGroup]:
        """Create new process group.
        
        Args:
            name: Group name
            color: Display color
            
        Returns:
            Created ProcessGroup or None if error occurs.
        """
        try:
            if name in self.groups:
                raise ValueError(f"Group already exists: {name}")
                
            group = ProcessGroup(
                name=name,
                color=color,
                processes=set(),
                created=datetime.now(),
                metadata={}
            )
            
            self.groups[name] = group
            self._save_config()
            
            return group
            
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return None

    def add_to_group(self, name: str, pid: int) -> bool:
        """Add process to group.
        
        Args:
            name: Group name
            pid: Process ID
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if name not in self.groups:
                return False
                
            self.groups[name].processes.add(pid)
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding process to group: {e}")
            return False

    def remove_from_group(self, name: str, pid: int) -> bool:
        """Remove process from group.
        
        Args:
            name: Group name
            pid: Process ID
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if name not in self.groups:
                return False
                
            self.groups[name].processes.discard(pid)
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing process from group: {e}")
            return False

    def get_process_state(self, pid: int) -> Optional[ProcessState]:
        """Get current state of process.
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessState enum value or None if error occurs.
        """
        try:
            process = psutil.Process(pid)
            status = process.status()
            try:
                return ProcessState(status.lower())
            except ValueError:
                return ProcessState.UNKNOWN
        except Exception as e:
            logger.error(f"Error getting process state: {e}")
            return ProcessState.UNKNOWN

    def get_process_color(self, pid: int) -> str:
        """Get display color for process.
        
        Args:
            pid: Process ID
            
        Returns:
            Color string.
        """
        # Check group colors first
        for group in self.groups.values():
            if pid in group.processes:
                return group.color
                
        # Fall back to state-based color
        state = self.get_process_state(pid)
        if state:
            return self.STATE_COLORS.get(state, "white")
            
        return "white"

    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """Get comprehensive process information.
        
        Args:
            pid: Process ID
            
        Returns:
            Dict containing process information.
        """
        try:
            process = psutil.Process(pid)
            
            info = {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'state': self.get_process_state(pid).value,
                'color': self.get_process_color(pid),
                'groups': [name for name, group in self.groups.items() if pid in group.processes],
                'managed': self.managed_processes.get(pid, {})
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {}

    def reset_process(self, pid: int) -> bool:
        """Reset all limits and restrictions for process.
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            process = psutil.Process(pid)
            
            # Reset CPU affinity
            process.cpu_affinity(list(range(psutil.cpu_count())))
            
            # Reset nice value
            process.nice(0)
            
            # Reset memory limit
            resource.setrlimit(resource.RLIMIT_AS, (-1, -1))
            
            # Remove from managed processes
            if pid in self.managed_processes:
                del self.managed_processes[pid]
                self._save_config()
                
            return True
            
        except Exception as e:
            logger.error(f"Error resetting process {pid}: {e}")
            return False

