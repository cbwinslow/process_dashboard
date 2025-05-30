# Development Scripts

## Available Scripts

- `dev_setup.sh`: Set up development environment
- `test.sh`: Run test suite
- `lint.sh`: Run code quality checks
- `docker-test.sh`: Run tests in Docker
- `verify_setup.sh`: Verify installation

## Usage

All scripts should be run from the project root:

```bash
# Set up development environment
./scripts/dev_setup.sh

# Run tests
./scripts/test.sh

# Run all checks
./scripts/run_checks.sh
```

## Adding New Scripts

1. Create script in this directory
2. Make executable: `chmod +x scripts/your-script.sh`
3. Add documentation here
4. Update DEVELOPMENT.md if needed
