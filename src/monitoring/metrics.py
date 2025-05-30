"""
System metrics collection for Process Dashboard.

Collects and tracks system performance metrics.
"""

import psutil
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("dashboard.monitoring")

class MetricsCollector:
    """Collects and tracks system metrics."""

    def __init__(self, history_length: int = 3600):
        """Initialize metrics collector.
        
        Args:
            history_length: Length of history to maintain (seconds)
        """
        self.history_length = history_length
        self.metrics_history: Dict[str, list] = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network': []
        }

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics.
        
        Returns:
            Dictionary of system metrics
        """
        try:
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'swap_percent': psutil.swap_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_avg': psutil.getloadavg(),
                'process_count': len(psutil.pids()),
                'network': self._get_network_stats()
            }
            
            # Update history
            self._update_history(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}

    def _get_network_stats(self) -> Dict[str, int]:
        """Get network statistics.
        
        Returns:
            Dictionary of network statistics
        """
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errors_in': net.errin,
            'errors_out': net.errout,
            'drops_in': net.dropin,
            'drops_out': net.dropout
        }

    def _update_history(self, metrics: Dict[str, Any]) -> None:
        """Update metrics history.
        
        Args:
            metrics: Current metrics
        """
        timestamp = metrics['timestamp']
        
        # Update CPU history
        self.metrics_history['cpu'].append({
            'timestamp': timestamp,
            'value': metrics['cpu_percent']
        })
        
        # Update memory history
        self.metrics_history['memory'].append({
            'timestamp': timestamp,
            'value': metrics['memory_percent']
        })
        
        # Update disk history
        self.metrics_history['disk'].append({
            'timestamp': timestamp,
            'value': metrics['disk_percent']
        })
        
        # Update network history
        self.metrics_history['network'].append({
            'timestamp': timestamp,
            'sent': metrics['network']['bytes_sent'],
            'received': metrics['network']['bytes_recv']
        })
        
        # Trim old entries
        self._trim_history()

    def _trim_history(self) -> None:
        """Remove old entries from history."""
        cutoff = datetime.now().timestamp() - self.history_length
        
        for metric_type in self.metrics_history:
            self.metrics_history[metric_type] = [
                entry for entry in self.metrics_history[metric_type]
                if entry['timestamp'].timestamp() > cutoff
            ]

    def get_history(self, metric_type: str) -> list:
        """Get history for specific metric.
        
        Args:
            metric_type: Type of metric (cpu, memory, disk, network)
            
        Returns:
            List of historical values
        """
        return self.metrics_history.get(metric_type, [])

    def export_metrics(self, export_path: Path) -> None:
        """Export metrics history to file.
        
        Args:
            export_path: Path to export file
        """
        try:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert datetime objects to timestamps
            export_data = {}
            for metric_type, history in self.metrics_history.items():
                export_data[metric_type] = [
                    {**entry, 'timestamp': entry['timestamp'].timestamp()}
                    for entry in history
                ]
            
            import json
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
