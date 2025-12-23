# Contributing to duk

Thank you for your interest in contributing to duk! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** including code snippets or command-line examples
- **Describe the behavior you observed** and what you expected to see
- **Include version information** (Python version, duk version, OS)
- **Include relevant logs** from the log directory (`var/duk/log/`)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the proposed enhancement
- **Explain why this enhancement would be useful** to most duk users
- **List any alternative solutions** you've considered
- **Include examples** of how the feature would be used

### Pull Requests

We actively welcome your pull requests! Please follow these guidelines:

1. **Fork the repository** and create your branch from `main`
2. **Follow the development workflow** outlined below
3. **Write or update tests** for your changes
4. **Update documentation** if you're changing functionality
5. **Ensure all tests pass** before submitting
6. **Follow the code standards** outlined below
7. **Write a clear commit message** describing your changes

## Development Workflow

### Prerequisites

- Python 3.9 or higher
- conda (optional, for environment management)

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/duk.git
cd duk

# Set up the development environment
make build

# Or using pip directly
pip install -e .[dev]
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Run tests**:
   ```bash
   make test
   ```

4. **Run linting**:
   ```bash
   make fmt
   ```

5. **Build documentation** (if applicable):
   ```bash
   make doc
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** on GitHub

## Code Standards

### General Guidelines

- Follow Python best practices and idiomatic patterns
- Maintain existing code structure and organization
- Use dependency injection patterns where appropriate
- Write clear, self-documenting code
- Add comments only when necessary to explain complex logic

### Required Before Each Commit

1. **Write unit tests** for each new feature using the pytest framework
2. **Ensure all tests pass**: `make test`
3. **Apply linting**: `make fmt`
4. **Update documentation** with usage examples when adding features
5. **Add logging** for all new functionality

### Testing Guidelines

- Use table-driven unit tests when possible
- Test both success and error cases
- Mock external API calls to avoid dependencies
- Aim for high test coverage

### Documentation Guidelines

- Update relevant documentation in the `doc/` directory
- Include usage examples for new features
- Follow the existing documentation style and format
- Update `doc/index.md` if adding new documentation files

### CLI Subprogram Guidelines

The `duk` CLI tool consists of multiple subprograms. When adding a new subprogram:

- **Command signature**: `duk <subprogram> [positional arguments] [optional arguments]`
- **Make it independent**: Treat each subprogram as a standalone module
- **Consistent options**: Use consistent option names across subprograms when possible
- **Documentation**: Create a dedicated documentation file in `doc/<subprogram>_command.md`

### Common Optional Arguments

For consistency, use these standard options when applicable:

- `-o, --output PATH`: Output file path
- `-q, --quiet`: Suppress output to stdout
- `-v, --verbose`: Enable verbose/debug logging
- `-n, --limit INTEGER`: Limit number of records
- `--csv`: Output as CSV format
- `--json`: Output as JSON format

## Repository Structure

```
duk/
├── src/            # Source code
├── test/           # Unit tests
├── doc/            # Documentation
├── etc/            # Configuration templates
├── var/            # Default output and log directory
├── Makefile        # Build and development commands
└── pyproject.toml  # Project configuration
```

## Development Commands

- `make build`: Set up project in conda environment
- `make install`: Install project locally
- `make test`: Run unit tests
- `make fmt`: Apply linting and formatting
- `make doc`: Build documentation
- `make dist`: Create distribution files
- `make clean`: Remove installed files and builds

## Style Guide

### Python Style

- **Line length**: 88 characters (Black default)
- **Imports**: Sorted using isort with Black profile
- **Docstrings**: Use clear, concise docstrings for public APIs
- **Type hints**: Use type hints for function signatures
- **Naming conventions**:
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Logging

- Use the standard Python logging module
- Include appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log at INFO level for normal operations
- Log at DEBUG level for detailed diagnostic information

## Getting Help

If you need help with your contribution:

- Check the [documentation](doc/index.md)
- Open an issue with your question
- Review existing issues and pull requests

## License

By contributing to duk, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to duk! 🎉
