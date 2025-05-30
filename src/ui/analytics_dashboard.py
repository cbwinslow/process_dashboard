"""
Analytics dashboard for Process Dashboard templates.

Provides visualizations and insights for template usage and performance.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import (
    Static, DataTable, BarChart, LineChart, Button,
    Label, Select, Tabs, Tab
)
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich import box

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ..config.template_analytics import (
    TemplateAnalytics,
    TemplateUsage,
    TemplateEvent
)

logger = logging.getLogger("dashboard.ui.analytics")

class MetricsPanel(Static):
    """Key metrics display panel."""

    DEFAULT_CSS = """
    MetricsPanel {
        layout: grid;
        grid-size: 4;
        grid-columns: 1fr 1fr 1fr 1fr;
        padding: 1;
        height: auto;
    }

    .metric-box {
        border: solid $accent;
        padding: 1;
        text-align: center;
    }

    .metric-value {
        text-style: bold;
    }
    """

    def __init__(self, metrics: Dict[str, Any]):
        """Initialize metrics panel.
        
        Args:
            metrics: Metrics dictionary
        """
        super().__init__()
        self.metrics = metrics

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        for name, value in self.metrics.items():
            with Vertical(classes="metric-box"):
                yield Label(name)
                yield Label(str(value), classes="metric-value")

class UsageTrendChart(Static):
    """Usage trend line chart."""

    def __init__(self, trends: Dict[str, List[float]], days: int = 30):
        """Initialize trend chart.
        
        Args:
            trends: Trend data
            days: Number of days
        """
        super().__init__()
        self.trends = trends
        self.days = days

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Create date labels
        dates = [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(self.days - 1, -1, -1)
        ]

        # Create line chart
        yield LineChart(
            data={
                "Uses": self.trends.get("uses", [0] * self.days),
                "Errors": self.trends.get("errors", [0] * self.days)
            },
            x_labels=dates,
            title="Usage Trends"
        )

class PerformanceChart(Static):
    """Performance metrics bar chart."""

    def __init__(self, metrics: Dict[str, float]):
        """Initialize performance chart.
        
        Args:
            metrics: Performance metrics
        """
        super().__init__()
        self.metrics = metrics

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield BarChart(
            data=self.metrics,
            title="Performance Metrics"
        )

class AnalyticsDashboard(Static):
    """Template analytics dashboard."""

    DEFAULT_CSS = """
    AnalyticsDashboard {
        layout: vertical;
        height: 100%;
        background: $background;
    }

    #header {
        height: 3;
        padding: 1;
        background: $accent;
    }

    #main-container {
        height: 100%;
    }

    Tabs {
        dock: top;
    }

    #metrics-panel {
        height: auto;
        margin-bottom: 1;
    }

    #charts-container {
        height: 60%;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
    }

    #details-panel {
        height: 30%;
    }

    DataTable {
        height: 100%;
        border: solid $accent;
    }

    #error-message {
        color: $error;
        margin: 1;
    }
    """

    # Reactive state
    selected_template = reactive[Optional[str]](None)
    selected_period = reactive[int](30)

    def __init__(self, analytics: TemplateAnalytics):
        """Initialize analytics dashboard.
        
        Args:
            analytics: Template analytics instance
        """
        super().__init__()
        self.analytics = analytics

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Header
        with Horizontal(id="header"):
            yield Label("Template Analytics")
            yield Select(
                [
                    ("Last 7 Days", 7),
                    ("Last 30 Days", 30),
                    ("Last 90 Days", 90)
                ],
                value=30,
                id="period-select"
            )

        # Main container
        with Vertical(id="main-container"):
            # Tab navigation
            with Tabs():
                yield Tab("Overview", id="overview-tab")
                yield Tab("Usage", id="usage-tab")
                yield Tab("Performance", id="performance-tab")
                yield Tab("Errors", id="errors-tab")

            # Overview tab content
            with Vertical(id="overview-content"):
                # Key metrics
                yield MetricsPanel(self._get_overview_metrics())

                # Charts
                with Horizontal(id="charts-container"):
                    yield UsageTrendChart(
                        self._get_usage_trends(),
                        days=self.selected_period
                    )
                    yield PerformanceChart(
                        self._get_performance_metrics()
                    )

                # Popular templates
                with Vertical(id="details-panel"):
                    yield Label("Popular Templates")
                    yield DataTable(id="popular-templates")

            # Usage tab content
            with Vertical(id="usage-content", classes="tab-content"):
                yield Label("Template Usage Details")
                with Grid():
                    yield Label("Total Uses")
                    yield Label("Average Duration")
                    yield Label("Success Rate")
                    yield Label("User Rating")
                yield DataTable(id="usage-details")

            # Performance tab content
            with Vertical(id="performance-content", classes="tab-content"):
                yield Label("Performance Analysis")
                yield BarChart(id="performance-chart")
                yield DataTable(id="performance-details")

            # Errors tab content
            with Vertical(id="errors-content", classes="tab-content"):
                yield Label("Error Analysis")
                yield DataTable(id="error-log")

        yield Static(id="error-message")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self.setup_tables()
        self.update_display()

    def setup_tables(self) -> None:
        """Set up data tables."""
        # Popular templates table
        popular = self.query_one("#popular-templates", DataTable)
        popular.add_columns(
            "Template",
            "Uses",
            "Success Rate",
            "Rating"
        )

        # Usage details table
        usage = self.query_one("#usage-details", DataTable)
        usage.add_columns(
            "Date",
            "Uses",
            "Duration",
            "Success"
        )

        # Performance details table
        performance = self.query_one("#performance-details", DataTable)
        performance.add_columns(
            "Metric",
            "Value",
            "Trend"
        )

        # Error log table
        errors = self.query_one("#error-log", DataTable)
        errors.add_columns(
            "Timestamp",
            "Template",
            "Error",
            "Context"
        )

    def _get_overview_metrics(self) -> Dict[str, Any]:
        """Get overview metrics.
        
        Returns:
            Metrics dictionary
        """
        try:
            popular = self.analytics.get_popular_templates()
            total_uses = sum(t["uses"] for t in popular)
            avg_success = sum(t["success_rate"] for t in popular) / len(popular)
            
            return {
                "Total Templates": len(popular),
                "Total Uses": total_uses,
                "Success Rate": f"{avg_success:.1f}%",
                "Active Today": self._get_active_today()
            }
        except Exception as e:
            logger.error(f"Failed to get overview metrics: {e}")
            return {}

    def _get_usage_trends(self) -> Dict[str, List[float]]:
        """Get usage trend data.
        
        Returns:
            Trend data dictionary
        """
        try:
            if self.selected_template:
                return self.analytics.get_usage_trends(
                    self.selected_template,
                    self.selected_period
                )
            
            # Get aggregate trends
            popular = self.analytics.get_popular_templates()
            trends = {}
            
            for template in popular:
                template_trends = self.analytics.get_usage_trends(
                    template["template_id"],
                    self.selected_period
                )
                
                for metric, values in template_trends.items():
                    if metric not in trends:
                        trends[metric] = values
                    else:
                        trends[metric] = [
                            a + b for a, b in zip(trends[metric], values)
                        ]
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get usage trends: {e}")
            return {}

    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics.
        
        Returns:
            Performance metrics dictionary
        """
        try:
            if self.selected_template:
                usage = self.analytics.get_template_usage(self.selected_template)
                if usage:
                    return usage.performance_impact
            
            # Get aggregate metrics
            popular = self.analytics.get_popular_templates()
            metrics = {}
            
            for template in popular:
                usage = self.analytics.get_template_usage(template["template_id"])
                if usage:
                    for metric, value in usage.performance_impact.items():
                        if metric not in metrics:
                            metrics[metric] = value
                        else:
                            metrics[metric] = (metrics[metric] + value) / 2
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}

    def _get_active_today(self) -> int:
        """Get number of active templates today.
        
        Returns:
            Active template count
        """
        try:
            today = datetime.now().date()
            popular = self.analytics.get_popular_templates()
            
            return sum(
                1 for t in popular
                if t["last_used"].date() == today
            )
        except Exception as e:
            logger.error(f"Failed to get active templates: {e}")
            return 0

    def update_display(self) -> None:
        """Update dashboard display."""
        try:
            # Update metrics panel
            metrics = self._get_overview_metrics()
            self.query_one(MetricsPanel).update(metrics)

            # Update trend chart
            trends = self._get_usage_trends()
            self.query_one(UsageTrendChart).update(trends)

            # Update performance chart
            metrics = self._get_performance_metrics()
            self.query_one(PerformanceChart).update(metrics)

            # Update tables
            self._update_tables()

        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            self.show_error("Failed to update display")

    def _update_tables(self) -> None:
        """Update data tables."""
        try:
            # Update popular templates
            popular = self.query_one("#popular-templates", DataTable)
            popular.clear()
            
            for template in self.analytics.get_popular_templates():
                popular.add_row(
                    template["template_id"],
                    str(template["uses"]),
                    f"{template['success_rate']:.1f}%",
                    "★★★★☆"  # TODO: Add actual rating
                )

            # Update usage details if template selected
            if self.selected_template:
                usage = self.query_one("#usage-details", DataTable)
                usage.clear()
                
                trends = self.analytics.get_usage_trends(
                    self.selected_template,
                    self.selected_period
                )
                
                for day, uses in enumerate(trends.get("uses", [])):
                    date = datetime.now() - timedelta(days=self.selected_period - day)
                    usage.add_row(
                        date.strftime("%Y-%m-%d"),
                        str(uses),
                        f"{trends['duration'][day]:.1f}s",
                        "✓" if trends['errors'][day] == 0 else "✗"
                    )

            # Update error log
            errors = self.query_one("#error-log", DataTable)
            errors.clear()
            
            # TODO: Add error log data

        except Exception as e:
            logger.error(f"Failed to update tables: {e}")
            self.show_error("Failed to update tables")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle period selection change."""
        if event.select.id == "period-select":
            self.selected_period = int(event.value)
            self.update_display()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle template selection."""
        if event.data_table.id == "popular-templates":
            self.selected_template = event.row_key.value
            self.update_display()

    def show_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message
        """
        self.query_one("#error-message").update(message)
