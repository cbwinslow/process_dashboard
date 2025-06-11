"""
Unit tests for monitoring.metrics (MetricsCollector).
"""
import pytest
from src.monitoring.metrics import MetricsCollector

def test_collect_metrics():
    collector = MetricsCollector()
    metrics = collector.collect_metrics()
    assert isinstance(metrics, dict)
    assert 'cpu' in metrics
    assert 'memory' in metrics

def test_get_history():
    collector = MetricsCollector()
    collector.collect_metrics()
    history = collector.get_history('cpu')
    assert isinstance(history, list)

