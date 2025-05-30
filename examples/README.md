# Example Code

## Available Examples

- `custom_monitor.py`: Custom process monitoring
- `resource_alerts.py`: Resource monitoring alerts
- `plugin_example.py`: Plugin system example

## Running Examples

```bash
# Run with Python
python examples/custom_monitor.py

# Run with Docker
docker-compose -f docker-compose.dev.yml run --rm dashboard python examples/custom_monitor.py
```

## Creating New Examples

1. Create new Python file in appropriate subdirectory
2. Add comprehensive docstrings
3. Include test cases
4. Update this README
