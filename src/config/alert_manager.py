"""
Alert management for Process Dashboard analytics.

Provides metric monitoring and alert generation for template analytics.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum
import json
from pathlib import Path
import sqlite3

logger = logging.getLogger("dashboard.config.alerts")

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status types."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    description: str
    metric: str
    condition: str
    threshold: float
    severity: AlertSeverity
    cooldown: int = 300  # seconds
    enabled: bool = True

@dataclass
class Alert:
    """Alert instance."""
    rule_name: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    value: float
    threshold: float
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class AlertManager:
    """Alert management system."""

    def __init__(self, data_dir: Path):
        """Initialize alert manager.
        
        Args:
            data_dir: Data directory path
        """
        self.data_dir = data_dir
        self.db_path = data_dir / "alerts.db"
        self.rules: Dict[str, AlertRule] = {}
        self.init_database()
        self.load_rules()

    def init_database(self) -> None:
        """Initialize alert database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create rules table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_rules (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    metric TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    severity TEXT NOT NULL,
                    cooldown INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL
                )
                """)
                
                # Create alerts table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    acknowledged_by TEXT,
                    resolved_at DATETIME,
                    FOREIGN KEY (rule_name) REFERENCES alert_rules(name)
                )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize alert database: {e}")
            raise

    def load_rules(self) -> None:
        """Load alert rules from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM alert_rules")
                for row in cursor.fetchall():
                    (name, description, metric, condition,
                     threshold, severity, cooldown, enabled) = row
                    
                    self.rules[name] = AlertRule(
                        name=name,
                        description=description,
                        metric=metric,
                        condition=condition,
                        threshold=threshold,
                        severity=AlertSeverity(severity),
                        cooldown=cooldown,
                        enabled=bool(enabled)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to load alert rules: {e}")

    def add_rule(self, rule: AlertRule) -> bool:
        """Add new alert rule.
        
        Args:
            rule: Alert rule
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO alert_rules (
                    name, description, metric, condition,
                    threshold, severity, cooldown, enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule.name,
                    rule.description,
                    rule.metric,
                    rule.condition,
                    rule.threshold,
                    rule.severity.value,
                    rule.cooldown,
                    rule.enabled
                ))
                
                conn.commit()
                
            self.rules[rule.name] = rule
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert rule: {e}")
            return False

    def update_rule(self, rule: AlertRule) -> bool:
        """Update alert rule.
        
        Args:
            rule: Alert rule
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE alert_rules
                SET description = ?, metric = ?, condition = ?,
                    threshold = ?, severity = ?, cooldown = ?,
                    enabled = ?
                WHERE name = ?
                """, (
                    rule.description,
                    rule.metric,
                    rule.condition,
                    rule.threshold,
                    rule.severity.value,
                    rule.cooldown,
                    rule.enabled,
                    rule.name
                ))
                
                conn.commit()
                
            self.rules[rule.name] = rule
            return True
            
        except Exception as e:
            logger.error(f"Failed to update alert rule: {e}")
            return False

    def delete_rule(self, rule_name: str) -> bool:
        """Delete alert rule.
        
        Args:
            rule_name: Rule name
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM alert_rules WHERE name = ?",
                    (rule_name,)
                )
                
                conn.commit()
                
            if rule_name in self.rules:
                del self.rules[rule_name]
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete alert rule: {e}")
            return False

    def check_metrics(self, metrics: Dict[str, float]) -> List[Alert]:
        """Check metrics against alert rules.
        
        Args:
            metrics: Current metric values
            
        Returns:
            List of triggered alerts
        """
        alerts = []
        
        try:
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                if rule.metric not in metrics:
                    continue
                
                value = metrics[rule.metric]
                triggered = self._evaluate_condition(
                    value,
                    rule.condition,
                    rule.threshold
                )
                
                if triggered:
                    # Check cooldown
                    if not self._check_cooldown(rule.name):
                        continue
                    
                    # Create alert
                    alert = Alert(
                        rule_name=rule.name,
                        message=self._format_alert_message(rule, value),
                        severity=rule.severity,
                        status=AlertStatus.ACTIVE,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        value=value,
                        threshold=rule.threshold
                    )
                    
                    self._save_alert(alert)
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to check metrics: {e}")
            return alerts

    def _evaluate_condition(
        self,
        value: float,
        condition: str,
        threshold: float
    ) -> bool:
        """Evaluate alert condition.
        
        Args:
            value: Current value
            condition: Condition operator
            threshold: Threshold value
            
        Returns:
            True if condition is met
        """
        try:
            if condition == ">":
                return value > threshold
            elif condition == ">=":
                return value >= threshold
            elif condition == "<":
                return value < threshold
            elif condition == "<=":
                return value <= threshold
            elif condition == "=":
                return abs(value - threshold) < 0.0001
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to evaluate condition: {e}")
            return False

    def _check_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown.
        
        Args:
            rule_name: Rule name
            
        Returns:
            True if rule can trigger
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get last alert
                cursor.execute("""
                SELECT created_at, status
                FROM alerts
                WHERE rule_name = ?
                ORDER BY created_at DESC
                LIMIT 1
                """, (rule_name,))
                
                row = cursor.fetchone()
                if not row:
                    return True
                
                last_time = datetime.fromisoformat(row[0])
                status = AlertStatus(row[1])
                
                # Check if resolved
                if status == AlertStatus.RESOLVED:
                    return True
                
                # Check cooldown
                rule = self.rules[rule_name]
                cooldown = timedelta(seconds=rule.cooldown)
                
                return datetime.now() - last_time > cooldown
                
        except Exception as e:
            logger.error(f"Failed to check cooldown: {e}")
            return True

    def _format_alert_message(self, rule: AlertRule, value: float) -> str:
        """Format alert message.
        
        Args:
            rule: Alert rule
            value: Current value
            
        Returns:
            Formatted message
        """
        return (
            f"{rule.description}\n"
            f"Metric: {rule.metric}\n"
            f"Value: {value:.2f} {rule.condition} {rule.threshold:.2f}"
        )

    def _save_alert(self, alert: Alert) -> None:
        """Save alert to database.
        
        Args:
            alert: Alert instance
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO alerts (
                    rule_name, message, severity, status,
                    created_at, updated_at, value, threshold,
                    acknowledged_by, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.rule_name,
                    alert.message,
                    alert.severity.value,
                    alert.status.value,
                    alert.created_at.isoformat(),
                    alert.updated_at.isoformat(),
                    alert.value,
                    alert.threshold,
                    alert.acknowledged_by,
                    alert.resolved_at.isoformat() if alert.resolved_at else None
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")

    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts.
        
        Returns:
            List of active alerts
        """
        alerts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM alerts
                WHERE status = ?
                ORDER BY created_at DESC
                """, (AlertStatus.ACTIVE.value,))
                
                for row in cursor.fetchall():
                    (_, rule_name, message, severity, status,
                     created_at, updated_at, value, threshold,
                     acknowledged_by, resolved_at) = row
                    
                    alerts.append(Alert(
                        rule_name=rule_name,
                        message=message,
                        severity=AlertSeverity(severity),
                        status=AlertStatus(status),
                        created_at=datetime.fromisoformat(created_at),
                        updated_at=datetime.fromisoformat(updated_at),
                        value=value,
                        threshold=threshold,
                        acknowledged_by=acknowledged_by,
                        resolved_at=datetime.fromisoformat(resolved_at)
                        if resolved_at else None
                    ))
                
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return alerts

    def acknowledge_alert(
        self,
        alert_id: int,
        user: str
    ) -> bool:
        """Acknowledge alert.
        
        Args:
            alert_id: Alert ID
            user: User acknowledging alert
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE alerts
                SET status = ?, acknowledged_by = ?, updated_at = ?
                WHERE id = ?
                """, (
                    AlertStatus.ACKNOWLEDGED.value,
                    user,
                    datetime.now().isoformat(),
                    alert_id
                ))
                
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE alerts
                SET status = ?, resolved_at = ?, updated_at = ?
                WHERE id = ?
                """, (
                    AlertStatus.RESOLVED.value,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    alert_id
                ))
                
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
