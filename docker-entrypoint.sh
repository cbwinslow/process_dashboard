#!/bin/bash
set -e

# Setup logging directory
mkdir -p ~/.local/share/process-dashboard/logs

# Initialize configuration if not exists
if [ ! -f ~/.config/process-dashboard/config.json ]; then
    mkdir -p ~/.config/process-dashboard
    echo '{
        "matrix_theme": true,
        "update_interval": 2,
        "history_length": 3600,
        "show_system": true,
        "show_children": true
    }' > ~/.config/process-dashboard/config.json
fi

# Execute command
exec "$@"
