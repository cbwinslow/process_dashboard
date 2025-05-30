"""Configuration management package."""

from .settings import DashboardConfig, load_or_create_config
from .logging_config import setup_logging, get_logger
from ..version import __version__

__all__ = [
    'DashboardConfig',
    'load_or_create_config',
    'setup_logging',
    'get_logger',
    '__version__'
]
