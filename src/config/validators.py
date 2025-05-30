"""
Configuration validation for Process Dashboard.

Provides validation rules and checks for configuration settings.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger("dashboard.config.validators")

@dataclass
class ValidationError:
    """Configuration validation error."""
    path: str
    message: str
    value: Any

class ConfigValidator:
    """Configuration validation system."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[ValidationError] = []

    def validate_display_config(self, config: Dict[str, Any]) -> bool:
        """Validate display configuration.
        
        Args:
            config: Display configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        # Validate refresh rate
        refresh_rate = config.get("refresh_rate")
        if not isinstance(refresh_rate, int) or refresh_rate < 1:
            self.errors.append(
                ValidationError(
                    "display.refresh_rate",
                    "Refresh rate must be a positive integer",
                    refresh_rate
                )
            )
            valid = False

        # Validate theme colors
        theme = config.get("theme", {})
        for color_name, color_value in theme.items():
            if not self._is_valid_color(color_value):
                self.errors.append(
                    ValidationError(
                        f"display.theme.{color_name}",
                        "Invalid color format (use #RRGGBB)",
                        color_value
                    )
                )
                valid = False

        # Validate columns
        columns = config.get("columns", [])
        valid_columns = {
            "pid", "name", "cpu_percent", "memory_percent",
            "status", "user", "priority", "group"
        }
        for column in columns:
            if column not in valid_columns:
                self.errors.append(
                    ValidationError(
                        "display.columns",
                        f"Invalid column name: {column}",
                        column
                    )
                )
                valid = False

        return valid

    def validate_process_config(self, config: Dict[str, Any]) -> bool:
        """Validate process configuration.
        
        Args:
            config: Process configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        # Validate priority
        priority = config.get("default_priority")
        if priority not in {"low", "normal", "high"}:
            self.errors.append(
                ValidationError(
                    "process.default_priority",
                    "Priority must be 'low', 'normal', or 'high'",
                    priority
                )
            )
            valid = False

        # Validate history size
        history_size = config.get("history_size")
        if not isinstance(history_size, int) or history_size < 1:
            self.errors.append(
                ValidationError(
                    "process.history_size",
                    "History size must be a positive integer",
                    history_size
                )
            )
            valid = False

        # Validate thresholds
        for threshold_type in ["warning_thresholds", "critical_thresholds"]:
            thresholds = config.get(threshold_type, {})
            for metric, value in thresholds.items():
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    self.errors.append(
                        ValidationError(
                            f"process.{threshold_type}.{metric}",
                            "Threshold must be between 0 and 100",
                            value
                        )
                    )
                    valid = False

        return valid

    def validate_resource_config(self, config: Dict[str, Any]) -> bool:
        """Validate resource configuration.
        
        Args:
            config: Resource configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        # Validate limits
        default_limits = config.get("default_limits", {})
        
        memory_limit = default_limits.get("memory_mb")
        if not isinstance(memory_limit, int) or memory_limit < 1:
            self.errors.append(
                ValidationError(
                    "resources.default_limits.memory_mb",
                    "Memory limit must be a positive integer",
                    memory_limit
                )
            )
            valid = False

        cpu_limit = default_limits.get("cpu_percent")
        if not isinstance(cpu_limit, (int, float)) or cpu_limit < 0 or cpu_limit > 100:
            self.errors.append(
                ValidationError(
                    "resources.default_limits.cpu_percent",
                    "CPU limit must be between 0 and 100",
                    cpu_limit
                )
            )
            valid = False

        # Validate check interval
        check_interval = config.get("check_interval")
        if not isinstance(check_interval, int) or check_interval < 1:
            self.errors.append(
                ValidationError(
                    "resources.check_interval",
                    "Check interval must be a positive integer",
                    check_interval
                )
            )
            valid = False

        return valid

    def validate_snmp_config(self, config: Dict[str, Any]) -> bool:
        """Validate SNMP configuration.
        
        Args:
            config: SNMP configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        if config.get("enabled"):
            # Validate port
            port = config.get("default_port")
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.errors.append(
                    ValidationError(
                        "snmp.default_port",
                        "Port must be between 1 and 65535",
                        port
                    )
                )
                valid = False

            # Validate community
            community = config.get("community")
            if not community or not isinstance(community, str):
                self.errors.append(
                    ValidationError(
                        "snmp.community",
                        "Community string is required",
                        community
                    )
                )
                valid = False

            # Validate metrics
            metrics = config.get("metrics", [])
            valid_metrics = {
                "cpu_load", "memory_usage", "disk_io",
                "network_io"
            }
            for metric in metrics:
                if metric not in valid_metrics:
                    self.errors.append(
                        ValidationError(
                            "snmp.metrics",
                            f"Invalid metric: {metric}",
                            metric
                        )
                    )
                    valid = False

        return valid

    def validate_group_config(self, config: Dict[str, Any]) -> bool:
        """Validate group configuration.
        
        Args:
            config: Group configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        for group_name, group_config in config.items():
            # Validate color
            color = group_config.get("color")
            if not self._is_valid_color(color):
                self.errors.append(
                    ValidationError(
                        f"groups.{group_name}.color",
                        "Invalid color format (use #RRGGBB)",
                        color
                    )
                )
                valid = False

            # Validate priority
            priority = group_config.get("priority")
            if priority not in {"low", "normal", "high"}:
                self.errors.append(
                    ValidationError(
                        f"groups.{group_name}.priority",
                        "Priority must be 'low', 'normal', or 'high'",
                        priority
                    )
                )
                valid = False

        return valid

    def validate_logging_config(self, config: Dict[str, Any]) -> bool:
        """Validate logging configuration.
        
        Args:
            config: Logging configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        
        # Validate log level
        level = config.get("level")
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in valid_levels:
            self.errors.append(
                ValidationError(
                    "logging.level",
                    f"Invalid log level: {level}",
                    level
                )
            )
            valid = False

        # Validate file path
        file_path = config.get("file")
        if file_path:
            try:
                path = Path(file_path)
                if not path.parent.exists():
                    self.errors.append(
                        ValidationError(
                            "logging.file",
                            "Log directory does not exist",
                            file_path
                        )
                    )
                    valid = False
            except Exception:
                self.errors.append(
                    ValidationError(
                        "logging.file",
                        "Invalid log file path",
                        file_path
                    )
                )
                valid = False

        # Validate max size
        max_size = config.get("max_size", "")
        if not self._is_valid_size(max_size):
            self.errors.append(
                ValidationError(
                    "logging.max_size",
                    "Invalid max size format (use number + MB/GB)",
                    max_size
                )
            )
            valid = False

        return valid

    def validate_keybindings(self, config: Dict[str, str]) -> bool:
        """Validate keyboard shortcuts.
        
        Args:
            config: Keybinding configuration dictionary
            
        Returns:
            True if valid
        """
        valid = True
        required_actions = {
            "quit", "refresh", "kill_process", "stop_process",
            "resume_process", "toggle_details", "toggle_help"
        }
        
        # Check for required actions
        for action in required_actions:
            if action not in config:
                self.errors.append(
                    ValidationError(
                        f"keybindings.{action}",
                        f"Missing required keybinding for {action}",
                        None
                    )
                )
                valid = False

        # Check for duplicate keys
        used_keys = set()
        for action, key in config.items():
            if key in used_keys:
                self.errors.append(
                    ValidationError(
                        f"keybindings.{action}",
                        f"Duplicate key binding: {key}",
                        key
                    )
                )
                valid = False
            used_keys.add(key)

        return valid

    def _is_valid_color(self, color: str) -> bool:
        """Check if color string is valid.
        
        Args:
            color: Color string to check
            
        Returns:
            True if valid
        """
        if not color:
            return False
        return bool(re.match(r"^#[0-9A-Fa-f]{6}$", color))

    def _is_valid_size(self, size: str) -> bool:
        """Check if size string is valid.
        
        Args:
            size: Size string to check
            
        Returns:
            True if valid
        """
        if not size:
            return False
        return bool(re.match(r"^\d+[MG]B$", size))

    def get_errors(self) -> List[ValidationError]:
        """Get validation errors.
        
        Returns:
            List of validation errors
        """
        return self.errors

    def clear_errors(self) -> None:
        """Clear validation errors."""
        self.errors = []

    def format_errors(self) -> str:
        """Format validation errors as string.
        
        Returns:
            Formatted error string
        """
        if not self.errors:
            return "No validation errors"
            
        return "\n".join(
            f"{error.path}: {error.message} (value: {error.value})"
            for error in self.errors
        )
