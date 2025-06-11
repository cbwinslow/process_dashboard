"""
Configuration management module for the Process Dashboard.

This module handles loading, saving, and managing application configuration settings.
"""

import os
import yaml
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("dashboard.config")

@dataclass
class ThemeConfig:
    """Theme configuration settings."""
    matrix_effect: bool = True
    background_color: str = "#000000"
    text_color: str = "#00ff00"
    accent_color: str = "#003300"
    highlight_color: str = "#008800"

@dataclass
class UpdateConfig:
    """Update interval configuration settings."""
    process_update_interval: float = 1.0  # seconds
    resource_update_interval: float = 2.0  # seconds
    disk_update_interval: float = 5.0     # seconds

@dataclass
class DisplayConfig:
    """Display configuration settings."""
    show_process_tree: bool = True
    show_system_resources: bool = True
    show_disk_usage: bool = True
    show_network_stats: bool = True

@dataclass
class DashboardConfig:
    """Main configuration class for the dashboard."""
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    updates: UpdateConfig = field(default_factory=UpdateConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)

def get_config_path() -> Path:
    """Get the path to the configuration file.
    
    Returns:
        Path: Path to the configuration file.
    """
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        base_path = Path(xdg_config)
    else:
        base_path = Path.home() / '.config'
    
    return base_path / 'process_dashboard' / 'config.yaml'

def create_default_config() -> DashboardConfig:
    """Create a default configuration instance.
    
    Returns:
        DashboardConfig: Default configuration object.
    """
    return DashboardConfig()

def save_config(config: DashboardConfig) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration object to save.
    """
    config_path = get_config_path()
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclass to dict
        config_dict = {
            'theme': {
                'matrix_effect': config.theme.matrix_effect,
                'background_color': config.theme.background_color,
                'text_color': config.theme.text_color,
                'accent_color': config.theme.accent_color,
                'highlight_color': config.theme.highlight_color,
            },
            'updates': {
                'process_update_interval': config.updates.process_update_interval,
                'resource_update_interval': config.updates.resource_update_interval,
                'disk_update_interval': config.updates.disk_update_interval,
            },
            'display': {
                'show_process_tree': config.display.show_process_tree,
                'show_system_resources': config.display.show_system_resources,
                'show_disk_usage': config.display.show_disk_usage,
                'show_network_stats': config.display.show_network_stats,
            }
        }
        
        # Save to file
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_dict, f)
            
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        raise

def load_config() -> Optional[DashboardConfig]:
    """Load configuration from file.
    
    Returns:
        Optional[DashboardConfig]: Loaded configuration or None if file doesn't exist.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return None
        
    try:
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
            
        if not config_dict:
            return None
            
        theme = ThemeConfig(
            matrix_effect=config_dict['theme'].get('matrix_effect', True),
            background_color=config_dict['theme'].get('background_color', "#000000"),
            text_color=config_dict['theme'].get('text_color', "#00ff00"),
            accent_color=config_dict['theme'].get('accent_color', "#003300"),
            highlight_color=config_dict['theme'].get('highlight_color', "#008800"),
        )
        
        updates = UpdateConfig(
            process_update_interval=config_dict['updates'].get('process_update_interval', 1.0),
            resource_update_interval=config_dict['updates'].get('resource_update_interval', 2.0),
            disk_update_interval=config_dict['updates'].get('disk_update_interval', 5.0),
        )
        
        display = DisplayConfig(
            show_process_tree=config_dict['display'].get('show_process_tree', True),
            show_system_resources=config_dict['display'].get('show_system_resources', True),
            show_disk_usage=config_dict['display'].get('show_disk_usage', True),
            show_network_stats=config_dict['display'].get('show_network_stats', True),
        )
        
        return DashboardConfig(theme=theme, updates=updates, display=display)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def load_or_create_config() -> DashboardConfig:
    """Load existing configuration or create a new one.
    
    Returns:
        DashboardConfig: Configuration object.
    """
    config = load_config()
    if config is None:
        config = create_default_config()
        try:
            save_config(config)
        except Exception as e:
            logger.warning(f"Failed to save default configuration: {e}")
    return config
