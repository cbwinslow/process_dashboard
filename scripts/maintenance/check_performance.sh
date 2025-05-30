#!/bin/bash

# Script to check dashboard performance

set -e

echo "Checking Process Dashboard Performance"
echo "===================================="

# Check CPU usage
echo "CPU Usage:"
ps aux | grep process-dashboard | grep -v grep | awk '{print $3"%"}'

# Check memory usage
echo -e "\nMemory Usage:"
ps aux | grep process-dashboard | grep -v grep | awk '{print $4"%"}'

# Check file descriptors
echo -e "\nOpen File Descriptors:"
lsof -p $(pgrep process-dashboard) | wc -l

# Check log size
echo -e "\nLog File Sizes:"
du -sh ~/.local/share/process-dashboard/logs/*.log 2>/dev/null || echo "No log files found"

# Check update frequency
echo -e "\nUpdate Frequency:"
grep "update" ~/.local/share/process-dashboard/logs/dashboard.log | tail -n 10

# Check system load
echo -e "\nSystem Load:"
uptime

# Check disk usage for logs
echo -e "\nLog Directory Disk Usage:"
du -sh ~/.local/share/process-dashboard/logs/

# Check process count
echo -e "\nProcess Count:"
ps aux | grep process-dashboard | grep -v grep | wc -l

# Check network connections
echo -e "\nNetwork Connections:"
netstat -an | grep process-dashboard | wc -l

echo -e "\nPerformance check complete"
