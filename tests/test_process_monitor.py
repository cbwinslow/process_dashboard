"""
Unit tests for the ProcessMonitor class.

Tests cover:
- Process listing functionality
- System resource monitoring
- Process tree mapping
- History tracking
- Error handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import psutil
from typing import Dict, List, Set
from src.processes.monitor import (
    ProcessMonitor,
    ProcessInfo,
    SystemResources,
    ProcessHistoryEntry
)

# Test data
MOCK_PROCESS_INFO = {
    "pid": 1234,
    "name": "test_process",
    "status": "running",
    "cpu_percent": 2.5,
    "memory_percent": 1.5,
    "memory_info": {"rss": 1024000, "vms": 2048000},
    "username": "testuser",
    "create_time": datetime.now() - timedelta(hours=1),
    "num_threads": 4,
    "parent_pid": 1,
    "children": [1235, 1236],
    "cmdline": ["test_process", "--arg1", "--arg2"],
    "cwd": "/home/testuser"
}

MOCK_SYSTEM_RESOURCES = {
    "cpu_percent": 25.0,
    "memory_total": 16000000000,
    "memory_available": 8000000000,
    "memory_percent": 50.0,
    "swap_total": 4000000000,
    "swap_used": 1000000000,
    "swap_percent": 25.0,
    "disk_usage": {
        "/": {
            "total": 500000000000,
            "used": 250000000000,
            "free": 250000000000,
            "percent": 50.0
        }
    },
    "io_counters": {
        "read_bytes": 1000000,
        "write_bytes": 500000
    },
    "load_avg": (1.5, 1.0, 0.5)
}

@pytest.fixture
def mock_psutil():
    """Fixture to mock psutil functionality."""
    with patch("src.processes.monitor.psutil") as mock_psutil:
        # Mock Process class
        mock_process = MagicMock()
        mock_process.pid = MOCK_PROCESS_INFO["pid"]
        mock_process.name.return_value = MOCK_PROCESS_INFO["name"]
        mock_process.status.return_value = MOCK_PROCESS_INFO["status"]
        mock_process.cpu_percent.return_value = MOCK_PROCESS_INFO["cpu_percent"]
        mock_process.memory_percent.return_value = MOCK_PROCESS_INFO["memory_percent"]
        mock_process.memory_info()._asdict.return_value = MOCK_PROCESS_INFO["memory_info"]
        mock_process.username.return_value = MOCK_PROCESS_INFO["username"]
        mock_process.create_time.return_value = MOCK_PROCESS_INFO["create_time"].timestamp()
        mock_process.num_threads.return_value = MOCK_PROCESS_INFO["num_threads"]
        mock_process.ppid.return_value = MOCK_PROCESS_INFO["parent_pid"]
        mock_process.children.return_value = [
            MagicMock(pid=pid) for pid in MOCK_PROCESS_INFO["children"]
        ]
        mock_process.cmdline.return_value = MOCK_PROCESS_INFO["cmdline"]
        mock_process.cwd.return_value = MOCK_PROCESS_INFO["cwd"]

        # Mock process iteration
        mock_psutil.process_iter.return_value = [mock_process]
        
        # Mock system resources
        mock_psutil.cpu_percent.return_value = MOCK_SYSTEM_RESOURCES["cpu_percent"]
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=MOCK_SYSTEM_RESOURCES["memory_total"],
            available=MOCK_SYSTEM_RESOURCES["memory_available"],
            percent=MOCK_SYSTEM_RESOURCES["memory_percent"]
        )
        mock_psutil.swap_memory.return_value = MagicMock(
            total=MOCK_SYSTEM_RESOURCES["swap_total"],
            used=MOCK_SYSTEM_RESOURCES["swap_used"],
            percent=MOCK_SYSTEM_RESOURCES["swap_percent"]
        )
        mock_psutil.disk_partitions.return_value = [
            MagicMock(mountpoint="/")
        ]
        mock_psutil.disk_usage.return_value = MagicMock(
            **MOCK_SYSTEM_RESOURCES["disk_usage"]["/"]
        )
        mock_psutil.disk_io_counters.return_value = MagicMock(
            **MOCK_SYSTEM_RESOURCES["io_counters"]
        )
        mock_psutil.getloadavg.return_value = MOCK_SYSTEM_RESOURCES["load_avg"]

        yield mock_psutil

@pytest.fixture
def process_monitor():
    """Fixture to create a ProcessMonitor instance."""
    return ProcessMonitor(history_interval=1, history_length=3600)

def test_init(process_monitor):
    """Test ProcessMonitor initialization."""
    assert process_monitor.history_interval == 1
    assert process_monitor.history_length == 3600
    assert isinstance(process_monitor.process_history, dict)
    assert isinstance(process_monitor._process_tree_cache, dict)

def test_get_process_list(process_monitor, mock_psutil):
    """Test getting process list."""
    processes = process_monitor.get_process_list()
    
    assert len(processes) == 1
    process = processes[MOCK_PROCESS_INFO["pid"]]
    
    assert process["pid"] == MOCK_PROCESS_INFO["pid"]
    assert process["name"] == MOCK_PROCESS_INFO["name"]
    assert process["status"] == MOCK_PROCESS_INFO["status"]
    assert process["cpu_percent"] == MOCK_PROCESS_INFO["cpu_percent"]
    assert process["memory_percent"] == MOCK_PROCESS_INFO["memory_percent"]

def test_get_process_list_error_handling(process_monitor, mock_psutil):
    """Test error handling in get_process_list."""
    mock_psutil.process_iter.side_effect = Exception("Test error")
    
    with pytest.raises(OSError) as exc_info:
        process_monitor.get_process_list()
    
    assert "Failed to collect process information" in str(exc_info.value)

def test_get_system_resources(process_monitor, mock_psutil):
    """Test getting system resources."""
    resources = process_monitor.get_system_resources()
    
    assert resources["cpu_percent"] == MOCK_SYSTEM_RESOURCES["cpu_percent"]
    assert resources["memory_total"] == MOCK_SYSTEM_RESOURCES["memory_total"]
    assert resources["memory_available"] == MOCK_SYSTEM_RESOURCES["memory_available"]
    assert resources["memory_percent"] == MOCK_SYSTEM_RESOURCES["memory_percent"]
    assert resources["swap_total"] == MOCK_SYSTEM_RESOURCES["swap_total"]
    assert resources["swap_used"] == MOCK_SYSTEM_RESOURCES["swap_used"]
    assert resources["swap_percent"] == MOCK_SYSTEM_RESOURCES["swap_percent"]

def test_get_process_tree(process_monitor, mock_psutil):
    """Test getting process tree with multi-level hierarchy and cache verification."""
    # Create a mock process tree:
    # pid 1000 (root)
    #   ├── pid 1001 (child)
    #   │   └── pid 1002 (grandchild)
    #   └── pid 1003 (child)
    
    mock_root = MagicMock()
    mock_root.pid = 1000
    mock_root.is_running.return_value = True
    
    mock_child1 = MagicMock()
    mock_child1.pid = 1001
    mock_child1.is_running.return_value = True
    
    mock_grandchild = MagicMock()
    mock_grandchild.pid = 1002
    mock_grandchild.is_running.return_value = True
    
    mock_child2 = MagicMock()
    mock_child2.pid = 1003
    mock_child2.is_running.return_value = True
    
    # Set up process hierarchy
    mock_root.children.return_value = [mock_child1, mock_child2]
    mock_child1.children.return_value = [mock_grandchild]
    mock_child2.children.return_value = []
    mock_grandchild.children.return_value = []
    
    # Configure Process creation
    def get_process(pid):
        processes = {
            1000: mock_root,
            1001: mock_child1,
            1002: mock_grandchild,
            1003: mock_child2
        }
        return processes[pid]
    
    mock_psutil.Process.side_effect = get_process
    
    # First call - should build tree
    children = process_monitor.get_process_tree(1000)
    assert children == {1001, 1002, 1003}
    
    # Second call - should use cache
    cached_children = process_monitor.get_process_tree(1000)
    assert cached_children == children
    
    # Verify cache was used (Process not called again)
    assert mock_psutil.Process.call_count == 4  # One call for each process in first call

def test_get_process_tree_no_such_process(process_monitor, mock_psutil):
    """Test handling of NoSuchProcess exception in process tree building."""
    # Mock psutil.Process to raise NoSuchProcess
    mock_psutil.Process.side_effect = psutil.NoSuchProcess(pid=1234)
    
    with pytest.raises(ProcessLookupError) as exc_info:
        process_monitor.get_process_tree(1234)
    
    assert "Process 1234 not found" in str(exc_info.value)

def test_get_process_tree_access_denied(process_monitor, mock_psutil):
    """Test handling of AccessDenied exception in process tree building."""
    # Create mock process that raises AccessDenied when accessing children
    mock_process = MagicMock()
    mock_process.pid = 1234
    mock_process.is_running.return_value = True
    mock_process.children.side_effect = psutil.AccessDenied(1234)
    mock_psutil.Process.return_value = mock_process
    
    # Should return empty set when access is denied
    children = process_monitor.get_process_tree(1234)
    assert children == set()
    
    # Verify proper logging
    mock_process.children.assert_called_once()

def test_get_process_tree_zombie_process(process_monitor, mock_psutil):
    """Test handling of zombie processes in process tree building."""
    # Mock parent process
    mock_parent = MagicMock()
    mock_parent.pid = 1000
    mock_parent.is_running.return_value = True
    
    # Mock zombie child process
    mock_zombie = MagicMock()
    mock_zombie.pid = 1001
    mock_zombie.is_running.side_effect = psutil.ZombieProcess(1001)
    mock_zombie.children.return_value = []
    
    # Set up process hierarchy
    mock_parent.children.return_value = [mock_zombie]
    
    def get_process(pid):
        if pid == 1000:
            return mock_parent
        elif pid == 1001:
            raise psutil.ZombieProcess(1001)
        raise psutil.NoSuchProcess(pid)
    
    mock_psutil.Process.side_effect = get_process
    
    # Should exclude zombie process from tree
    children = process_monitor.get_process_tree(1000)
    assert children == set()

def test_process_tree_cache_expiration(process_monitor, mock_psutil):
    """Test process tree cache expiration and refresh."""
    mock_process = MagicMock()
    mock_process.pid = 1000
    mock_process.is_running.return_value = True
    
    mock_child = MagicMock()
    mock_child.pid = 1001
    mock_child.is_running.return_value = True
    mock_child.children.return_value = []
    
    # Set up process hierarchy with one child
    mock_process.children.return_value = [mock_child]
    
    def get_process(pid):
        if pid == 1000:
            return mock_process
        elif pid == 1001:
            return mock_child
        raise psutil.NoSuchProcess(pid)
    
    mock_psutil.Process.side_effect = get_process
    
    # First call - should get one child
    children = process_monitor.get_process_tree(1000)
    assert children == {1001}
    
    # Verify cache was used
    initial_call_count = mock_psutil.Process.call_count
    cached_children = process_monitor.get_process_tree(1000)
    assert cached_children == {1001}
    assert mock_psutil.Process.call_count == initial_call_count  # No additional calls
    
    # Force cache expiration
    process_monitor._last_tree_update -= process_monitor._tree_cache_ttl
    
    # Change process tree
    mock_process.children.return_value = []
    
    # Get updated tree after cache expiration
    children = process_monitor.get_process_tree(1000)
    assert children == set()
    assert mock_psutil.Process.call_count > initial_call_count  # Verify refresh occurred

def test_process_history_tracking(process_monitor, mock_psutil):
    """Test process history tracking."""
    # First update
    process_monitor._update_history_if_needed()
    
    # Force time to pass
    process_monitor.last_history_update -= timedelta(seconds=2)
    
    # Second update
    process_monitor._update_history_if_needed()
    
    history = process_monitor.get_process_history(MOCK_PROCESS_INFO["pid"])
    assert len(history) > 0
    assert isinstance(history[0], ProcessHistoryEntry)
    assert history[0].cpu_percent == MOCK_PROCESS_INFO["cpu_percent"]
    assert history[0].memory_percent == MOCK_PROCESS_INFO["memory_percent"]

def test_format_process_data(process_monitor):
    """Test process data formatting."""
    formatted = process_monitor.format_process_data(MOCK_PROCESS_INFO)
    
    assert formatted["PID"] == str(MOCK_PROCESS_INFO["pid"])
    assert formatted["Name"] == MOCK_PROCESS_INFO["name"]
    assert formatted["CPU %"] == f"{MOCK_PROCESS_INFO['cpu_percent']:.1f}%"
    assert formatted["Memory %"] == f"{MOCK_PROCESS_INFO['memory_percent']:.1f}%"
    assert formatted["Status"] == MOCK_PROCESS_INFO["status"]

def test_format_resource_data(process_monitor):
    """Test resource data formatting."""
    formatted = process_monitor.format_resource_data(MOCK_SYSTEM_RESOURCES)
    
    assert formatted["CPU Usage"] == f"{MOCK_SYSTEM_RESOURCES['cpu_percent']:.1f}%"
    assert "Memory" in formatted
    assert "Swap" in formatted
    assert "Load Average" in formatted

def test_history_cleanup(process_monitor):
    """Test that old history entries are cleaned up."""
    # Add old history entry
    old_entry = ProcessHistoryEntry(
        timestamp=datetime.now() - timedelta(seconds=process_monitor.history_length + 100),
        cpu_percent=1.0,
        memory_percent=1.0,
        status="running"
    )
    process_monitor.process_history[1234] = [old_entry]
    
    # Add new history entry
    new_entry = ProcessHistoryEntry(
        timestamp=datetime.now(),
        cpu_percent=2.0,
        memory_percent=2.0,
        status="running"
    )
    process_monitor.process_history[1234].append(new_entry)
    
    # Force cleanup
    process_monitor._update_history_if_needed()
    
    # Verify old entry was removed
    history = process_monitor.process_history[1234]
    assert len(history) == 1
    assert history[0].cpu_percent == 2.0

