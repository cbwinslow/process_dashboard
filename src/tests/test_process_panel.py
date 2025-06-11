"""
Unit tests for ui.process_panel (ProcessManagementPanel class).
"""
import pytest
from src.ui.process_panel import ProcessManagementPanel
from src.tests.dummy_ui_deps import DummyProcessController, DummySNMPMonitor

def test_panel_init():
    panel = ProcessManagementPanel(process_controller=DummyProcessController(), snmp_monitor=DummySNMPMonitor())
    assert hasattr(panel, 'refresh') or hasattr(panel, 'update')

def test_panel_update(monkeypatch):
    panel = ProcessManagementPanel(process_controller=DummyProcessController(), snmp_monitor=DummySNMPMonitor())
    monkeypatch.setattr(panel, 'refresh', lambda: None)
    panel.update()
    # Should not raise
