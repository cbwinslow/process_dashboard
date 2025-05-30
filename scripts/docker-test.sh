#!/bin/bash

# Script to run tests in Docker container

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests in Docker container...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm dashboard
}

# Function to run linting
run_lint() {
    echo -e "${YELLOW}Running linting in Docker container...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm lint
}

# Function to run type checking
run_type_check() {
    echo -e "${YELLOW}Running type checking in Docker container...${NC}"
    docker-compose -f docker-compose.dev.yml run --rm type-check
}

# Main execution
echo -e "${GREEN}Starting containerized testing...${NC}"

# Build containers
echo -e "${YELLOW}Building containers...${NC}"
docker-compose -f docker-compose.dev.yml build

# Run all checks
run_lint
run_type_check
run_tests

echo -e "${GREEN}All containerized tests completed successfully!${NC}"
