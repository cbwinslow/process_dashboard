#!/bin/bash

# Script to run linting and type checking

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Running black code formatter...${NC}"
black src tests

echo -e "${GREEN}Running flake8 linter...${NC}"
flake8 src tests

echo -e "${GREEN}Running mypy type checker...${NC}"
mypy src

# Check if any tools failed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All checks passed successfully!${NC}"
else
    echo -e "${RED}Some checks failed!${NC}"
    exit 1
fi
