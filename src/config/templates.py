"""
Configuration templates for Process Dashboard.

Provides predefined configuration templates and import/export functionality.
"""

from typing import Dict, Any, Optional, List
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
import shutil

logger = logging.getLogger("dashboard.config.templates")

# Default configuration templates
TEMPLATES = {
    "minimal": {
        "name": "Minimal Configuration",
        "description": "Basic setup with essential features only",
        "config": {
            "version": "1.0.0",
            "display": {
                "refresh_rate": 2,
                "theme": {
                    "background": "#001100",
                    "text": "#00FF00",
                    "accent": "#008800",
                    "error": "#FF0000",
                    "warning": "#FFFF00",
                    "success": "#00FF00"
                },
                "columns": ["pid", "name", "cpu_percent", "memory_percent", "status"]
            },
            "process": {
                "default_priority": "normal",
                "auto_cleanup": True,
                "history_size": 100,
                "warning_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 80
                },
                "critical_thresholds": {
                    "cpu_percent": 95,
                    "memory_percent": 95
                }
            },
            "resources": {
                "enable_limits": True,
                "default_limits": {
                    "memory_mb": 1024,
                    "cpu_percent": 50
                },
                "check_interval": 5
            },
            "snmp": {
                "enabled": False
            },
            "logging": {
                "level": "INFO",
                "file": "dashboard.log"
            }
        }
    },
    "development": {
        "name": "Development Environment",
        "description": "Optimized for software development with detailed monitoring",
        "config": {
            "version": "1.0.0",
            "display": {
                "refresh_rate": 1,
                "theme": {
                    "background": "#002200",
                    "text": "#00FF00",
                    "accent": "#00AA00",
                    "error": "#FF0000",
                    "warning": "#FFFF00",
                    "success": "#00FF00"
                },
                "columns": [
                    "pid", "name", "cpu_percent", "memory_percent",
                    "status", "user", "priority", "group"
                ]
            },
            "process": {
                "default_priority": "normal",
                "auto_cleanup": True,
                "history_size": 1000,
                "warning_thresholds": {
                    "cpu_percent": 70,
                    "memory_percent": 70
                },
                "critical_thresholds": {
                    "cpu_percent": 90,
                    "memory_percent": 90
                }
            },
            "resources": {
                "enable_limits": True,
                "default_limits": {
                    "memory_mb": 2048,
                    "cpu_percent": 75
                },
                "check_interval": 2
            },
            "snmp": {
                "enabled": False
            },
            "groups": {
                "development": {
                    "color": "#00FF00",
                    "priority": "high"
                },
                "testing": {
                    "color": "#FFFF00",
                    "priority": "normal"
                },
                "background": {
                    "color": "#888888",
                    "priority": "low"
                }
            },
            "logging": {
                "level": "DEBUG",
                "file": "dashboard.log",
                "max_size": "50MB",
                "backup_count": 5
            }
        }
    },
    "server_monitoring": {
        "name": "Server Monitoring",
        "description": "Focused on system monitoring with SNMP support",
        "config": {
            "version": "1.0.0",
            "display": {
                "refresh_rate": 5,
                "theme": {
                    "background": "#000033",
                    "text": "#FFFFFF",
                    "accent": "#0088FF",
                    "error": "#FF0000",
                    "warning": "#FFFF00",
                    "success": "#00FF00"
                },
                "columns": [
                    "pid", "name", "cpu_percent", "memory_percent",
                    "status", "user", "priority", "group"
                ]
            },
            "process": {
                "default_priority": "normal",
                "auto_cleanup": True,
                "history_size": 10000,
                "warning_thresholds": {
                    "cpu_percent": 85,
                    "memory_percent": 85
                },
                "critical_thresholds": {
                    "cpu_percent": 95,
                    "memory_percent": 95
                }
            },
            "resources": {
                "enable_limits": True,
                "default_limits": {
                    "memory_mb": 4096,
                    "cpu_percent": 90
                },
                "check_interval": 10
            },
            "snmp": {
                "enabled": True,
                "default_port": 161,
                "community": "public",
                "metrics": [
                    "cpu_load",
                    "memory_usage",
                    "disk_io",
                    "network_io"
                ],
                "collection_interval": 30
            },
            "groups": {
                "system": {
                    "color": "#0088FF",
                    "priority": "high"
                },
                "services": {
                    "color": "#00FF00",
                    "priority": "high"
                },
                "background": {
                    "color": "#888888",
                    "priority": "low"
                }
            },
            "logging": {
                "level": "INFO",
                "file": "dashboard.log",
                "max_size": "100MB",
                "backup_count": 10,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }
}

class ConfigurationTemplate:
    """Configuration template manager."""

    def __init__(self, config_dir: Path):
        """Initialize template manager.
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self.templates_dir = config_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def get_template_list(self) -> List[Dict[str, str]]:
        """Get list of available templates.
        
        Returns:
            List of template information
        """
        templates = []
        
        # Add built-in templates
        for template_id, template in TEMPLATES.items():
            templates.append({
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "built_in": True
            })
        
        # Add custom templates
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file) as f:
                    template = yaml.safe_load(f)
                templates.append({
                    "id": template_file.stem,
                    "name": template.get("name", template_file.stem),
                    "description": template.get("description", "Custom template"),
                    "built_in": False
                })
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
        
        return templates

    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load template configuration.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template configuration if found
        """
        try:
            # Check built-in templates
            if template_id in TEMPLATES:
                return TEMPLATES[template_id]["config"]
            
            # Check custom templates
            template_file = self.templates_dir / f"{template_id}.yaml"
            if template_file.exists():
                with open(template_file) as f:
                    template = yaml.safe_load(f)
                return template.get("config")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None

    def save_template(
        self,
        name: str,
        config: Dict[str, Any],
        description: str = ""
    ) -> bool:
        """Save configuration as template.
        
        Args:
            name: Template name
            config: Configuration dictionary
            description: Optional template description
            
        Returns:
            True if successful
        """
        try:
            # Create template data
            template = {
                "name": name,
                "description": description,
                "created": datetime.now().isoformat(),
                "config": config
            }
            
            # Generate safe filename
            template_id = name.lower().replace(" ", "_")
            template_file = self.templates_dir / f"{template_id}.yaml"
            
            # Save template
            with open(template_file, 'w') as f:
                yaml.safe_dump(template, f, default_flow_style=False)
            
            logger.info(f"Saved template: {template_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """Delete custom template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if successful
        """
        try:
            # Cannot delete built-in templates
            if template_id in TEMPLATES:
                return False
            
            # Delete custom template
            template_file = self.templates_dir / f"{template_id}.yaml"
            if template_file.exists():
                template_file.unlink()
                logger.info(f"Deleted template: {template_file}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False

    def export_config(
        self,
        config: Dict[str, Any],
        export_file: Path,
        format: str = "yaml"
    ) -> bool:
        """Export configuration to file.
        
        Args:
            config: Configuration dictionary
            export_file: Export file path
            format: Export format (yaml or json)
            
        Returns:
            True if successful
        """
        try:
            # Add export metadata
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "format_version": "1.0.0",
                "config": config
            }
            
            # Export in requested format
            if format.lower() == "json":
                with open(export_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
            else:
                with open(export_file, 'w') as f:
                    yaml.safe_dump(export_data, f, default_flow_style=False)
            
            logger.info(f"Exported configuration to: {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False

    def import_config(self, import_file: Path) -> Optional[Dict[str, Any]]:
        """Import configuration from file.
        
        Args:
            import_file: Import file path
            
        Returns:
            Imported configuration if successful
        """
        try:
            # Determine format from extension
            if import_file.suffix.lower() == ".json":
                with open(import_file) as f:
                    import_data = json.load(f)
            else:
                with open(import_file) as f:
                    import_data = yaml.safe_load(f)
            
            # Validate import data
            if not isinstance(import_data, dict):
                raise ValueError("Invalid import data format")
            
            config = import_data.get("config")
            if not config:
                raise ValueError("No configuration found in import file")
            
            logger.info(f"Imported configuration from: {import_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return None
