# duk - Market Data CLI Tool

`duk` is a Python-based CLI tool for downloading market and financial data through various APIs. It provides both a command-line interface and a Python library API for data preprocessing and transformations.

## Features

- Download security price history from Financial Modeling Prep (FMP) API
- Support for both CLI and library usage
- Configurable through `~/.dukrc` file
- Logging to both file and stdout
- Pandas-based data processing
- Multiple output formats (table, CSV, JSON)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/rtrimble13/duk.git
cd duk

# Install using make
make install
```

### Using pip

```bash
pip install duk
```

## Configuration

Create a configuration file at `~/.dukrc`:

```ini
[api]
fmp_api_key = YOUR_FMP_API_KEY_HERE

[logging]
log_level = INFO
log_file = ~/.local/share/duk/duk.log
console_logging = true

[output]
output_dir = ./var
default_limit = 5
```

Alternatively, you can set the `FMP_API_KEY` environment variable:

```bash
export FMP_API_KEY=your_api_key_here
```

## Usage

### Command Line Interface

#### Price History (ph) Command

Download security price history:

```bash
# Basic usage (returns 5 most recent data points)
duk ph IBM

# Specify limit
duk ph IBM --limit 10

# Date range
duk ph IBM --from-date 2024-01-01 --to-date 2024-01-31

# Specific fields
duk ph IBM --fields date close volume

# Output format
duk ph IBM --output-format csv
duk ph IBM --output-format json
```

The symbol is case-insensitive, so `duk ph ibm`, `duk ph IBM`, and `duk ph IbM` all work.

### Library API

Use `duk` as a Python library:

```python
from duk import get_price_history

# Get price history
df = get_price_history('IBM', limit=10)
print(df)

# With date range
df = get_price_history(
    'IBM',
    from_date='2024-01-01',
    to_date='2024-01-31'
)

# Custom fields
df = get_price_history(
    'IBM',
    fields=['date', 'close', 'volume']
)
```

## Development

### Setup Development Environment

```bash
make build
```

### Run Tests

```bash
make test
```

### Linting

```bash
make fmt
```

### Build Distribution

```bash
make dist
```

## Project Structure

```
duk/
├── src/duk/          # Source code
│   ├── __init__.py   # Package initialization
│   ├── cli.py        # CLI interface
│   ├── config.py     # Configuration management
│   ├── logger.py     # Logging setup
│   └── ph.py         # Price history module
├── test/             # Unit tests
├── doc/              # Documentation
├── etc/              # Configuration templates
└── var/              # Default output directory
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass (`make test`)
2. Code is formatted (`make fmt`)
3. New features include unit tests
4. Documentation is updated

## Author

Ryan Trimble (rtrimble13@gmail.com)
