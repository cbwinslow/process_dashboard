#!/bin/bash

# Script to rotate and archive logs

set -e

LOG_DIR="$HOME/.local/share/process-dashboard/logs"
ARCHIVE_DIR="$LOG_DIR/archive"
MAX_AGE_DAYS=30
MAX_SIZE_MB=100

# Create archive directory if needed
mkdir -p "$ARCHIVE_DIR"

# Rotate logs over size limit
find "$LOG_DIR" -type f -name "*.log" -size +"$MAX_SIZE_MB"M | while read -r log; do
    echo "Rotating large log: $log"
    mv "$log" "$log.$(date +%Y%m%d)"
    gzip "$log.$(date +%Y%m%d)"
    mv "$log.$(date +%Y%m%d).gz" "$ARCHIVE_DIR/"
done

# Archive old logs
find "$LOG_DIR" -type f -name "*.log" -mtime +"$MAX_AGE_DAYS" | while read -r log; do
    echo "Archiving old log: $log"
    gzip -c "$log" > "$ARCHIVE_DIR/$(basename "$log").$(date +%Y%m%d).gz"
    rm "$log"
done

# Clean up old archives
find "$ARCHIVE_DIR" -type f -name "*.gz" -mtime +90 -delete

echo "Log rotation complete"
