"""Version information."""

import os
from pathlib import Path

def get_version() -> str:
    """Get the current version of Process Dashboard."""
    version_file = Path(__file__).parent.parent / 'VERSION'
    try:
        with open(version_file) as f:
            return f.read().strip()
    except FileNotFoundError:
        return '0.1.0'  # Default version if file not found

__version__ = get_version()
