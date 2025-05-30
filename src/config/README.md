# Configuration Management

## Components

- `settings.py`: Configuration handling
- `logging_config.py`: Logging setup
- `defaults.py`: Default values

## Usage

```python
from config.settings import DashboardConfig

config = DashboardConfig()
config.load()
```

## Configuration Files

Default locations:
- Linux: ~/.config/process-dashboard/
- macOS: ~/Library/Application Support/process-dashboard/
- Windows: %APPDATA%\process-dashboard\
