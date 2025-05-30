# Documentation Directory

## Contents

- `api/`: API documentation
- `examples/`: Usage examples
- `guides/`: User and developer guides
- `images/`: Screenshots and diagrams

## Key Documents

- `installation.md`: Installation guide
- `configuration.md`: Configuration guide
- `development.md`: Development guide
- `api/index.html`: API reference

## Generating Documentation

```bash
# Generate API documentation
pdoc --html --output-dir docs/api src/

# Build user guides (if using Sphinx)
cd docs && make html
```
