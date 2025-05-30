#!/bin/bash

# Script to set up automated maintenance

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up Process Dashboard maintenance...${NC}"

# Create maintenance directories
echo "Creating maintenance directories..."
mkdir -p ~/.local/share/process-dashboard/maintenance

# Install scripts
echo "Installing maintenance scripts..."
cp scripts/maintenance/*.sh ~/.local/share/process-dashboard/maintenance/
chmod +x ~/.local/share/process-dashboard/maintenance/*.sh

# Create cron configuration
echo "Configuring cron jobs..."
CRON_FILE=$(mktemp)

# Add cron jobs
cat > "$CRON_FILE" << 'EOF'
# Process Dashboard Maintenance
0 1 * * * ~/.local/share/process-dashboard/maintenance/rotate_logs.sh >> ~/.local/share/process-dashboard/logs/maintenance.log 2>&1
0 */6 * * * ~/.local/share/process-dashboard/maintenance/check_performance.sh >> ~/.local/share/process-dashboard/logs/maintenance.log 2>&1
0 2 * * * ~/.local/share/process-dashboard/maintenance/security_scan.sh >> ~/.local/share/process-dashboard/logs/maintenance.log 2>&1
0 3 * * 0 ~/.local/share/process-dashboard/maintenance/cleanup.sh >> ~/.local/share/process-dashboard/logs/maintenance.log 2>&1
EOF

# Install new cron configuration
crontab -l > /tmp/current_cron 2>/dev/null || true
cat "$CRON_FILE" >> /tmp/current_cron
crontab /tmp/current_cron

# Clean up
rm "$CRON_FILE" /tmp/current_cron

# Create log rotation configuration
echo "Configuring log rotation..."
sudo tee /etc/logrotate.d/process-dashboard > /dev/null << 'EOF'
~/.local/share/process-dashboard/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 $USER $USER
}
EOF

# Set up monitoring
echo "Setting up monitoring..."
mkdir -p ~/.config/process-dashboard/monitoring

# Create monitoring configuration
cat > ~/.config/process-dashboard/monitoring/alerts.json << 'EOF'
{
    "cpu_threshold": 80,
    "memory_threshold": 80,
    "disk_threshold": 90,
    "log_size_threshold_mb": 100,
    "alert_email": "",
    "notification_level": "warning"
}
EOF

echo -e "${GREEN}Maintenance setup complete!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review cron jobs: crontab -l"
echo "2. Check log rotation: cat /etc/logrotate.d/process-dashboard"
echo "3. Configure monitoring: ~/.config/process-dashboard/monitoring/alerts.json"
echo
echo -e "${GREEN}Maintenance will run automatically according to schedule.${NC}"
