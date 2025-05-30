#!/bin/bash

# Script to perform security checks

set -e

echo "Running Security Scan"
echo "===================="

# Check file permissions
echo "Checking file permissions..."
find ~/.local/share/process-dashboard -type f -ls

# Check log file permissions
echo -e "\nChecking log file permissions..."
ls -l ~/.local/share/process-dashboard/logs/

# Check config file permissions
echo -e "\nChecking config file permissions..."
ls -l ~/.config/process-dashboard/

# Check for suspicious processes
echo -e "\nChecking for suspicious processes..."
ps aux | grep process-dashboard | grep -v grep

# Check open ports
echo -e "\nChecking open ports..."
netstat -tlpn | grep process-dashboard

# Check file integrity
echo -e "\nChecking file integrity..."
find src -type f -name "*.py" -exec md5sum {} \;

# Check dependencies
echo -e "\nChecking dependencies..."
pip list | grep -E "textual|psutil|rich"

# Check for known vulnerabilities
echo -e "\nChecking for known vulnerabilities..."
safety check 2>/dev/null || echo "Safety not installed. Run: pip install safety"

echo -e "\nSecurity scan complete"
