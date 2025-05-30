#!/bin/bash

# Script to manage monitoring templates and configurations

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default paths
CONFIG_DIR="$HOME/.config/process-dashboard"
TEMPLATE_DIR="$CONFIG_DIR/templates"

# Help function
show_help() {
    echo "Process Dashboard Template Manager"
    echo
    echo "Usage: manage-templates.sh COMMAND [options]"
    echo
    echo "Commands:"
    echo "  list              List available templates"
    echo "  install TYPE      Install template type (basic, server)"
    echo "  create NAME       Create new template"
    echo "  edit NAME         Edit existing template"
    echo "  delete NAME       Delete template"
    echo "  export NAME       Export template"
    echo "  import FILE       Import template"
    echo
    echo "Options:"
    echo "  --force          Force operation"
    echo "  --help           Show this help message"
}

# Create necessary directories
mkdir -p "$CONFIG_DIR" "$TEMPLATE_DIR"

# Command functions
list_templates() {
    echo -e "${GREEN}Available Templates:${NC}"
    echo "Basic Templates:"
    ls -1 config/examples/monitoring/*.json 2>/dev/null || echo "None"
    echo
    echo "Custom Templates:"
    ls -1 "$TEMPLATE_DIR"/*.json 2>/dev/null || echo "None"
}

install_template() {
    local type="$1"
    local target="$CONFIG_DIR/monitoring.json"
    
    case "$type" in
        basic)
            cp config/examples/monitoring/basic_monitoring.json "$target"
            echo -e "${GREEN}Installed basic monitoring configuration${NC}"
            ;;
        server)
            cp config/examples/monitoring/server_monitoring.json "$target"
            echo -e "${GREEN}Installed server monitoring configuration${NC}"
            ;;
        *)
            echo -e "${RED}Unknown template type: $type${NC}"
            exit 1
            ;;
    esac
}

create_template() {
    local name="$1"
    local file="$TEMPLATE_DIR/$name.json"
    
    if [ -f "$file" ]; then
        echo -e "${RED}Template already exists: $name${NC}"
        exit 1
    fi
    
    # Create template with Python
    python - << EOF
import json

template = {
    "alerts": {
        "example_alert": {
            "threshold": 80,
            "duration": 300,
            "actions": ["notify", "log"]
        }
    },
    "monitoring": {
        "interval": 5,
        "history_length": 3600,
        "metrics_enabled": {
            "cpu": true,
            "memory": true
        }
    },
    "notifications": {
        "email": {"enabled": false},
        "desktop": {"enabled": true}
    }
}

with open("$file", 'w') as f:
    json.dump(template, f, indent=4)
EOF
    
    echo -e "${GREEN}Created template: $file${NC}"
    echo "Edit the template to customize settings"
}

edit_template() {
    local name="$1"
    local file="$TEMPLATE_DIR/$name.json"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}Template not found: $name${NC}"
        exit 1
    fi
    
    ${EDITOR:-vim} "$file"
    
    # Validate JSON
    python -m json.tool "$file" > /dev/null
    echo -e "${GREEN}Template updated: $file${NC}"
}

delete_template() {
    local name="$1"
    local file="$TEMPLATE_DIR/$name.json"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}Template not found: $name${NC}"
        exit 1
    fi
    
    rm "$file"
    echo -e "${GREEN}Deleted template: $name${NC}"
}

export_template() {
    local name="$1"
    local file="$TEMPLATE_DIR/$name.json"
    local export_file="$name-$(date +%Y%m%d).json"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}Template not found: $name${NC}"
        exit 1
    fi
    
    cp "$file" "$export_file"
    echo -e "${GREEN}Exported template to: $export_file${NC}"
}

import_template() {
    local file="$1"
    local name=$(basename "$file" .json)
    local target="$TEMPLATE_DIR/$name.json"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}File not found: $file${NC}"
        exit 1
    fi
    
    # Validate JSON
    python -m json.tool "$file" > /dev/null
    
    cp "$file" "$target"
    echo -e "${GREEN}Imported template as: $name${NC}"
}

# Parse command
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

COMMAND="$1"
shift

case $COMMAND in
    list)
        list_templates
        ;;
    install)
        [ $# -eq 0 ] && { echo "Specify template type"; exit 1; }
        install_template "$1"
        ;;
    create)
        [ $# -eq 0 ] && { echo "Specify template name"; exit 1; }
        create_template "$1"
        ;;
    edit)
        [ $# -eq 0 ] && { echo "Specify template name"; exit 1; }
        edit_template "$1"
        ;;
    delete)
        [ $# -eq 0 ] && { echo "Specify template name"; exit 1; }
        delete_template "$1"
        ;;
    export)
        [ $# -eq 0 ] && { echo "Specify template name"; exit 1; }
        export_template "$1"
        ;;
    import)
        [ $# -eq 0 ] && { echo "Specify file path"; exit 1; }
        import_template "$1"
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac
