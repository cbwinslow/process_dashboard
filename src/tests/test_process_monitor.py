"""
Unit tests for monitor.py (ProcessMonitor class).
"""
from src.processes.monitor import ProcessMonitor

def test_get_process_list():
    monitor = ProcessMonitor()
    processes = monitor.get_process_list()
    assert isinstance(processes, list)
    assert all('pid' in p for p in processes)

def test_get_process_by_pid():
    monitor = ProcessMonitor()
    processes = monitor.get_process_list()
    if processes:
        pid = processes[0]['pid']
        proc = monitor.get_process_by_pid(pid)
        assert proc['pid'] == pid

def test_refresh():
    monitor = ProcessMonitor()
    before = monitor.get_process_list()
    monitor.refresh()
    after = monitor.get_process_list()
    assert isinstance(after, list)
