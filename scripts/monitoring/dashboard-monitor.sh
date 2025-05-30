#!/bin/bash

# Unified monitoring interface for Process Dashboard

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
COMMAND="status"
METRIC_TYPE="all"
DURATION="1h"
UPDATE_INTERVAL=5
OUTPUT_FORMAT="ascii"
LOG_FILE="$HOME/.local/share/process-dashboard/logs/monitoring.log"

# Help function
show_help() {
    echo "Process Dashboard Monitoring Tool"
    echo
    echo "Usage: dashboard-monitor.sh COMMAND [options]"
    echo
    echo "Commands:"
    echo "  status         Show current system status"
    echo "  start         Start continuous monitoring"
    echo "  visualize     Generate metrics visualization"
    echo "  alerts        Show/configure alerts"
    echo "  export        Export monitoring data"
    echo
    echo "Options:"
    echo "  --metric TYPE     Metric type (cpu, memory, disk, network, all)"
    echo "  --duration TIME   Duration (e.g., 1h, 30m, 60s)"
    echo "  --interval SEC    Update interval in seconds"
    echo "  --format FORMAT   Output format (ascii, json)"
    echo "  --log FILE       Log file location"
    echo "  --help           Show this help message"
    echo
    echo "Examples:"
    echo "  dashboard-monitor.sh status"
    echo "  dashboard-monitor.sh start --interval 10"
    echo "  dashboard-monitor.sh visualize --metric cpu --duration 1h"
    echo "  dashboard-monitor.sh alerts --configure"
    echo "  dashboard-monitor.sh export --format json"
}

# Parse command
if [ $# -gt 0 ]; then
    COMMAND="$1"
    shift
fi

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --metric)
            METRIC_TYPE="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --interval)
            UPDATE_INTERVAL="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --log)
            LOG_FILE="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to show current status
show_status() {
    echo -e "${GREEN}Current System Status${NC}"
    python - << 'EOF'
from monitoring.metrics import MetricsCollector
from monitoring.visualization.charts import format_metrics_summary

collector = MetricsCollector()
metrics = collector.collect_metrics()
print(format_metrics_summary(metrics))
EOF
}

# Function to start monitoring
start_monitoring() {
    echo -e "${GREEN}Starting continuous monitoring...${NC}"
    ./scripts/monitoring/monitor.sh --interval "$UPDATE_INTERVAL" --log "$LOG_FILE"
}

# Function to visualize metrics
visualize_metrics() {
    echo -e "${GREEN}Generating visualization...${NC}"
    ./scripts/monitoring/visualize.sh --metric "$METRIC_TYPE" --duration "$DURATION" --format "$OUTPUT_FORMAT"
}

# Function to manage alerts
manage_alerts() {
    echo -e "${GREEN}Alert Management${NC}"
    python - << 'EOF'
from monitoring.alerts import AlertManager

manager = AlertManager()
print("\nCurrent Alert Configuration:")
for key, value in manager.config.items():
    print(f"{key}: {value}")
EOF
}

# Function to export data
export_data() {
    echo -e "${GREEN}Exporting monitoring data...${NC}"
    python - << 'EOF'
from monitoring.metrics import MetricsCollector
import json
from pathlib import Path
from datetime import datetime

collector = MetricsCollector()
export_data = {
    'timestamp': datetime.now().isoformat(),
    'metrics': collector.collect_metrics(),
    'history': collector.metrics_history
}

export_path = Path.home() / 'process-dashboard-export.json'
with open(export_path, 'w') as f:
    json.dump(export_data, f, indent=2)
print(f"Data exported to {export_path}")
EOF
}

# Execute command
case $COMMAND in
    status)
        show_status
        ;;
    start)
        start_monitoring
        ;;
    visualize)
        visualize_metrics
        ;;
    alerts)
        manage_alerts
        ;;
    export)
        export_data
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac
