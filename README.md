# Process Dashboard

A Terminal User Interface (TUI) system process management tool with a Matrix-inspired theme. Monitor and manage your system processes in style with real-time updates and configurable displays.

## Features

- 🖥️ Real-time process monitoring with detailed information
- 📊 System resource usage visualization
- 💾 Disk usage tracking and display
- 🎨 Matrix-inspired theme with customizable colors
- ⚙️ Configurable update intervals and layout options
- 🔧 User-friendly TUI with keyboard shortcuts
- 📱 Responsive grid-based layout
- 🔍 Process filtering and sorting capabilities
- 💻 Cross-platform support (Linux, macOS, Windows)

## Installation

1. Ensure you have Python 3.8 or higher installed:
   ```bash
   python --version
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/process_dashboard.git
   cd process_dashboard
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the dashboard:
   ```bash
   python src/main.py
   ```

2. Keyboard shortcuts:
   - `q`: Quit the application
   - `r`: Refresh all displays manually
   - `c`: Toggle configuration panel
   - `Arrow keys`: Navigate through panels
   - `Tab`: Switch between interactive elements

3. Menu options:
   - File: Save/load configurations
   - View: Adjust display layout
   - Processes: Process management options
   - Configuration: Access settings
   - Help: View keyboard shortcuts and help

## Configuration

The dashboard can be configured through the YAML configuration file located at:
```
~/.config/process_dashboard/config.yaml
```

### Available Settings

```yaml
theme:
  background_color: "#000000"
  text_color: "#00FF00"
  accent_color: "#008000"
  border_color: "#004000"
  matrix_effect: true

layout:
  show_process_list: true
  show_resource_monitor: true
  show_disk_usage: true
  show_config_panel: true
  grid_rows: 2
  grid_columns: 2

updates:
  process_update_interval: 1.0
  resource_update_interval: 2.0
  disk_update_interval: 5.0
```

## Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

4. Check code quality:
   ```bash
   black .
   pylint src/
   mypy src/
   ```

### Project Structure

```
process_dashboard/
├── src/
│   ├── config/
│   │   └── settings.py
│   ├── processes/
│   │   └── monitor.py
│   ├── ui/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   └── main.py
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

## Screenshots

[Coming Soon]

*Screenshot placeholder: Display of the matrix-themed process dashboard with multiple panes showing system information.*

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 Process Dashboard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

