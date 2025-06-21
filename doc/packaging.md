# Packaging Guide

This document describes how to build and distribute the `duk` package for both PyPI and conda.

## Prerequisites

The project uses modern Python packaging standards:
- `pyproject.toml` for project configuration
- `src/` layout for source code
- Setuptools with PEP 517/518 support
- Conda recipe for conda-forge distribution

## Building Packages

### PyPI Distribution

#### Method 1: Using make dist (Recommended)

```bash
# Install development dependencies
make install

# Build distribution packages with automatic fallback
make dist
```

#### Method 2: Using the build module

```bash
# Install development dependencies (includes build tool)
make install

# Build distribution packages
make build
```

#### Method 3: Standalone build script (Fallback)

If the standard build method fails (e.g., due to network issues), use the standalone build script:

```bash
make build-standalone
```

This method:
- Creates a temporary `setup.py` file
- Uses setuptools directly to build packages
- More resilient to network issues during CI/CD

### Conda Distribution

#### Building Conda Packages

```bash
# Install conda-build (if not already installed)
conda install conda-build

# Build conda package
make conda-build
```

#### Alternative Manual Build

```bash
# Build conda package manually
conda-build conda-recipe/
```

### Built Packages

#### PyPI Packages

All methods create distribution packages in the `dist/` directory:
- `duk-X.Y.Z-py3-none-any.whl` - Universal wheel
- `duk-X.Y.Z.tar.gz` - Source distribution

#### Conda Packages

Conda packages are built in the conda-build output directory (typically `~/miniconda3/conda-bld/`):
- `duk-X.Y.Z-py_0.tar.bz2` - Conda package

## Installation Testing

### PyPI Packages

Test that built packages can be installed:

```bash
# Test wheel installation
pip install dist/duk-*.whl

# Test source distribution installation  
pip install dist/duk-*.tar.gz

# Verify CLI works
duk --help
```

### Conda Packages

Test conda package installation:

```bash
# Install from local build
conda install --use-local duk

# Verify CLI works
duk --help
```

## Publishing

### Publishing to PyPI

#### Manual Publishing

```bash
# Install twine if not already installed
pip install twine

# Check package
twine check dist/*

# Upload to PyPI (requires credentials)
make publish
# or
twine upload dist/*
```

### Publishing to Conda-Forge

For conda-forge distribution:

1. Fork the [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes) repository
2. Create a new recipe in `recipes/duk/meta.yaml` based on the `conda-recipe/meta.yaml` 
3. Submit a pull request
4. Once merged, the package will be available via `conda install -c conda-forge duk`

### Automated Publishing

The project includes a GitHub Actions workflow (`.github/workflows/build-test.yml`) that:

1. **Tests** the package on multiple Python versions (3.8-3.12)
2. **Builds** distribution packages using both methods
3. **Publishes** to PyPI automatically on GitHub releases

To set up automated publishing:
1. Create a PyPI API token
2. Add it as `PYPI_API_TOKEN` secret in GitHub repository settings
3. Create a GitHub release to trigger publication

## Package Structure

The package follows Python packaging best practices:

```
duk/
├── src/duk/              # Source code
│   ├── __init__.py       # Version info
│   ├── main.py           # CLI entry point
│   └── commands/         # Subcommands
├── test/                 # Unit tests
├── doc/                  # Documentation
├── conda-recipe/         # Conda packaging recipe
│   └── meta.yaml         # Conda package configuration
├── pyproject.toml        # Package configuration
├── setup.cfg             # Tool configuration
├── Makefile              # Development commands
└── scripts/build.py      # Standalone build script
```

## Configuration Details

### pyproject.toml

Key configuration sections:
- `[build-system]` - Build backend (setuptools)
- `[project]` - Package metadata and dependencies
- `[project.scripts]` - CLI entry points
- `[project.optional-dependencies]` - Development dependencies

### Entry Points

The CLI tool is configured as a console script:
```toml
[project.scripts]
duk = "duk.main:main"
```

This creates the `duk` command that calls the `main()` function in `src/duk/main.py`.

## Troubleshooting

### Build Failures

If `make build` fails:
1. Try the standalone method: `make build-standalone`
2. Check network connectivity
3. Verify all dependencies are installed: `make install`

### Import Errors

If the package can't be imported after installation:
1. Check Python path: `python -c "import sys; print(sys.path)"`
2. Verify installation: `pip show duk`
3. Reinstall in development mode: `make install`

### Version Conflicts

The version is defined in `src/duk/__init__.py` and must match `pyproject.toml`:
```python
__version__ = "0.1.0"
```