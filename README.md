# duk
TurningBull Data Utility Knife

A Python CLI tool for downloading financial market data and performing data preprocessing.

## Installation

### From Source (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/rtrimble13/duk.git
   cd duk
   ```

2. Install in development mode:
   ```bash
   make install
   ```

3. Verify installation:
   ```bash
   duk --help
   ```

### From PyPI (Coming Soon)

```bash
pip install duk
```

## Development

### Available Commands

- `make install` - Install the package in development mode
- `make test` - Run unit tests
- `make clean` - Clean build artifacts
- `make lint` - Run linting checks
- `make format` - Format code with black
- `make build` - Build distribution packages
- `make publish` - Publish to PyPI (requires credentials)

### Building Distribution Packages

To create distributable packages:

```bash
make build
```

This creates both wheel and source distributions in the `dist/` directory.

### Testing

Run the complete test suite:

```bash
make test
```

## Usage

See the [documentation](doc/README.md) for detailed usage instructions.

Quick example:
```bash
# Download latest Treasury rates
duk tr

# Get help for specific commands
duk tr --help
```
