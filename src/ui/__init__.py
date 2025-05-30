"""User interface package."""

from .process_list import ProcessListWidget
from .resource_monitor import ResourceMonitor
from .config_panel import ConfigPanel
from ..version import __version__

__all__ = [
    'ProcessListWidget',
    'ResourceMonitor',
    'ConfigPanel',
    '__version__'
]
