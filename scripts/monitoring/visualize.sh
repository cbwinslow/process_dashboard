#!/bin/bash

# Script to visualize monitoring data

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
METRIC_TYPE="all"
DURATION="1h"
OUTPUT_FORMAT="ascii"

# Help function
show_help() {
    echo "Usage: visualize.sh [options]"
    echo
    echo "Options:"
    echo "  --metric TYPE    Metric type (cpu, memory, disk, network, all)"
    echo "  --duration TIME  Duration (e.g., 1h, 30m, 60s)"
    echo "  --format FORMAT  Output format (ascii, json)"
    echo "  --help          Show this help message"
    echo
    echo "Examples:"
    echo "  visualize.sh --metric cpu --duration 1h"
    echo "  visualize.sh --metric all --format json"
}

# Parse arguments
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
        --format)
            OUTPUT_FORMAT="$2"
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

# Validate metric type
valid_metrics=("cpu" "memory" "disk" "network" "all")
if [[ ! " ${valid_metrics[@]} " =~ " ${METRIC_TYPE} " ]]; then
    echo -e "${RED}Invalid metric type: ${METRIC_TYPE}${NC}"
    show_help
    exit 1
fi

# Convert duration to seconds
case $DURATION in
    *h)
        SECONDS=${DURATION%h}
        SECONDS=$((SECONDS * 3600))
        ;;
    *m)
        SECONDS=${DURATION%m}
        SECONDS=$((SECONDS * 60))
        ;;
    *s)
        SECONDS=${DURATION%s}
        ;;
    *)
        echo -e "${RED}Invalid duration format${NC}"
        show_help
        exit 1
        ;;
esac

# Create temporary Python script
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << 'EOF'
from monitoring.visualization.charts import ASCIIChart, create_metrics_visualization
from monitoring.metrics import MetricsCollector
import json
import sys

def main():
    # Get command line arguments
    metric_type = sys.argv[1]
    duration = int(sys.argv[2])
    output_format = sys.argv[3]

    try:
        # Initialize collector
        collector = MetricsCollector(history_length=duration)
        
        # Collect current metrics
        metrics = collector.collect_metrics()

        if output_format == "json":
            # Output JSON format
            if metric_type == "all":
                print(json.dumps(collector.metrics_history, indent=2))
            else:
                print(json.dumps(collector.get_history(metric_type), indent=2))
        else:
            # Output ASCII visualization
            if metric_type == "all":
                print(create_metrics_visualization(collector.metrics_history))
            else:
                chart = ASCIIChart()
                history = collector.get_history(metric_type)
                if history:
                    values = [entry['value'] for entry in history]
                    print(chart.create_line_chart(
                        values,
                        f"{metric_type.title()} Usage History"
                    ))
                else:
                    print(f"No data available for {metric_type}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Run visualization
echo -e "${GREEN}Generating visualization...${NC}"
python "$TMP_SCRIPT" "$METRIC_TYPE" "$SECONDS" "$OUTPUT_FORMAT"

# Cleanup
rm "$TMP_SCRIPT"

echo -e "${GREEN}Visualization complete${NC}"
