"""
Configuration management for Process Dashboard.

Handles loading, validation, and application of user configuration settings.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import shutil

logger = logging.getLogger("dashboard.config")

@dataclass
class DisplayConfig:
    """Display configuration settings."""
    refresh_rate: int = 2
    theme: Dict[str, str] = field(default_factory=lambda: {
        "background": "#001100",
        "text": "#00FF00",
        "accent": "#008800",
        "error": "#FF0000",
        "warning": "#FFFF00",
        "success": "#00FF00"
    })
    columns: list = field(default_factory=lambda: [
        "pid", "name", "cpu_percent", "memory_percent",
        "status", "user", "priority", "group"
    ])

@dataclass
class ProcessConfig:
    """Process management configuration."""
    default_priority: str = "normal"
    auto_cleanup: bool = True
    history_size: int = 1000
    warning_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_percent": 80.0,
        "memory_percent": 80.0
    })
    critical_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_percent": 95.0,
        "memory_percent": 95.0
    })

@dataclass
class ResourceConfig:
    """Resource management configuration."""
    enable_limits: bool = True
    default_limits: Dict[str, Any] = field(default_factory=lambda: {
        "memory_mb": 1024,
        "cpu_percent": 50
    })
    check_interval: int = 5

@dataclass
class SNMPConfig:
    """SNMP monitoring configuration."""
    enabled: bool = False
    default_port: int = 161
    community: str = "public"
    metrics: list = field(default_factory=lambda: [
        "cpu_load", "memory_usage", "disk_io", "network_io"
    ])
    collection_interval: int = 30

@dataclass
class GroupConfig:
    """Process group configuration."""
    color: str
    priority: str

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: str = "dashboard.log"
    max_size: str = "10MB"
    backup_count: int = 3
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class DashboardConfig:
    """Main configuration container."""
    display: DisplayConfig = field(default_factory=DisplayConfig)
    process: ProcessConfig = field(default_factory=ProcessConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    snmp: SNMPConfig = field(default_factory=SNMPConfig)
    groups: Dict[str, GroupConfig] = field(default_factory=dict)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    keybindings: Dict[str, str] = field(default_factory=lambda: {
        "quit": "q",
        "refresh": "r",
        "kill_process": "k",
        "stop_process": "s",
        "resume_process": "c",
        "toggle_details": "d",
        "toggle_group_view": "g",
        "help": "h"
    })

class ConfigManager:
    """Configuration management system."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Optional configuration directory path
        """
        self.config_dir = config_dir or Path.home() / ".config" / "process-dashboard"
        self.config_file = self.config_dir / "config.yaml"
        self.config = DashboardConfig()

    def ensure_config_exists(self) -> None:
        """Ensure configuration file exists, create if not."""
        if not self.config_file.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy default config if available
            default_config = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
            if default_config.exists():
                shutil.copy(default_config, self.config_file)
            else:
                # Create new config file with defaults
                self.save_config()

    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            self.ensure_config_exists()
            
            with open(self.config_file) as f:
                config_data = yaml.safe_load(f)
            
            # Update configuration objects
            if config_data:
                if "display" in config_data:
                    self.config.display = DisplayConfig(**config_data["display"])
                
                if "process" in config_data:
                    self.config.process = ProcessConfig(**config_data["process"])
                
                if "resources" in config_data:
                    self.config.resources = ResourceConfig(**config_data["resources"])
                
                if "snmp" in config_data:
                    self.config.snmp = SNMPConfig(**config_data["snmp"])
                
                if "groups" in config_data:
                    self.config.groups = {
                        name: GroupConfig(**group_data)
                        for name, group_data in config_data["groups"].items()
                    }
                
                if "logging" in config_data:
                    self.config.logging = LoggingConfig(**config_data["logging"])
                
                if "keybindings" in config_data:
                    self.config.keybindings.update(config_data["keybindings"])
                
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_data = {
                "display": self.config.display.__dict__,
                "process": self.config.process.__dict__,
                "resources": self.config.resources.__dict__,
                "snmp": self.config.snmp.__dict__,
                "groups": {
                    name: group.__dict__
                    for name, group in self.config.groups.items()
                },
                "logging": self.config.logging.__dict__,
                "keybindings": self.config.keybindings
            }
            
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.safe_dump(config_data, f, default_flow_style=False)
            
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_config(self) -> DashboardConfig:
        """Get current configuration.
        
        Returns:
            Current configuration object
        """
        return self.config

    def update_config(self, config: DashboardConfig) -> None:
        """Update configuration with new settings.
        
        Args:
            config: New configuration object
        """
        self.config = config
        self.save_config()

    def get_theme(self) -> Dict[str, str]:
        """Get current theme colors.
        
        Returns:
            Dictionary of theme colors
        """
        return self.config.display.theme

    def get_keybinding(self, action: str) -> str:
        """Get key binding for action.
        
        Args:
            action: Action name
            
        Returns:
            Key binding or default if not found
        """
        return self.config.keybindings.get(action, "")
