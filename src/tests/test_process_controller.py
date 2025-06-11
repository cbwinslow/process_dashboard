"""
Unit tests for process_controller.py (ProcessController class).
"""
import pytest
from src.processes.process_controller import ProcessController

def test_list_processes():
    controller = ProcessController()
    plist = controller.list_processes()
    assert isinstance(plist, list)
    assert all('pid' in p for p in plist)

def test_filter_processes():
    controller = ProcessController()
    plist = controller.list_processes()
    filtered = controller.filter_processes(name='python')
    assert isinstance(filtered, list)
    # Can't guarantee a python process, but should not error

def test_sort_processes():
    controller = ProcessController()
    plist = controller.list_processes()
    sorted_list = controller.sort_processes(plist, key='cpu', reverse=True)
    assert isinstance(sorted_list, list)
    # Should be sorted by cpu descending if cpu key exists
