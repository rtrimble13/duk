# duk

A CLI tool and library for downloading markets and financial data through various APIs.

## Installation

### Using pip

```bash
pip install tb-duk
```

### From source

```bash
git clone https://github.com/rtrimble13/duk.git
cd duk
make install
```

## Configuration

duk uses a configuration file located at `~/.dukrc`. A template configuration file is provided in `etc/dukrc`.

To set up your configuration:

```bash
cp etc/dukrc ~/.dukrc
# Edit ~/.dukrc with your preferred settings
```

### Configuration Options

- **[api] section**
  - `fmp_key`: API key for Financial Modeling Prep
    - Can also be set via the `FMP_API_KEY` environment variable (takes precedence over config file)

- **[general] section**
  - `default_output_dir`: Default directory for output files (default: `var/duk`)
  - `default_output_type`: Default output format, either `csv` or `json` (default: `csv`)
  - `log_level`: Logging level - `debug`, `info`, `warning`, `error`, or `critical` (default: `info`)
  - `log_dir`: Directory for log files (default: `var/duk/log`)

## Usage

### CLI Usage

```bash
# Display help
duk --help

# Use with custom config file
duk --config /path/to/config --help
```

### Library Usage

duk can be used as a Python library to fetch financial data programmatically.

#### Get Historical Price Data

```python
from duk import get_price_history

# Get daily price data for a date range
df = get_price_history(
    api_key="your_api_key",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

print(df.head())
```

For more examples and detailed documentation, see [doc/get_price_history.md](doc/get_price_history.md).

## Development

### Prerequisites

- Python 3.9 or higher
- conda (optional, for environment management)

### Setup Development Environment

```bash
# Using make (recommended)
make build

# Or using pip directly
pip install -e .[dev]
```

### Running Tests

```bash
make test
```

### Linting

```bash
make fmt
```

### Building Documentation

```bash
make doc
```

### Creating Distribution

```bash
make dist
```

## Project Structure

- `src/duk/`: Source code
- `test/`: Unit tests
- `doc/`: Documentation
- `etc/`: Configuration templates
- `var/`: Default output and log directory

## License

MIT License - see LICENSE file for details.
