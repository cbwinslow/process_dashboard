"""
Configuration management module for Process Dashboard.

This module handles loading, saving, and validating dashboard configurations,
including layout settings, theme preferences, and update intervals.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from rich.logging import RichHandler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("config")

@dataclass
class ThemeConfig:
    """Theme configuration settings."""
    background_color: str = "#000000"
    text_color: str = "#00FF00"
    accent_color: str = "#008000"
    border_color: str = "#004000"
    matrix_effect: bool = True

@dataclass
class LayoutConfig:
    """Layout configuration settings."""
    show_process_list: bool = True
    show_resource_monitor: bool = True
    show_disk_usage: bool = True
    show_config_panel: bool = True
    grid_rows: int = 2
    grid_columns: int = 2

@dataclass
class UpdateConfig:
    """Update interval configuration settings."""
    process_update_interval: float = 1.0
    resource_update_interval: float = 2.0
    disk_update_interval: float = 5.0

@dataclass
class DashboardConfig:
    """Main configuration class for the Process Dashboard."""
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    updates: UpdateConfig = field(default_factory=UpdateConfig)

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "process_dashboard"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    def save(self, config_path: Optional[Path] = None) -> None:
        """
        Save the current configuration to a YAML file.

        Args:
            config_path: Optional path to save the configuration file.
                       If not provided, uses the default path.
        """
        try:
            config_path = config_path or self.get_default_config_path()
            with open(config_path, 'w') as f:
                yaml.safe_dump(asdict(self), f, default_flow_style=False)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'DashboardConfig':
        """
        Load configuration from a YAML file.

        Args:
            config_path: Optional path to load the configuration file from.
                       If not provided, uses the default path.

        Returns:
            DashboardConfig: Loaded configuration object.
        """
        try:
            config_path = config_path or cls.get_default_config_path()
            if not config_path.exists():
                logger.info("No configuration file found, using defaults")
                return cls()

            with open(config_path) as f:
                config_data = yaml.safe_load(f)

            theme_data = config_data.get('theme', {})
            layout_data = config_data.get('layout', {})
            updates_data = config_data.get('updates', {})

            return cls(
                theme=ThemeConfig(**theme_data),
                layout=LayoutConfig(**layout_data),
                updates=UpdateConfig(**updates_data)
            )
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return cls()

    def validate(self) -> bool:
        """
        Validate the current configuration settings.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        try:
            # Validate update intervals
            if (self.updates.process_update_interval <= 0 or
                self.updates.resource_update_interval <= 0 or
                self.updates.disk_update_interval <= 0):
                logger.error("Update intervals must be positive numbers")
                return False

            # Validate grid dimensions
            if self.layout.grid_rows < 1 or self.layout.grid_columns < 1:
                logger.error("Grid dimensions must be positive numbers")
                return False

            # Validate color formats
            color_attrs = [
                self.theme.background_color,
                self.theme.text_color,
                self.theme.accent_color,
                self.theme.border_color
            ]
            for color in color_attrs:
                if not color.startswith('#') or len(color) != 7:
                    logger.error(f"Invalid color format: {color}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

def load_or_create_config(config_path: Optional[Path] = None) -> DashboardConfig:
    """
    Load existing configuration or create a new one with default values.

    Args:
        config_path: Optional path to the configuration file.

    Returns:
        DashboardConfig: Loaded or newly created configuration object.
    """
    config = DashboardConfig.load(config_path)
    if not config.validate():
        logger.warning("Invalid configuration detected, using defaults")
        config = DashboardConfig()
    return config

