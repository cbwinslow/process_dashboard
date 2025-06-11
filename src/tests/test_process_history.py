"""
Unit tests for ProcessHistory module.
"""
import time
import pytest
from src.processes.history import ProcessHistory

def test_add_and_get_history():
    ph = ProcessHistory(max_length=3)
    ph.add_snapshot({'pid': 1, 'cpu': 10})
    ph.add_snapshot({'pid': 2, 'cpu': 20})
    ph.add_snapshot({'pid': 3, 'cpu': 30})
    assert len(ph.get_history()) == 3
    # Test max_length enforcement
    ph.add_snapshot({'pid': 4, 'cpu': 40})
    assert len(ph.get_history()) == 3
    assert ph.get_history()[0]['pid'] == 2

def test_get_history_key():
    ph = ProcessHistory()
    ph.add_snapshot({'pid': 1, 'cpu': 10, 'mem': 100})
    ph.add_snapshot({'pid': 2, 'cpu': 20, 'mem': 200})
    cpu_hist = ph.get_history('cpu')
    assert all('cpu' in h for h in cpu_hist)
    assert cpu_hist[0]['cpu'] == 10

def test_clear():
    ph = ProcessHistory()
    ph.add_snapshot({'pid': 1})
    ph.clear()
    assert len(ph.get_history()) == 0
