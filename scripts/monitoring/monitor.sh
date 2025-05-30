#!/bin/bash

# Script to start continuous monitoring

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
UPDATE_INTERVAL=5
LOG_FILE="$HOME/.local/share/process-dashboard/logs/monitoring.log"

# Help function
show_help() {
    echo "Usage: monitor.sh [options]"
    echo
    echo "Options:"
    echo "  --interval SECONDS  Update interval (default: 5)"
    echo "  --log FILE         Log file location"
    echo "  --help             Show this help message"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            UPDATE_INTERVAL="$2"
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

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Create temporary Python script
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << 'EOF'
from monitoring.metrics import MetricsCollector
from monitoring.alerts import AlertManager
import time
import sys

def main():
    # Get update interval
    interval = int(sys.argv[1])
    
    # Initialize components
    collector = MetricsCollector()
    alert_manager = AlertManager()
    
    print("Starting monitoring...")
    
    try:
        while True:
            # Collect metrics
            metrics = collector.collect_metrics()
            
            # Check for alerts
            alerts = alert_manager.check_thresholds(metrics)
            
            # Handle alerts
            for alert in alerts:
                print(f"ALERT: {alert}")
                alert_manager.send_alert(alert)
            
            # Wait for next update
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Start monitoring
echo -e "${GREEN}Starting monitoring...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo -e "${YELLOW}Logging to: ${LOG_FILE}${NC}"

# Run monitor with logging
python "$TMP_SCRIPT" "$UPDATE_INTERVAL" 2>&1 | tee -a "$LOG_FILE"

# Cleanup
rm "$TMP_SCRIPT"

echo -e "${GREEN}Monitoring stopped${NC}"
