# Monitoring Quick Reference

## Common Commands

### Start Monitoring
```bash
./scripts/monitoring/dashboard-monitor.sh start
```

### Check Status
```bash
./scripts/monitoring/dashboard-monitor.sh status
```

### View Metrics
```bash
./scripts/monitoring/dashboard-monitor.sh visualize
```

### Manage Alerts
```bash
./scripts/monitoring/manage-templates.sh edit alerts
```

## Configuration Files

### Main Configuration
`~/.config/process-dashboard/monitoring.json`

### Alert Templates
`~/.config/process-dashboard/templates/`

### Logs
`~/.local/share/process-dashboard/logs/`

## Key Shortcuts

- 'm': Monitoring view
- 'a': Alerts view
- 'v': Visualization
- 'r': Refresh data
- 'q': Quit view

## Alert Levels

- INFO: Normal operations
- WARNING: Resource thresholds
- ERROR: Critical issues
- CRITICAL: System failures

## Common Issues

1. High CPU
   - Check process list
   - Review thresholds
   - Check history

2. Memory Usage
   - Monitor swap
   - Check leaks
   - Review limits

3. Disk Space
   - Check usage
   - Review quotas
   - Clean old data

## Quick Actions

1. Reset Monitoring
```bash
./scripts/monitoring/dashboard-monitor.sh reset
```

2. Test Alerts
```bash
./scripts/monitoring/dashboard-monitor.sh test-alerts
```

3. Export Data
```bash
./scripts/monitoring/dashboard-monitor.sh export
```
