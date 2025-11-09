# duk Python API

`duk` can be used as a Python module to programmatically access financial data. The API functions provide the same functionality as the CLI commands but return data as pandas DataFrames for easy manipulation and analysis in Python programs.

## Installation

Install duk as a Python package:

```bash
pip install duk
```

Or install from source:

```bash
git clone https://github.com/rtrimble13/duk.git
cd duk
pip install -e .
```

## Configuration

The API functions use the same configuration system as the CLI tool. Configure your API keys in `~/.dukrc`:

```toml
[api_keys]
fmp_api_key = "your-fmp-api-key-here"
```

Alternatively, set environment variables:

```bash
export FMP_API_KEY="your-fmp-api-key-here"
```

See [configuration.md](configuration.md) for more details on configuration options.

## API Functions

### ph() - Price History

Download historical security price data.

```python
import duk

df = duk.ph(
    tickers,                    # str or list of str
    start_date=None,            # str in 'YYYY-MM-DD' format
    end_date=None,              # str in 'YYYY-MM-DD' format
    num_records=None,           # int
    fields=None,                # list of str
    frequency='daily',          # str
    include_dividends=False,    # bool
    include_splits=False,       # bool
    calculate_adjusted=False,   # bool
    use_cache=True             # bool
)
```

#### Parameters

- **tickers** (str or list): Single ticker symbol (e.g., 'AAPL') or list of ticker symbols
- **start_date** (str, optional): Start date in 'YYYY-MM-DD' format
- **end_date** (str, optional): End date in 'YYYY-MM-DD' format
- **num_records** (int, optional): Number of records to return (default: 5 if no dates specified)
- **fields** (list, optional): List of fields to include. Valid options:
  - 'open', 'high', 'low', 'close', 'volume', 'adjusted_close', 'dividend', 'split'
  - If None, defaults to ['close']
- **frequency** (str, optional): Data frequency (default: 'daily')
  - Valid options: 'daily', 'weekly', 'monthly', 'quarterly', 'semiannual', 'annual'
- **include_dividends** (bool): Include dividend data (default: False)
- **include_splits** (bool): Include split data (default: False)
- **calculate_adjusted** (bool): Calculate adjusted close prices (default: False)
- **use_cache** (bool): Use cached data if available (default: True)

#### Returns

pandas.DataFrame with columns:
- **symbol**: Stock symbol
- **date**: Date of the record (datetime)
- Additional columns based on the 'fields' parameter

#### Examples

##### Basic Usage

```python
import duk

# Get latest 5 days of close prices for AAPL
df = duk.ph('AAPL')
print(df)
```

Output:
```
  symbol       date  close
0   AAPL 2023-12-01  152.0
1   AAPL 2023-11-30  150.0
...
```

##### Multiple Tickers

```python
# Get data for multiple tickers
df = duk.ph(['AAPL', 'MSFT', 'GOOGL'])
print(df)
```

##### OHLC Data

```python
# Get open, high, low, close data
df = duk.ph('AAPL', fields=['open', 'high', 'low', 'close'])
print(df)
```

Output:
```
  symbol       date   open   high    low  close
0   AAPL 2023-12-01  150.0  155.0  148.0  152.0
...
```

##### Date Range

```python
# Get data for specific date range
df = duk.ph('AAPL', start_date='2023-01-01', end_date='2023-12-31')
print(f"Retrieved {len(df)} days of data")
```

##### With Volume

```python
# Get close and volume data
df = duk.ph('AAPL', fields=['close', 'volume'])
print(df)
```

##### Frequency Aggregation

```python
# Get weekly aggregated data
df = duk.ph('AAPL', 
           start_date='2023-01-01', 
           end_date='2023-12-31',
           frequency='weekly',
           fields=['open', 'high', 'low', 'close', 'volume'])
print(df)
```

##### With Dividends and Splits

```python
# Get data with dividend and split information
df = duk.ph('AAPL', 
           start_date='2023-01-01', 
           end_date='2023-12-31',
           fields=['close', 'dividend', 'split'],
           include_dividends=True,
           include_splits=True)
print(df)
```

##### Adjusted Prices

```python
# Get adjusted close prices (accounts for dividends and splits)
df = duk.ph('AAPL', 
           start_date='2023-01-01', 
           end_date='2023-12-31',
           fields=['close', 'adjusted_close'],
           calculate_adjusted=True)
print(df)
```

##### Disable Cache

```python
# Force fresh data download (bypass cache)
df = duk.ph('AAPL', use_cache=False)
print(df)
```

#### Error Handling

The `ph()` function raises exceptions for error conditions:

```python
import duk

try:
    df = duk.ph('INVALID_TICKER')
except RuntimeError as e:
    print(f"Error: {e}")
    
try:
    df = duk.ph('AAPL', fields=['invalid_field'])
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

## Advanced Usage

### Integration with pandas

The API returns pandas DataFrames, making it easy to integrate with data analysis workflows:

```python
import duk
import matplotlib.pyplot as plt

# Get price data
df = duk.ph('AAPL', 
           start_date='2023-01-01', 
           end_date='2023-12-31',
           fields=['close'])

# Calculate returns
df['returns'] = df['close'].pct_change()

# Plot
df.plot(x='date', y='close', title='AAPL Close Price')
plt.show()
```

### Combining Multiple Data Sources

```python
import duk
import pandas as pd

# Get data for multiple tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
df = duk.ph(tickers, 
           start_date='2023-01-01', 
           end_date='2023-12-31',
           fields=['close'])

# Pivot for analysis
pivot_df = df.pivot(index='date', columns='symbol', values='close')
print(pivot_df.head())

# Calculate correlation matrix
corr_matrix = pivot_df.pct_change().corr()
print(corr_matrix)
```

### Batch Processing

```python
import duk
from pathlib import Path

# Process list of tickers
tickers_file = Path('tickers.txt')
with open(tickers_file) as f:
    tickers = [line.strip() for line in f]

# Download data for all tickers
all_data = []
for ticker in tickers:
    try:
        df = duk.ph(ticker, 
                   start_date='2023-01-01', 
                   end_date='2023-12-31')
        all_data.append(df)
        print(f"Downloaded data for {ticker}")
    except RuntimeError as e:
        print(f"Failed to download {ticker}: {e}")

# Combine all data
combined_df = pd.concat(all_data, ignore_index=True)
```

## Future API Functions

Additional API functions will be added to mirror other duk CLI commands:

- `duk.tr()` - Treasury rates data
- `duk.ls()` - List available data

## See Also

- [CLI Documentation](README.md) - Command-line interface usage
- [Configuration](configuration.md) - Configuration file format
- [Price History CLI](price_history.md) - Detailed CLI usage for price history
