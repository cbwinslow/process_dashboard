"""
Monitoring package for Process Dashboard.

Provides system monitoring, metrics collection, and alerts.
"""

from .alerts import AlertManager
from .metrics import MetricsCollector
from ..version import __version__

__all__ = ['AlertManager', 'MetricsCollector', '__version__']
