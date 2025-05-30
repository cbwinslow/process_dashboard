"""
Alert templates for Process Dashboard monitoring.

Provides customizable alert templates and notification formats.
"""

from typing import Dict, Any
from datetime import datetime
import json
from pathlib import Path

# Default alert templates
DEFAULT_TEMPLATES = {
    "cpu_high": {
        "title": "High CPU Usage",
        "message": "CPU usage is at {value}% (threshold: {threshold}%)",
        "level": "warning",
        "threshold": 80,
        "duration": 300,  # 5 minutes
        "actions": ["notify", "log"]
    },
    "memory_high": {
        "title": "High Memory Usage",
        "message": "Memory usage is at {value}% (threshold: {threshold}%)",
        "level": "warning",
        "threshold": 80,
        "duration": 300,
        "actions": ["notify", "log"]
    },
    "disk_critical": {
        "title": "Critical Disk Space",
        "message": "Disk usage is at {value}% (threshold: {threshold}%)",
        "level": "error",
        "threshold": 90,
        "duration": 0,  # Immediate
        "actions": ["notify", "log", "email"]
    },
    "process_count_high": {
        "title": "High Process Count",
        "message": "Process count is {value} (threshold: {threshold})",
        "level": "warning",
        "threshold": 500,
        "duration": 600,  # 10 minutes
        "actions": ["notify", "log"]
    },
    "network_errors": {
        "title": "Network Errors Detected",
        "message": "Network errors: {value} (threshold: {threshold})",
        "level": "warning",
        "threshold": 10,
        "duration": 300,
        "actions": ["notify", "log"]
    }
}

class AlertTemplate:
    """Alert template manager."""

    def __init__(self, config_path: Path = None):
        """Initialize template manager.
        
        Args:
            config_path: Path to template configuration
        """
        self.config_path = config_path or Path.home() / ".config" / "process-dashboard" / "alert_templates.json"
        self.templates = DEFAULT_TEMPLATES.copy()
        self.load_templates()

    def load_templates(self) -> None:
        """Load custom alert templates."""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    custom_templates = json.load(f)
                    self.templates.update(custom_templates)
        except Exception as e:
            print(f"Error loading templates: {e}")

    def save_templates(self) -> None:
        """Save custom alert templates."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.templates, f, indent=4)
        except Exception as e:
            print(f"Error saving templates: {e}")

    def get_template(self, name: str) -> Dict[str, Any]:
        """Get alert template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template dictionary
        """
        return self.templates.get(name, {})

    def add_template(self, name: str, template: Dict[str, Any]) -> None:
        """Add new alert template.
        
        Args:
            name: Template name
            template: Template dictionary
        """
        self.templates[name] = template
        self.save_templates()

    def remove_template(self, name: str) -> None:
        """Remove alert template.
        
        Args:
            name: Template name
        """
        if name in self.templates:
            del self.templates[name]
            self.save_templates()

    def format_alert(self, template_name: str, values: Dict[str, Any]) -> str:
        """Format alert message using template.
        
        Args:
            template_name: Template name
            values: Values for template
            
        Returns:
            Formatted alert message
        """
        template = self.get_template(template_name)
        if not template:
            return ""

        try:
            message = template['message'].format(**values)
            return f"[{template['level'].upper()}] {template['title']}: {message}"
        except Exception as e:
            print(f"Error formatting alert: {e}")
            return ""

