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

### Conda Environment Setup (Recommended)

For local development using miniconda3/anaconda:

1. Set up the development environment:
   ```bash
   make dev
   ```

2. Activate the environment:
   ```bash
   conda activate duk
   ```

3. Install duk in development mode:
   ```bash
   pip install -e .
   ```

4. Run tests:
   ```bash
   make test
   ```

### Alternative Setup (pip)

Alternatively, you can use pip directly:

1. Install in development mode:
   ```bash
   make install
   ```

### Available Commands

- `make dev` - Create/update conda development environment
- `make install` - Install the package in development mode
- `make test` - Run unit tests
- `make clean` - Clean build artifacts
- `make lint` - Run linting checks
- `make format` - Format code with black
- `make build` - Build distribution packages
- `make publish` - Publish to PyPI (requires credentials)

### Conda Environment Management

Additional conda-specific commands:

- `make env-create` - Create conda environment from environment.yml
- `make env-update` - Update existing conda environment
- `make env-export` - Export current environment to environment.yml
- `make env-remove` - Remove the conda development environment

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
