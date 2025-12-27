# duk Documentation Index

Welcome to the duk documentation! This index provides links to all available documentation for the duk CLI tool and Python library.

## Quick Start

- [README](../README.md) - Project overview, installation, and basic usage
- [CONTRIBUTING](../CONTRIBUTING.md) - Guide for contributing to the project
- [CHANGELOG](../CHANGELOG.md) - Version history and release notes

## CLI Commands

The duk CLI provides several subcommands for interacting with financial data APIs:

### ls - List Securities and Market Information

- [ls Command Documentation](ls_command.md) - List actively trading securities, sectors, and industries

**Usage**: `duk ls [OPTIONS]`

**Examples**:
- List all actively trading securities
- Get all market sectors
- Get all industries

### ph - Historical Price Data

- [ph Command Documentation](ph_command.md) - Retrieve historical price data for securities

**Usage**: `duk ph SYMBOL [OPTIONS]`

**Examples**:
- Get daily price data for a date range
- Get weekly/monthly aggregated data
- Export price data to CSV or JSON

### yc - Yield Curve Data

- [yc Command Documentation](yc_command.md) - Retrieve Treasury yield curve data

**Usage**: `duk yc [OPTIONS]`

**Examples**:
- Get current yield curve
- Get historical yield curve for a specific date
- Export yield curve data

## Python Library API

The duk library can be used programmatically in Python applications:

### get_price_history Function

- [get_price_history Documentation](get_price_history.md) - Detailed API reference for retrieving historical price data

**Key Features**:
- Flexible date range specification
- Multiple frequency options (daily, weekly, monthly, quarterly, semi-annual, annual)
- Field selection for custom data views
- Pandas DataFrame output for easy analysis

### get_yield_curve Function

- [get_yield_curve Documentation](get_yield_curve.md) - API reference for yield curve data

**Key Features**:
- Current and historical yield curves
- Treasury data for various maturities
- DataFrame output format

### return_utils Module

- [return_utils Documentation](return_utils.md) - Comprehensive return calculation utilities

**Key Features**:
- Simple and log returns
- Cumulative and annualized returns
- Dividend-adjusted and excess returns
- Multi-period return calculations
- Full support for pandas Series and DataFrame

## Configuration

### Configuration File

The duk tool uses a configuration file located at `~/.dukrc`. See the [README](../README.md#configuration) for details on:

- API key configuration
- Default output settings
- Logging configuration
- Output directory settings

### Environment Variables

Alternative to configuration files:

- `FMP_API_KEY` - Financial Modeling Prep API key (overrides config file)

## Project Structure

```
duk/
├── src/duk/           # Source code
│   ├── api/          # API client modules
│   ├── cli/          # CLI command implementations
│   ├── core/         # Core functionality
│   └── utils/        # Utility functions
├── test/             # Unit tests
├── doc/              # Documentation (you are here!)
├── etc/              # Configuration templates
└── var/              # Default output and logs
```

## Development

For developers contributing to duk:

- [CONTRIBUTING](../CONTRIBUTING.md) - Contribution guidelines and development workflow
- [CODE_OF_CONDUCT](../CODE_OF_CONDUCT.md) - Community standards and expectations
- [SECURITY](../SECURITY.md) - Security policy and vulnerability reporting

### Development Workflow

```bash
make build    # Set up development environment
make test     # Run unit tests
make fmt      # Apply linting and formatting
make doc      # Build documentation
make dist     # Create distribution package
```

## Community Standards

- [Code of Conduct](../CODE_OF_CONDUCT.md) - Guidelines for respectful collaboration
- [Security Policy](../SECURITY.md) - How to report security vulnerabilities
- [License](../LICENSE) - MIT License terms

## Support and Resources

### Getting Help

- Check the documentation in this index
- Search existing [GitHub Issues](https://github.com/rtrimble13/duk/issues)
- Open a new issue for bug reports or feature requests

### API Providers

duk currently integrates with:

- [Financial Modeling Prep (FMP)](https://financialmodelingprep.com/) - For price history and company data

### External Resources

- [pandas Documentation](https://pandas.pydata.org/docs/) - For DataFrame manipulation
- [Python Click](https://click.palletsprojects.com/) - CLI framework used by duk

## Examples and Tutorials

### Common Use Cases

1. **Downloading historical data for multiple stocks**
   - See [get_price_history.md](get_price_history.md#example-13-compare-multiple-stocks---close-prices-only)

2. **Getting list of tradable securities**
   - See [ls_command.md](ls_command.md#example-1-get-actively-trading-securities)

3. **Exporting data to files**
   - See [ph_command.md](ph_command.md) for file output examples

4. **Data analysis workflows**
   - See [get_price_history.md](get_price_history.md#example-10-data-analysis-example)

## Version Information

Current stable version: **0.2.0**

- Python support: 3.9, 3.10, 3.11, 3.12, 3.13
- License: MIT
- Status: Alpha

See [CHANGELOG](../CHANGELOG.md) for version history and updates.

## Contributing

We welcome contributions! Please see:

1. [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
2. [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) - Community standards
3. [GitHub Issues](https://github.com/rtrimble13/duk/issues) - Current issues and feature requests

## License

duk is released under the MIT License. See [LICENSE](../LICENSE) for full details.

---

**Last Updated**: December 2024

For the latest documentation, please visit the [GitHub repository](https://github.com/rtrimble13/duk).
