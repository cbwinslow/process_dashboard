#!/bin/bash

# Script to clean up temporary files and old data

set -e

echo "Running Cleanup"
echo "=============="

# Clean Python cache files
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Clean test cache
echo -e "\nCleaning test cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true

# Clean build artifacts
echo -e "\nCleaning build artifacts..."
rm -rf build/ dist/ *.egg-info/

# Clean logs older than 90 days
echo -e "\nCleaning old logs..."
find ~/.local/share/process-dashboard/logs -type f -mtime +90 -delete 2>/dev/null || true

# Clean temporary files
echo -e "\nCleaning temporary files..."
find /tmp -name "process-dashboard-*" -mtime +1 -delete 2>/dev/null || true

echo -e "\nCleanup complete"
