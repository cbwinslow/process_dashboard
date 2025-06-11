"""
Unit tests for monitoring.alerts (AlertManager).
"""
import pytest
from src.monitoring.alerts import AlertManager

def test_check_thresholds():
    manager = AlertManager()
    metrics = {'cpu': 95, 'memory': 80}
    alerts = manager.check_thresholds(metrics)
    assert isinstance(alerts, list)

def test_config_set_threshold():
    manager = AlertManager()
    manager.config['cpu_threshold'] = 50
    metrics = {'cpu': 60}
    alerts = manager.check_thresholds(metrics)
    assert any('cpu' in str(a) for a in alerts)
