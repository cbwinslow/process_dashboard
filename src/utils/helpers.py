"""
Utility functions for Process Dashboard.
"""
import os
import platform
from pathlib import Path

def get_config_path(filename: str) -> Path:
    """Return the platform-appropriate config file path."""
    if platform.system() == 'Linux':
        base = Path.home() / '.config' / 'process-dashboard'
    elif platform.system() == 'Darwin':
        base = Path.home() / 'Library' / 'Application Support' / 'process-dashboard'
    elif platform.system() == 'Windows':
        base = Path(os.environ.get('APPDATA', '')) / 'process-dashboard'
    else:
        base = Path('.')
    return base / filename

def human_readable_bytes(num, suffix='B'):
    """Convert a byte value into a human-readable string."""
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"
