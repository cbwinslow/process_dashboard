"""
Configuration migration system for Process Dashboard.

Handles version control and updates for configuration files.
"""

from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import yaml
from datetime import datetime
import shutil

logger = logging.getLogger("dashboard.config.migrator")

class ConfigMigration:
    """Configuration migration handler."""

    CURRENT_VERSION = "1.0.0"

    def __init__(self, config_dir: Path):
        """Initialize migration handler.
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self.backup_dir = config_dir / "backups"
        self.migrations_dir = config_dir / "migrations"

    def check_version(self, config: Dict[str, Any]) -> Optional[str]:
        """Check configuration version.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Version string if update needed, None if current
        """
        current_version = config.get("version", "0.0.0")
        if current_version != self.CURRENT_VERSION:
            return current_version
        return None

    def backup_config(self, config_file: Path) -> Path:
        """Create backup of configuration file.
        
        Args:
            config_file: Configuration file path
            
        Returns:
            Backup file path
        """
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_{timestamp}.yaml"
            
            # Copy configuration
            shutil.copy2(config_file, backup_file)
            
            logger.info(f"Created configuration backup: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")
            raise

    def migrate_config(self, config: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Migrate configuration to current version.
        
        Args:
            config: Configuration dictionary
            from_version: Current version
            
        Returns:
            Updated configuration
        """
        try:
            # Load migration steps
            steps = self._load_migration_steps(from_version)
            
            # Apply migrations in order
            current_config = config.copy()
            for step in steps:
                current_config = step.apply(current_config)
                logger.info(f"Applied migration step: {step.version}")
            
            # Update version
            current_config["version"] = self.CURRENT_VERSION
            
            return current_config
            
        except Exception as e:
            logger.error(f"Failed to migrate configuration: {e}")
            raise

    def _load_migration_steps(self, from_version: str) -> List["MigrationStep"]:
        """Load required migration steps.
        
        Args:
            from_version: Starting version
            
        Returns:
            List of migration steps
        """
        steps = []
        
        # Add version-specific migrations
        if from_version < "0.5.0":
            steps.append(DisplayMigration())
        if from_version < "0.8.0":
            steps.append(ProcessMigration())
        if from_version < "1.0.0":
            steps.append(ResourceMigration())
            
        return sorted(steps, key=lambda x: x.version)

class MigrationStep:
    """Base class for migration steps."""
    
    version: str = ""

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration step.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration
        """
        raise NotImplementedError

class DisplayMigration(MigrationStep):
    """Migrate display configuration."""
    
    version = "0.5.0"

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply display configuration migration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration
        """
        display = config.get("display", {})
        
        # Update theme format
        if "theme" in display:
            theme = display["theme"]
            if isinstance(theme, str):
                # Convert old theme name to color scheme
                schemes = {
                    "dark": {
                        "background": "#001100",
                        "text": "#00FF00",
                        "accent": "#008800"
                    },
                    "light": {
                        "background": "#FFFFFF",
                        "text": "#000000",
                        "accent": "#008800"
                    }
                }
                display["theme"] = schemes.get(theme, schemes["dark"])
        
        # Update column configuration
        if "columns" in display:
            columns = display["columns"]
            if isinstance(columns, str):
                # Convert comma-separated string to list
                display["columns"] = [c.strip() for c in columns.split(",")]
        
        config["display"] = display
        return config

class ProcessMigration(MigrationStep):
    """Migrate process configuration."""
    
    version = "0.8.0"

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply process configuration migration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration
        """
        process = config.get("process", {})
        
        # Update threshold format
        for threshold_type in ["warning_thresholds", "critical_thresholds"]:
            if threshold_type in process:
                thresholds = process[threshold_type]
                if isinstance(thresholds, (int, float)):
                    # Convert single value to full threshold set
                    process[threshold_type] = {
                        "cpu_percent": float(thresholds),
                        "memory_percent": float(thresholds)
                    }
        
        # Update priority format
        if "priority" in process:
            priority = process["priority"]
            if isinstance(priority, int):
                # Convert numeric priority to named
                priority_map = {
                    -1: "low",
                    0: "normal",
                    1: "high"
                }
                process["default_priority"] = priority_map.get(priority, "normal")
                del process["priority"]
        
        config["process"] = process
        return config

class ResourceMigration(MigrationStep):
    """Migrate resource configuration."""
    
    version = "1.0.0"

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource configuration migration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration
        """
        resources = config.get("resources", {})
        
        # Update limits format
        if "limits" in resources:
            limits = resources["limits"]
            if isinstance(limits, dict):
                # Convert old limits format to new
                resources["default_limits"] = {
                    "memory_mb": limits.get("memory", 1024),
                    "cpu_percent": limits.get("cpu", 50)
                }
                del resources["limits"]
        
        # Update check interval
        if "interval" in resources:
            resources["check_interval"] = resources.pop("interval")
        
        config["resources"] = resources
        return config

def migrate_configuration(config_path: Path) -> None:
    """Migrate configuration file if needed.
    
    Args:
        config_path: Path to configuration file
    """
    try:
        # Load current configuration
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if not config:
            logger.warning("Empty configuration file")
            return
        
        # Check version
        migrator = ConfigMigration(config_path.parent)
        current_version = migrator.check_version(config)
        
        if current_version:
            logger.info(f"Configuration needs migration from version {current_version}")
            
            # Create backup
            migrator.backup_config(config_path)
            
            # Migrate configuration
            updated_config = migrator.migrate_config(config, current_version)
            
            # Save updated configuration
            with open(config_path, 'w') as f:
                yaml.safe_dump(updated_config, f, default_flow_style=False)
            
            logger.info("Configuration migration complete")
            
    except Exception as e:
        logger.error(f"Configuration migration failed: {e}")
        raise
