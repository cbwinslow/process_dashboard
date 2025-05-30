#!/bin/bash

# Script to set up development environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Setting up development environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -e ".[dev]"

# Install pre-commit hooks
echo -e "${GREEN}Installing pre-commit hooks...${NC}"
pre-commit install

# Create necessary directories
echo -e "${GREEN}Creating project directories...${NC}"
mkdir -p src/tests
mkdir -p src/processes
mkdir -p src/ui
mkdir -p src/config

# Final message
echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${YELLOW}Activate the virtual environment with: source venv/bin/activate${NC}"
