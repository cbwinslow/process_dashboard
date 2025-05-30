# Process Monitoring Module

## Components

- `monitor.py`: Core process monitoring
- `controller.py`: Process control operations
- `history.py`: Process history tracking

## Usage

```python
from processes.monitor import ProcessMonitor

monitor = ProcessMonitor()
processes = monitor.get_process_list()
```

## Development

See tests/test_process_monitor.py for usage examples.
