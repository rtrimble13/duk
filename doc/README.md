# duk Documentation

This directory contains documentation for the duk CLI tool and its subprograms.

## Available Documentation

### CLI Commands

- [Price History (`duk ph`)](price_history.md) - Download historical security price data
- [Treasury Rates (`duk tr`)](treasury_rates.md) - Download U.S. Treasury par yield curve rates
- [List Data (`duk ls`)](list_data.md) - List available data sources

### Python API

- [API Reference](api.md) - Use duk as a Python module

### Other

- [Configuration](configuration.md) - Configuration file format and options
- [Packaging Guide](packaging.md) - Build and distribute the duk package

## Quick Start

1. Install duk:
   ```bash
   make install
   ```

2. Get help:
   ```bash
   duk --help
   duk tr --help
   ```

3. Download latest treasury rates:
   ```bash
   duk tr
   ```

## Development

- Run tests: `make test`
- Format code: `make format`
- Run linting: `make lint`
- Clean build artifacts: `make clean`