# duk

A CLI tool and library for downloading financial market data and performing data preprocessing.

## Installation

### Using pip

```bash
pip install duk
```

### From source

```bash
git clone https://github.com/rtrimble13/duk.git
cd duk
make install
```

### Using conda

```bash
conda env create -f environment.yaml
conda activate duk
make install
```

## Configuration

Copy the template configuration file and edit it with your settings:

```bash
cp etc/dukrc ~/.dukrc
```

Edit `~/.dukrc` and add your FMP API key:

```ini
[api]
fmp_api_key = YOUR_FMP_API_KEY_HERE
```

Get your API key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/).

## Usage

### Price History (ph) Command

Download security price history from FMP:

```bash
# Get 5 most recent data points for IBM
duk ph IBM

# Get 10 most recent data points
duk ph AAPL --limit 10

# Get data for a specific date range
duk ph MSFT --from-date 2023-01-01 --to-date 2023-12-31

# Save output to file
duk ph IBM --output ibm_history.csv --format csv

# Specify fields to display
duk ph IBM --fields date,close,open,high,low,volume
```

### Using as a Library

```python
from duk.api import get_price_history

# Get price history
df = get_price_history(
    symbol="IBM",
    api_key="your_api_key",
    limit=5
)

print(df)
```

## Development

### Building

```bash
make build
```

### Running Tests

```bash
make test
```

### Linting

```bash
make fmt
```

### Building Distribution

```bash
make dist
```

## License

MIT License. See LICENSE file for details.
