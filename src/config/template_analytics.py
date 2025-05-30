"""
Template analytics and usage tracking for Process Dashboard.

Provides insights into template usage and effectiveness.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
import sqlite3
from collections import defaultdict

logger = logging.getLogger("dashboard.config.analytics")

@dataclass
class TemplateUsage:
    """Template usage statistics."""
    template_id: str
    uses: int
    last_used: datetime
    avg_duration: float
    success_rate: float
    error_count: int
    user_ratings: List[int]
    performance_impact: Dict[str, float]

@dataclass
class TemplateEvent:
    """Template usage event."""
    template_id: str
    event_type: str
    timestamp: datetime
    duration: Optional[float] = None
    error: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    rating: Optional[int] = None

class TemplateAnalytics:
    """Template analytics system."""

    def __init__(self, data_dir: Path):
        """Initialize analytics system.
        
        Args:
            data_dir: Data directory path
        """
        self.data_dir = data_dir
        self.db_path = data_dir / "template_analytics.db"
        self.init_database()

    def init_database(self) -> None:
        """Initialize analytics database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS template_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    duration REAL,
                    error TEXT,
                    metrics TEXT,
                    rating INTEGER,
                    FOREIGN KEY (template_id) REFERENCES templates(id)
                )
                """)
                
                # Create summary table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS template_summary (
                    template_id TEXT PRIMARY KEY,
                    uses INTEGER DEFAULT 0,
                    last_used DATETIME,
                    avg_duration REAL DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    ratings TEXT,
                    performance TEXT
                )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def record_event(self, event: TemplateEvent) -> None:
        """Record template usage event.
        
        Args:
            event: Template event
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert event
                cursor.execute("""
                INSERT INTO template_events (
                    template_id, event_type, timestamp, duration,
                    error, metrics, rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.template_id,
                    event.event_type,
                    event.timestamp.isoformat(),
                    event.duration,
                    event.error,
                    json.dumps(event.metrics) if event.metrics else None,
                    event.rating
                ))
                
                # Update summary
                self._update_summary(cursor, event)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record event: {e}")

    def _update_summary(self, cursor: sqlite3.Cursor, event: TemplateEvent) -> None:
        """Update template summary statistics.
        
        Args:
            cursor: Database cursor
            event: Template event
        """
        try:
            # Get current summary
            cursor.execute("""
            SELECT uses, avg_duration, error_count, ratings, performance
            FROM template_summary
            WHERE template_id = ?
            """, (event.template_id,))
            
            row = cursor.fetchone()
            
            if row:
                uses, avg_duration, error_count, ratings_json, performance_json = row
                ratings = json.loads(ratings_json) if ratings_json else []
                performance = json.loads(performance_json) if performance_json else {}
                
                # Update statistics
                uses += 1
                if event.duration:
                    avg_duration = (avg_duration * (uses - 1) + event.duration) / uses
                if event.error:
                    error_count += 1
                if event.rating:
                    ratings.append(event.rating)
                if event.metrics:
                    for metric, value in event.metrics.items():
                        if metric in performance:
                            performance[metric] = (performance[metric] + value) / 2
                        else:
                            performance[metric] = value
                
                # Update summary
                cursor.execute("""
                UPDATE template_summary
                SET uses = ?, last_used = ?, avg_duration = ?,
                    error_count = ?, ratings = ?, performance = ?
                WHERE template_id = ?
                """, (
                    uses,
                    event.timestamp.isoformat(),
                    avg_duration,
                    error_count,
                    json.dumps(ratings),
                    json.dumps(performance),
                    event.template_id
                ))
                
            else:
                # Create new summary
                cursor.execute("""
                INSERT INTO template_summary (
                    template_id, uses, last_used, avg_duration,
                    error_count, ratings, performance
                ) VALUES (?, 1, ?, ?, ?, ?, ?)
                """, (
                    event.template_id,
                    event.timestamp.isoformat(),
                    event.duration or 0,
                    1 if event.error else 0,
                    json.dumps([event.rating] if event.rating else []),
                    json.dumps(event.metrics or {})
                ))
                
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")
            raise

    def get_template_usage(self, template_id: str) -> Optional[TemplateUsage]:
        """Get template usage statistics.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template usage statistics if found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT uses, last_used, avg_duration, success_rate,
                       error_count, ratings, performance
                FROM template_summary
                WHERE template_id = ?
                """, (template_id,))
                
                row = cursor.fetchone()
                
                if row:
                    (uses, last_used, avg_duration, success_rate,
                     error_count, ratings_json, performance_json) = row
                    
                    return TemplateUsage(
                        template_id=template_id,
                        uses=uses,
                        last_used=datetime.fromisoformat(last_used),
                        avg_duration=avg_duration,
                        success_rate=success_rate,
                        error_count=error_count,
                        user_ratings=json.loads(ratings_json),
                        performance_impact=json.loads(performance_json)
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get template usage: {e}")
            return None

    def get_usage_trends(
        self,
        template_id: str,
        days: int = 30
    ) -> Dict[str, List[float]]:
        """Get template usage trends.
        
        Args:
            template_id: Template identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary of trend data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                start_date = datetime.now() - timedelta(days=days)
                
                # Get daily statistics
                cursor.execute("""
                SELECT date(timestamp) as day,
                       count(*) as uses,
                       avg(duration) as avg_duration,
                       sum(case when error is not null then 1 else 0 end) as errors
                FROM template_events
                WHERE template_id = ? AND timestamp >= ?
                GROUP BY day
                ORDER BY day
                """, (template_id, start_date.isoformat()))
                
                trends = defaultdict(list)
                
                for row in cursor.fetchall():
                    day, uses, avg_duration, errors = row
                    trends["uses"].append(uses)
                    trends["duration"].append(avg_duration or 0)
                    trends["errors"].append(errors)
                
                return dict(trends)
                
        except Exception as e:
            logger.error(f"Failed to get usage trends: {e}")
            return {}

    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular templates.
        
        Args:
            limit: Maximum number of templates
            
        Returns:
            List of template statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT template_id, uses, last_used, avg_duration,
                       success_rate, error_count
                FROM template_summary
                ORDER BY uses DESC
                LIMIT ?
                """, (limit,))
                
                return [
                    {
                        "template_id": row[0],
                        "uses": row[1],
                        "last_used": datetime.fromisoformat(row[2]),
                        "avg_duration": row[3],
                        "success_rate": row[4],
                        "error_count": row[5]
                    }
                    for row in cursor.fetchall()
                ]
                
        except Exception as e:
            logger.error(f"Failed to get popular templates: {e}")
            return []

    def get_template_recommendations(
        self,
        performance_metrics: Dict[str, float]
    ) -> List[str]:
        """Get template recommendations based on performance needs.
        
        Args:
            performance_metrics: Desired performance metrics
            
        Returns:
            List of recommended template IDs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get templates with good performance matches
                cursor.execute("""
                SELECT template_id, performance
                FROM template_summary
                WHERE success_rate >= 0.8
                  AND uses >= 5
                """)
                
                matches = []
                
                for row in cursor.fetchall():
                    template_id, performance_json = row
                    performance = json.loads(performance_json)
                    
                    # Calculate match score
                    score = 0
                    for metric, desired in performance_metrics.items():
                        if metric in performance:
                            diff = abs(performance[metric] - desired)
                            score += 1 - (diff / max(desired, performance[metric]))
                    
                    if score > 0:
                        matches.append((template_id, score))
                
                # Sort by score
                matches.sort(key=lambda x: x[1], reverse=True)
                
                return [m[0] for m in matches[:10]]
                
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
