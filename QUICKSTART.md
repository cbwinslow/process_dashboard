# Process Dashboard Quick Start Guide

## For Users

### Quick Installation
```bash
pip install process-dashboard
```

### Start the Dashboard
```bash
process-dashboard
```

### Basic Usage
1. View Processes:
   - Up/Down arrows to navigate
   - Enter to select process
   - 'f' to filter processes
   - 'r' to refresh

2. Process Control:
   - 't' to terminate selected process
   - 'k' to kill selected process
   - Arrow keys to adjust priority

3. Resource Monitoring:
   - Real-time CPU, Memory, Disk usage
   - Network statistics
   - System load information

4. Configuration:
   - 'c' to open config panel
   - Customize update intervals
   - Set display preferences
   - Configure alerts

## For Developers

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/process-dashboard.git
cd process-dashboard

# Setup development environment
./scripts/dev_setup.sh
source venv/bin/activate

# Verify setup
./scripts/verify_setup.sh

# Run tests
./scripts/test.sh
```

### Project Structure
```
process-dashboard/
├── src/               # Source code
│   ├── processes/     # Process monitoring
│   ├── ui/           # User interface
│   ├── config/       # Configuration
│   └── tests/        # Test suite
├── scripts/          # Development scripts
└── docs/            # Documentation
```

### Key Files
- `src/main.py`: Application entry point
- `src/processes/monitor.py`: Process monitoring
- `src/ui/process_list.py`: Process list UI
- `src/config/settings.py`: Configuration management

### Development Workflow
1. Create feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes and run checks:
   ```bash
   ./scripts/run_checks.sh
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Submit pull request

### Common Development Tasks

#### Run Specific Tests
```bash
# Run specific test file
pytest tests/test_process_monitor.py

# Run specific test
pytest tests/test_process_monitor.py::test_init
```

#### Format Code
```bash
# Format all code
./scripts/lint.sh

# Format specific file
black src/main.py
```

#### Type Checking
```bash
# Check all files
mypy src

# Check specific file
mypy src/main.py
```

#### Build Package
```bash
python -m build
```

### Debugging

1. Enable debug logging:
   ```bash
   export LOG_LEVEL=DEBUG
   process-dashboard
   ```

2. Check logs:
   ```bash
   tail -f ~/.local/share/process-dashboard/logs/dashboard.log
   ```

3. Use debugger:
   ```python
   import pdb; pdb.set_trace()
   ```

### Configuration

1. User config file:
   ```
   ~/.config/process-dashboard/config.json
   ```

2. Environment variables:
   - `PROCESS_DASHBOARD_THEME`
   - `PROCESS_DASHBOARD_UPDATE_INTERVAL`
   - `PROCESS_DASHBOARD_LOG_LEVEL`

### Adding New Features

1. Update tests:
   ```bash
   # Create new test file
   touch src/tests/test_your_feature.py
   ```

2. Implement feature:
   ```bash
   # Create new module
   touch src/your_feature.py
   ```

3. Update documentation:
   ```bash
   # Update relevant docs
   vim docs/your_feature.md
   ```

### Getting Help

1. Check documentation:
   ```bash
   less docs/README.md
   ```

2. Run verify script:
   ```bash
   ./scripts/verify_setup.sh
   ```

3. Enable debug logging:
   ```bash
   export LOG_LEVEL=DEBUG
   ```

### Best Practices

1. Always write tests first
2. Keep documentation updated
3. Run all checks before committing
4. Follow type hints
5. Use proper error handling
6. Maintain logging

### Performance Considerations

1. Use async operations where appropriate
2. Implement caching for expensive operations
3. Profile code with cProfile
4. Monitor memory usage
5. Optimize database queries

### Security

1. Never store sensitive data
2. Validate all user input
3. Use proper permissions
4. Handle errors securely
5. Follow security guidelines

