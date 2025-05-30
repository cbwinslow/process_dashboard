#!/bin/bash

# Script to run tests and generate coverage reports

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Running tests with coverage...${NC}"

# Run pytest with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Tests passed successfully!${NC}"
    echo "Coverage report generated in htmlcov/index.html"
else
    echo -e "${RED}Tests failed!${NC}"
    exit 1
fi
