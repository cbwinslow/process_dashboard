"""Configuration management package."""

from .settings import DashboardConfig, load_or_create_config
from ..version import __version__

__all__ = [
    'DashboardConfig',
    'load_or_create_config',
    '__version__'
]
