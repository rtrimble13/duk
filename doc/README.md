# duk Documentation

This directory contains documentation for the duk CLI tool and its subprograms.

## Available Documentation

- [Treasury Rates (`duk tr`)](treasury_rates.md) - Download U.S. Treasury par yield curve rates

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