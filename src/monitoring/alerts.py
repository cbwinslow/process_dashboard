"""
Alert system for Process Dashboard.

Handles system alerts and notifications based on configured thresholds.
"""

import json
import logging
import smtplib
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger("dashboard.monitoring")

class AlertManager:
    """Manages system alerts and notifications."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize alert manager.
        
        Args:
            config_path: Path to alert configuration file
        """
        self.config_path = config_path or Path.home() / ".config" / "process-dashboard" / "monitoring" / "alerts.json"
        self.load_config()

    def load_config(self) -> None:
        """Load alert configuration."""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Alert config not found at {self.config_path}, using defaults")
            self.config = {
                "cpu_threshold": 80,
                "memory_threshold": 80,
                "disk_threshold": 90,
                "log_size_threshold_mb": 100,
                "alert_email": "",
                "notification_level": "warning",
                "desktop_notifications": True
            }
            self.save_config()

    def save_config(self) -> None:
        """Save alert configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """Check system metrics against thresholds.
        
        Args:
            metrics: System metrics to check
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Check CPU usage
        if metrics.get('cpu_percent', 0) > self.config['cpu_threshold']:
            alerts.append(f"CPU usage above threshold: {metrics['cpu_percent']}%")
        
        # Check memory usage
        if metrics.get('memory_percent', 0) > self.config['memory_threshold']:
            alerts.append(f"Memory usage above threshold: {metrics['memory_percent']}%")
        
        # Check disk usage
        if metrics.get('disk_percent', 0) > self.config['disk_threshold']:
            alerts.append(f"Disk usage above threshold: {metrics['disk_percent']}%")
        
        return alerts

    def send_alert(self, message: str, level: str = "warning") -> None:
        """Send alert notification.
        
        Args:
            message: Alert message
            level: Alert level (info, warning, error)
        """
        # Log alert
        logger.warning(f"Alert: {message}")
        
        # Send email if configured
        if self.config['alert_email']:
            self._send_email(message, level)
        
        # Send desktop notification if enabled
        if self.config['desktop_notifications']:
            self._send_desktop_notification(message, level)

    def _send_email(self, message: str, level: str) -> None:
        """Send alert email.
        
        Args:
            message: Alert message
            level: Alert level
        """
        try:
            if not self.config['alert_email']:
                return

            msg = MIMEText(f"""
Process Dashboard Alert

Level: {level.upper()}
Time: {datetime.now()}
Message: {message}
            """)
            
            msg['Subject'] = f"Process Dashboard Alert: {level.upper()}"
            msg['From'] = "process-dashboard@localhost"
            msg['To'] = self.config['alert_email']
            
            # Use local sendmail
            with subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE) as p:
                p.communicate(msg.as_bytes())
                
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    def _send_desktop_notification(self, message: str, level: str) -> None:
        """Send desktop notification.
        
        Args:
            message: Alert message
            level: Alert level
        """
        try:
            # Try using notify-send
            subprocess.run([
                "notify-send",
                f"Process Dashboard {level.upper()}",
                message,
                "--urgency=critical" if level == "error" else "--urgency=normal"
            ])
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")

    def check_log_size(self, log_path: Path) -> None:
        """Check log file size and rotate if needed.
        
        Args:
            log_path: Path to log file
        """
        try:
            if not log_path.exists():
                return
                
            size_mb = log_path.stat().st_size / (1024 * 1024)
            if size_mb > self.config['log_size_threshold_mb']:
                self.send_alert(
                    f"Log file {log_path} exceeds size threshold ({size_mb:.1f}MB)",
                    "warning"
                )
                
        except Exception as e:
            logger.error(f"Failed to check log size: {e}")
