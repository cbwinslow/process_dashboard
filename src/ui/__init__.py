"""User interface package."""

from .resource_monitor import ResourceMonitor
from .config_panel import ConfigPanel
from ..version import __version__

__all__ = [
    'ResourceMonitor',
    'ConfigPanel',
    '__version__'
]
