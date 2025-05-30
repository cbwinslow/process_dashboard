"""
Visualization tools for Process Dashboard metrics.

Provides ASCII-based charts and visualizations for terminal display.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics
import logging

logger = logging.getLogger("dashboard.monitoring.visualization")

class ASCIIChart:
    """ASCII-based chart generator."""

    def __init__(self, width: int = 80, height: int = 20):
        """Initialize chart.
        
        Args:
            width: Chart width in characters
            height: Chart height in characters
        """
        self.width = width
        self.height = height

    def create_line_chart(self, data: List[float], title: str = "") -> str:
        """Create ASCII line chart.
        
        Args:
            data: List of values to plot
            title: Chart title
            
        Returns:
            ASCII chart string
        """
        if not data:
            return "No data to display"

        try:
            # Calculate min/max
            min_val = min(data)
            max_val = max(data)
            range_val = max_val - min_val or 1

            # Create empty chart
            chart = [[" " for _ in range(self.width)] for _ in range(self.height)]

            # Plot data points
            for i, value in enumerate(data[-self.width:]):
                # Calculate y position
                y = int((value - min_val) / range_val * (self.height - 1))
                y = min(max(y, 0), self.height - 1)
                
                # Plot point
                chart[self.height - 1 - y][i] = "●"

            # Add axes
            for i in range(self.height):
                chart[i][0] = "│"
            for i in range(self.width):
                chart[self.height - 1][i] = "─"

            # Add labels
            result = [title.center(self.width)] if title else []
            result.extend([
                "".join(row) for row in chart
            ])
            result.append(f"Min: {min_val:.1f} Max: {max_val:.1f}")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            return "Error creating chart"

    def create_bar_chart(self, data: Dict[str, float], title: str = "") -> str:
        """Create ASCII bar chart.
        
        Args:
            data: Dictionary of labels and values
            title: Chart title
            
        Returns:
            ASCII chart string
        """
        if not data:
            return "No data to display"

        try:
            # Calculate max value and bar width
            max_val = max(data.values())
            label_width = max(len(label) for label in data.keys())
            bar_width = self.width - label_width - 5

            # Create chart
            result = [title.center(self.width)] if title else []
            
            for label, value in data.items():
                # Calculate bar length
                bar_len = int((value / max_val) * bar_width)
                bar = "█" * bar_len
                
                # Format line
                line = f"{label.ljust(label_width)} │{bar} {value:.1f}"
                result.append(line)

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return "Error creating chart"

    def create_histogram(self, data: List[float], bins: int = 10, title: str = "") -> str:
        """Create ASCII histogram.
        
        Args:
            data: List of values
            bins: Number of bins
            title: Chart title
            
        Returns:
            ASCII histogram string
        """
        if not data:
            return "No data to display"

        try:
            # Calculate bins
            min_val = min(data)
            max_val = max(data)
            bin_size = (max_val - min_val) / bins
            
            # Count values in bins
            bin_counts = [0] * bins
            for value in data:
                bin_idx = min(int((value - min_val) / bin_size), bins - 1)
                bin_counts[bin_idx] += 1

            # Create histogram
            max_count = max(bin_counts)
            result = [title.center(self.width)] if title else []
            
            for i, count in enumerate(bin_counts):
                # Calculate bar length
                bar_len = int((count / max_count) * (self.width - 15))
                bar = "█" * bar_len
                
                # Calculate bin range
                bin_start = min_val + i * bin_size
                bin_end = bin_start + bin_size
                
                # Format line
                line = f"{bin_start:4.1f}-{bin_end:4.1f} │{bar} {count}"
                result.append(line)

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to create histogram: {e}")
            return "Error creating histogram"

def format_metrics_summary(metrics: Dict[str, Any]) -> str:
    """Format metrics summary for display.
    
    Args:
        metrics: Metrics dictionary
        
    Returns:
        Formatted summary string
    """
    try:
        summary = [
            "System Metrics Summary",
            "=" * 50,
            f"CPU Usage: {metrics.get('cpu_percent', 0):.1f}%",
            f"Memory Usage: {metrics.get('memory_percent', 0):.1f}%",
            f"Disk Usage: {metrics.get('disk_percent', 0):.1f}%",
            f"Process Count: {metrics.get('process_count', 0)}",
            f"Load Average: {' '.join(f'{x:.2f}' for x in metrics.get('load_avg', [0, 0, 0]))}",
            "",
            "Network Statistics",
            "-" * 30
        ]

        network = metrics.get('network', {})
        if network:
            summary.extend([
                f"Bytes Sent: {network.get('bytes_sent', 0):,}",
                f"Bytes Received: {network.get('bytes_recv', 0):,}",
                f"Packets Sent: {network.get('packets_sent', 0):,}",
                f"Packets Received: {network.get('packets_recv', 0):,}",
                f"Errors In: {network.get('errors_in', 0)}",
                f"Errors Out: {network.get('errors_out', 0)}"
            ])

        return "\n".join(summary)

    except Exception as e:
        logger.error(f"Failed to format metrics summary: {e}")
        return "Error formatting metrics summary"

def create_metrics_visualization(metrics_history: Dict[str, List[Dict[str, Any]]]) -> str:
    """Create visualization of metrics history.
    
    Args:
        metrics_history: Dictionary of metric histories
        
    Returns:
        Visualization string
    """
    try:
        chart = ASCIIChart()
        output = []

        # CPU Usage Chart
        if 'cpu' in metrics_history:
            cpu_values = [entry['value'] for entry in metrics_history['cpu']]
            output.append(chart.create_line_chart(cpu_values, "CPU Usage History"))
            output.append("")

        # Memory Usage Chart
        if 'memory' in metrics_history:
            memory_values = [entry['value'] for entry in metrics_history['memory']]
            output.append(chart.create_line_chart(memory_values, "Memory Usage History"))
            output.append("")

        # Disk Usage Chart
        if 'disk' in metrics_history:
            disk_values = [entry['value'] for entry in metrics_history['disk']]
            output.append(chart.create_line_chart(disk_values, "Disk Usage History"))
            output.append("")

        # Network Usage
        if 'network' in metrics_history:
            network_data = {
                'Sent': metrics_history['network'][-1]['sent'],
                'Received': metrics_history['network'][-1]['received']
            }
            output.append(chart.create_bar_chart(network_data, "Network Usage"))

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Failed to create metrics visualization: {e}")
        return "Error creating visualization"
