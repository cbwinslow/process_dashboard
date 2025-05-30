# Process Dashboard Monitoring Usage Guide

## Quick Start

The dashboard monitor provides a unified interface for all monitoring functionality:

```bash
# Show current status
./scripts/monitoring/dashboard-monitor.sh status

# Start continuous monitoring
./scripts/monitoring/dashboard-monitor.sh start

# Visualize metrics
./scripts/monitoring/dashboard-monitor.sh visualize
```

## Commands

### Status
Shows current system status:
```bash
./scripts/monitoring/dashboard-monitor.sh status
```

### Start Monitoring
Start continuous monitoring:
```bash
./scripts/monitoring/dashboard-monitor.sh start --interval 10
```

### Visualize Metrics
Generate visualizations:
```bash
./scripts/monitoring/dashboard-monitor.sh visualize --metric cpu --duration 1h
```

### Manage Alerts
Configure and view alerts:
```bash
./scripts/monitoring/dashboard-monitor.sh alerts
```

### Export Data
Export monitoring data:
```bash
./scripts/monitoring/dashboard-monitor.sh export --format json
```

## Options

- `--metric TYPE`: Metric type (cpu, memory, disk, network, all)
- `--duration TIME`: Duration (e.g., 1h, 30m, 60s)
- `--interval SEC`: Update interval in seconds
- `--format FORMAT`: Output format (ascii, json)
- `--log FILE`: Log file location

## Examples

```bash
# Monitor CPU usage
./scripts/monitoring/dashboard-monitor.sh visualize --metric cpu --duration 30m

# Export JSON data
./scripts/monitoring/dashboard-monitor.sh export --format json

# Continuous monitoring with custom interval
./scripts/monitoring/dashboard-monitor.sh start --interval 30

# View specific metric status
./scripts/monitoring/dashboard-monitor.sh status --metric memory
```

## Tips

1. Regular Monitoring
   ```bash
   # Add to crontab
   */5 * * * * /path/to/dashboard-monitor.sh status >> /path/to/status.log
   ```

2. Alert Configuration
   ```bash
   # Configure alerts
   ./scripts/monitoring/dashboard-monitor.sh alerts --configure
   ```

3. Data Analysis
   ```bash
   # Export and analyze
   ./scripts/monitoring/dashboard-monitor.sh export --format json
   ```

## Troubleshooting

1. Monitor not starting:
   ```bash
   # Check permissions
   chmod +x scripts/monitoring/dashboard-monitor.sh
   ```

2. Missing data:
   ```bash
   # Check log file
   tail -f ~/.local/share/process-dashboard/logs/monitoring.log
   ```

3. Visualization issues:
   ```bash
   # Verify terminal support
   echo $TERM
   ```
