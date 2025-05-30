"""
Notification delivery system for Process Dashboard alerts.

Provides multi-channel notification delivery and alert correlation.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
import sqlite3
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import platform
import queue
import threading
import re

from .alert_manager import Alert, AlertSeverity

logger = logging.getLogger("dashboard.config.notifications")

@dataclass
class NotificationChannel:
    """Notification channel configuration."""
    name: str
    type: str
    config: Dict[str, Any]
    enabled: bool = True
    severity_filter: Set[AlertSeverity] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.severity_filter is None:
            self.severity_filter = set(AlertSeverity)

@dataclass
class NotificationTemplate:
    """Notification message template."""
    name: str
    subject: str
    body: str
    format: str = "text"  # text, html, markdown

class AlertPattern:
    """Alert correlation pattern."""
    def __init__(
        self,
        name: str,
        pattern: str,
        window: int,
        min_occurrences: int,
        metrics: List[str]
    ):
        """Initialize pattern.
        
        Args:
            name: Pattern name
            pattern: Regex pattern
            window: Time window in seconds
            min_occurrences: Minimum occurrences to match
            metrics: Related metrics
        """
        self.name = name
        self.pattern = re.compile(pattern)
        self.window = window
        self.min_occurrences = min_occurrences
        self.metrics = metrics
        self.matches: List[datetime] = []

    def match(self, alert: Alert) -> bool:
        """Check if alert matches pattern.
        
        Args:
            alert: Alert to check
            
        Returns:
            True if matches
        """
        # Remove old matches
        cutoff = datetime.now() - timedelta(seconds=self.window)
        self.matches = [m for m in self.matches if m > cutoff]
        
        # Check for match
        if self.pattern.search(alert.message):
            self.matches.append(alert.created_at)
            return len(self.matches) >= self.min_occurrences
        
        return False

class NotificationManager:
    """Notification management system."""

    def __init__(self, data_dir: Path):
        """Initialize notification manager.
        
        Args:
            data_dir: Data directory path
        """
        self.data_dir = data_dir
        self.db_path = data_dir / "notifications.db"
        self.channels: Dict[str, NotificationChannel] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.patterns: List[AlertPattern] = []
        self.notification_queue = queue.Queue()
        self.init_database()
        self.load_config()
        self._start_notification_worker()

    def init_database(self) -> None:
        """Initialize notification database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create notifications table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sent_at DATETIME,
                    error TEXT,
                    FOREIGN KEY (alert_id) REFERENCES alerts(id)
                )
                """)
                
                # Create correlation table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT NOT NULL,
                    first_alert_id INTEGER NOT NULL,
                    last_alert_id INTEGER NOT NULL,
                    count INTEGER NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (first_alert_id) REFERENCES alerts(id),
                    FOREIGN KEY (last_alert_id) REFERENCES alerts(id)
                )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def load_config(self) -> None:
        """Load notification configuration."""
        try:
            config_file = self.data_dir / "notification_config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                
                # Load channels
                for channel_config in config.get("channels", []):
                    self.channels[channel_config["name"]] = NotificationChannel(
                        name=channel_config["name"],
                        type=channel_config["type"],
                        config=channel_config.get("config", {}),
                        enabled=channel_config.get("enabled", True),
                        severity_filter=set(
                            AlertSeverity(s) for s in channel_config.get(
                                "severity_filter",
                                [s.value for s in AlertSeverity]
                            )
                        )
                    )
                
                # Load templates
                for template_config in config.get("templates", []):
                    self.templates[template_config["name"]] = NotificationTemplate(
                        name=template_config["name"],
                        subject=template_config["subject"],
                        body=template_config["body"],
                        format=template_config.get("format", "text")
                    )
                
                # Load patterns
                for pattern_config in config.get("patterns", []):
                    self.patterns.append(AlertPattern(
                        name=pattern_config["name"],
                        pattern=pattern_config["pattern"],
                        window=pattern_config["window"],
                        min_occurrences=pattern_config["min_occurrences"],
                        metrics=pattern_config.get("metrics", [])
                    ))
                
        except Exception as e:
            logger.error(f"Failed to load notification config: {e}")

    def _start_notification_worker(self) -> None:
        """Start notification delivery worker thread."""
        def worker():
            while True:
                try:
                    notification = self.notification_queue.get()
                    if notification is None:
                        break
                    
                    alert_id, channel = notification
                    self._deliver_notification(alert_id, channel)
                    self.notification_queue.task_done()
                    
                except Exception as e:
                    logger.error(f"Notification worker error: {e}")
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def process_alert(self, alert: Alert) -> None:
        """Process alert for notification.
        
        Args:
            alert: Alert to process
        """
        try:
            # Check correlation patterns
            self._check_patterns(alert)
            
            # Queue notifications
            for channel in self.channels.values():
                if not channel.enabled:
                    continue
                
                if alert.severity not in channel.severity_filter:
                    continue
                
                self.notification_queue.put((alert.id, channel))
                
        except Exception as e:
            logger.error(f"Failed to process alert: {e}")

    def _check_patterns(self, alert: Alert) -> None:
        """Check alert against correlation patterns.
        
        Args:
            alert: Alert to check
        """
        try:
            for pattern in self.patterns:
                if pattern.match(alert):
                    self._record_correlation(pattern, alert)
                    
        except Exception as e:
            logger.error(f"Failed to check patterns: {e}")

    def _record_correlation(self, pattern: AlertPattern, alert: Alert) -> None:
        """Record alert correlation.
        
        Args:
            pattern: Matching pattern
            alert: Triggering alert
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO correlations (
                    pattern_name, first_alert_id, last_alert_id,
                    count, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    pattern.name,
                    pattern.matches[0].id,
                    alert.id,
                    len(pattern.matches),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record correlation: {e}")

    def _deliver_notification(
        self,
        alert_id: int,
        channel: NotificationChannel
    ) -> None:
        """Deliver notification through channel.
        
        Args:
            alert_id: Alert ID
            channel: Notification channel
        """
        try:
            # Get alert details
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM alerts WHERE id = ?",
                    (alert_id,)
                )
                alert_data = cursor.fetchone()
            
            if not alert_data:
                raise ValueError(f"Alert {alert_id} not found")
            
            # Format notification
            template = self._get_template(channel)
            message = self._format_message(template, alert_data)
            
            # Send notification
            if channel.type == "email":
                self._send_email(channel, message)
            elif channel.type == "system":
                self._send_system_notification(message)
            elif channel.type == "terminal":
                self._send_terminal_notification(message)
            
            # Record success
            self._record_notification(
                alert_id,
                channel.name,
                "sent"
            )
            
        except Exception as e:
            logger.error(f"Failed to deliver notification: {e}")
            self._record_notification(
                alert_id,
                channel.name,
                "error",
                str(e)
            )

    def _get_template(
        self,
        channel: NotificationChannel
    ) -> NotificationTemplate:
        """Get notification template for channel.
        
        Args:
            channel: Notification channel
            
        Returns:
            Notification template
        """
        template_name = channel.config.get("template")
        if template_name and template_name in self.templates:
            return self.templates[template_name]
        
        # Use default template
        return NotificationTemplate(
            name="default",
            subject="Process Dashboard Alert",
            body="${severity} Alert: ${message}"
        )

    def _format_message(
        self,
        template: NotificationTemplate,
        alert_data: tuple
    ) -> Dict[str, str]:
        """Format notification message.
        
        Args:
            template: Message template
            alert_data: Alert data tuple
            
        Returns:
            Formatted message
        """
        # Extract alert fields
        (alert_id, rule_name, message, severity,
         status, created_at, _, value, threshold, _, _) = alert_data
        
        # Format subject
        subject = template.subject.replace("${severity}", severity)
        subject = subject.replace("${rule_name}", rule_name)
        
        # Format body
        body = template.body.replace("${severity}", severity)
        body = body.replace("${message}", message)
        body = body.replace("${rule_name}", rule_name)
        body = body.replace("${created_at}", created_at)
        body = body.replace("${value}", str(value))
        body = body.replace("${threshold}", str(threshold))
        
        return {
            "subject": subject,
            "body": body,
            "format": template.format
        }

    def _send_email(
        self,
        channel: NotificationChannel,
        message: Dict[str, str]
    ) -> None:
        """Send email notification.
        
        Args:
            channel: Email channel
            message: Formatted message
        """
        try:
            config = channel.config
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message["subject"]
            msg["From"] = config["from_address"]
            msg["To"] = config["to_address"]
            
            # Add body
            if message["format"] == "html":
                msg.attach(MIMEText(message["body"], "html"))
            else:
                msg.attach(MIMEText(message["body"], "plain"))
            
            # Send email
            with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
                if config.get("use_tls"):
                    server.starttls()
                if config.get("username"):
                    server.login(config["username"], config["password"])
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")

    def _send_system_notification(self, message: Dict[str, str]) -> None:
        """Send system notification.
        
        Args:
            message: Formatted message
        """
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run([
                    "osascript",
                    "-e", f'display notification "{message["body"]}" with title "{message["subject"]}"'
                ])
            elif platform.system() == "Linux":
                subprocess.run([
                    "notify-send",
                    message["subject"],
                    message["body"]
                ])
            elif platform.system() == "Windows":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    message["subject"],
                    message["body"],
                    duration=5
                )
                
        except Exception as e:
            raise Exception(f"Failed to send system notification: {e}")

    def _send_terminal_notification(self, message: Dict[str, str]) -> None:
        """Send terminal notification.
        
        Args:
            message: Formatted message
        """
        try:
            # Print to terminal
            print(f"\n{message['subject']}")
            print("-" * len(message['subject']))
            print(message['body'])
            print()
            
        except Exception as e:
            raise Exception(f"Failed to send terminal notification: {e}")

    def _record_notification(
        self,
        alert_id: int,
        channel: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """Record notification status.
        
        Args:
            alert_id: Alert ID
            channel: Channel name
            status: Notification status
            error: Optional error message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO notifications (
                    alert_id, channel, status, sent_at, error
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    alert_id,
                    channel,
                    status,
                    datetime.now().isoformat() if status == "sent" else None,
                    error
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record notification: {e}")

    def get_notification_status(
        self,
        alert_id: int
    ) -> List[Dict[str, Any]]:
        """Get notification status for alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            List of notification status records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT channel, status, sent_at, error
                FROM notifications
                WHERE alert_id = ?
                ORDER BY sent_at DESC
                """, (alert_id,))
                
                return [
                    {
                        "channel": row[0],
                        "status": row[1],
                        "sent_at": datetime.fromisoformat(row[2])
                        if row[2] else None,
                        "error": row[3]
                    }
                    for row in cursor.fetchall()
                ]
                
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            return []

    def get_correlations(
        self,
        since: datetime,
        pattern_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get alert correlations.
        
        Args:
            since: Start time
            pattern_name: Optional pattern filter
            
        Returns:
            List of correlations
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT pattern_name, first_alert_id, last_alert_id,
                       count, created_at
                FROM correlations
                WHERE created_at >= ?
                """
                params = [since.isoformat()]
                
                if pattern_name:
                    query += " AND pattern_name = ?"
                    params.append(pattern_name)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                
                return [
                    {
                        "pattern": row[0],
                        "first_alert": row[1],
                        "last_alert": row[2],
                        "count": row[3],
                        "created_at": datetime.fromisoformat(row[4])
                    }
                    for row in cursor.fetchall()
                ]
                
        except Exception as e:
            logger.error(f"Failed to get correlations: {e}")
            return []
