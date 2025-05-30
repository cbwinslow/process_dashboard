# Getting Started with Process Dashboard

## Quick Installation

### Using pip
```bash
pip install process-dashboard
process-dashboard
```

### Using Docker
```bash
docker run -it \
    --network host \
    --cap-add SYS_PTRACE \
    process-dashboard
```

## Development Setup

1. Clone Repository
```bash
git clone https://github.com/yourusername/process-dashboard.git
cd process-dashboard
```

2. Set Up Environment
```bash
# Using local Python
./scripts/dev_setup.sh
source venv/bin/activate

# Or using Docker
docker-compose -f docker-compose.dev.yml up --build
```

3. Verify Setup
```bash
# Local verification
./scripts/verify_setup.sh

# Docker verification
./scripts/docker-test.sh
```

## Basic Usage

### Process Monitoring
- View processes with `Up/Down` arrows
- Filter processes with `f`
- Sort by different metrics
- Monitor system resources

### Process Control
- Select process with `Enter`
- Terminate process with `t`
- Kill process with `k`
- Adjust priority with arrow keys

### Configuration
- Press `c` for config panel
- Set update intervals
- Configure display options
- Adjust logging levels

## Development Workflow

1. Create Feature Branch
```bash
git checkout -b feature/your-feature
```

2. Make Changes
```bash
# Run tests while developing
pytest --watch

# Check code quality
./scripts/lint.sh
```

3. Submit Changes
```bash
# Run all checks
./scripts/run_checks.sh

# Create pull request
gh pr create
```

## Docker Development

1. Build Development Container
```bash
docker-compose -f docker-compose.dev.yml build
```

2. Run Tests
```bash
docker-compose -f docker-compose.dev.yml run --rm dashboard pytest
```

3. Development Shell
```bash
docker-compose -f docker-compose.dev.yml run --rm dashboard bash
```

## Troubleshooting

### Installation Issues
```bash
# Verify Python version
python --version  # Should be 3.7 or later

# Check dependencies
pip check process-dashboard
```

### Runtime Issues
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
process-dashboard

# Check logs
tail -f ~/.local/share/process-dashboard/logs/dashboard.log
```

### Docker Issues
```bash
# Check container logs
docker logs process-dashboard

# Verify permissions
docker-compose -f docker-compose.dev.yml run --rm dashboard id
```

## Getting Help

1. Check Documentation
   - README.md for overview
   - DEVELOPMENT.md for development
   - docs/ directory for details

2. Common Issues
   - Permission errors: Check user permissions
   - Display issues: Verify terminal support
   - Performance: Check resource usage

3. Reporting Issues
   - Use issue templates
   - Include logs
   - Provide reproduction steps

## Next Steps

1. Explore Advanced Features
   - Custom monitoring
   - Alert configuration
   - Process grouping

2. Contribute
   - Check CONTRIBUTING.md
   - Review open issues
   - Submit improvements

3. Stay Updated
   - Watch releases
   - Check CHANGELOG.md
   - Follow project updates

