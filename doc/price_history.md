# Price History Downloader (`duk ph`)

The `duk ph` subprogram downloads historical security price data using the Financial Modeling Prep (FMP) API.

Note: An FMP API key is required. You can provide the key in one of two ways:
1. Set the `FMP_API_KEY` environment variable (recommended for CI/automated environments)
2. Place your key in `~/.dukrc` configuration file

## Overview

The price history downloader retrieves historical price data for securities, with support for:

- Multiple ticker symbols as arguments
- Various date range options and record counts
- Flexible output field combinations (default: close only)
- Dividend and stock split data integration
- Adjusted price calculations
- Frequency aggregation (daily, weekly, monthly, quarterly, semiannual, annual)
- CSV and JSON output formats
- Combined or separate output for multiple tickers

## Basic Usage

```bash
# Get latest 5 days of close prices for AAPL
duk ph AAPL

# Get last 30 records
duk ph AAPL -n 30

# Get specific date range
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

## Ticker Input Options

### Single Ticker
```bash
# Download data for Apple Inc.
duk ph AAPL

# Ticker symbols are case-insensitive (converted to uppercase internally)
duk ph aapl
```

### Multiple Tickers
```bash
# Download data for multiple tickers (separate outputs)
duk ph AAPL MSFT GOOGL

# Download data for multiple tickers (combined into one output)
duk ph AAPL MSFT GOOGL --combine
```

## Date Options

### Specific Date Range
```bash
# Download data for a specific date range
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Short form
duk ph AAPL -s 2023-01-01 -e 2023-12-31
```

### Number of Records
```bash
# Download last 10 records
duk ph AAPL --num-records 10
duk ph AAPL -n 10

# Download 30 records starting from a specific date
duk ph AAPL --start-date 2023-01-01 -n 30

# Download 30 records ending at a specific date
duk ph AAPL --end-date 2023-12-31 -n 30
```

**Note**: Using both `--start-date` and `--end-date` invalidates the `--num-records` parameter.

## Output Field Combinations

### Default Output (Close Only)
```bash
# Returns close prices only (default behavior)
duk ph AAPL
```

### OHLC Output
```bash
# Returns Open, High, Low, Close prices
duk ph AAPL --ohlc
```

### Volume Data
```bash
# Add volume to close (default)
duk ph AAPL --vol

# Add volume to OHLC
duk ph AAPL --ohlc --vol
```

### Remove Close from Output
```bash
# Get Open, High, Low (without close)
duk ph AAPL --ohlc --no-close

# Get adjusted close only (without regular close)
duk ph AAPL --adj --no-close
```

### Special Data Fields

#### Adjusted Prices
```bash
# Include adjusted close prices (factors in dividends and splits)
duk ph AAPL --adj

# Adjusted prices only (no regular close)
duk ph AAPL --adj --no-close

# OHLC with adjusted close
duk ph AAPL --ohlc --adj
```

#### Dividend Data
```bash
# Include dividend payments
duk ph AAPL --div

# Close and dividends
duk ph AAPL --div

# Dividends only (no close)
duk ph AAPL --div --no-close

# OHLC with dividends
duk ph AAPL --ohlc --div
```

#### Stock Split Data
```bash
# Include stock split ratios
duk ph AAPL --split

# Close and splits
duk ph AAPL --split

# Splits only (no close)
duk ph AAPL --split --no-close

# OHLC with splits
duk ph AAPL --ohlc --split
```

#### Combined Adjustments
```bash
# Include adjusted prices with dividend and split data
duk ph AAPL --adj --div --split

# Only special fields, no price data
duk ph AAPL --adj --div --split --no-close
```

## Frequency Aggregation

### Available Frequencies
- `daily` (default) - Raw daily data from FMP
- `weekly` - Aggregated to weekly intervals
- `monthly` - Aggregated to monthly intervals  
- `quarterly` - Aggregated to quarterly intervals
- `semiannual` - Aggregated to 6-month intervals
- `annual` - Aggregated to yearly intervals

```bash
# Weekly aggregated data
duk ph AAPL --frequency weekly

# Monthly data for the last year
duk ph AAPL -n 365 --frequency monthly

# Quarterly data with adjustments
duk ph AAPL --frequency quarterly --adj
```

### Aggregation Rules
- **Open**: First value in the period
- **High**: Maximum value in the period
- **Low**: Minimum value in the period
- **Close**: Last value in the period
- **Volume**: Sum of volume in the period
- **Dividends**: Sum of dividends in the period
- **Splits**: Last split ratio in the period
- **Adjusted Close**: Last adjusted value in the period

## Output Options

### Output to Console (Default)
```bash
# CSV output to stdout (default)
duk ph AAPL

# Output is always in CSV format to stdout
```

### Output to File
```bash
# Save to CSV file with default naming (price_history_AAPL_YYYYMMDD.csv)
duk ph AAPL --csv

# Save to JSON file with default naming
duk ph AAPL --json

# Save with custom filename
duk ph AAPL --csv --filename my_apple_data
duk ph AAPL --csv -o my_apple_data

# Specify output directory
duk ph AAPL --csv --directory ./data
duk ph AAPL --csv -D ./data

# JSON format to file
duk ph AAPL --json
```

**Note**: You cannot specify both `--csv` and `--json` at the same time.

### Multiple Ticker Output
```bash
# Separate files for each ticker
duk ph AAPL MSFT GOOGL --csv

# Single combined file
duk ph AAPL MSFT GOOGL --csv --combine

# Custom filename with multiple tickers (ticker names will be appended)
duk ph AAPL MSFT --csv -o tech_stocks
# Creates: tech_stocks_AAPL.csv and tech_stocks_MSFT.csv
```

### Output Formats

#### CSV Format (Default)
- First column: ticker symbol
- Second column: date (YYYY-MM-DD format)
- Remaining columns: requested data fields
- Suitable for spreadsheet applications and pandas

#### JSON Format
- Array of objects with ticker, date, and data fields
- Optimized for loading into pandas DataFrames
- Dates in YYYY-MM-DD string format

## Data Structure

### CSV Output Format
```csv
symbol,date,close
AAPL,2023-11-30,150.0
AAPL,2023-12-01,152.0
```

### JSON Output Format
```json
[
  {
    "symbol": "AAPL",
    "date": "2023-11-30",
    "close": 150.0
  },
  {
    "symbol": "AAPL",
    "date": "2023-12-01",
    "close": 152.0
  }
]
```

### Special Fields Output

#### Dividend Fields
- **dividend**: Dividend amount on payment date, 0 on other dates

#### Split Fields  
- **split**: Split ratio on split date (e.g., 2.0 for 2:1 split), 0 on other dates

#### Adjusted Prices
- **adjusted_close**: Close price adjusted for all historical dividends and splits

## Examples

### Basic Usage Examples
```bash
# Latest 5 days close for Apple
duk ph AAPL

# Last 30 records with volume
duk ph AAPL -n 30 --vol

# Last 30 records with OHLC
duk ph AAPL -n 30 --ohlc

# Year 2023 data
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

### File Output Examples
```bash
# Save last 30 days to CSV file
duk ph AAPL -n 30 --csv

# Save custom data to JSON file
duk ph AAPL -n 90 --ohlc --vol --adj --json -o apple_q4

# Save to specific directory
duk ph AAPL --csv --directory ./market_data
```

### Multiple Ticker Examples
```bash
# Multiple tickers, separate outputs to stdout
duk ph AAPL MSFT GOOGL

# Multiple tickers, combined output
duk ph AAPL MSFT GOOGL --combine

# Multiple tickers to separate CSV files
duk ph AAPL MSFT GOOGL --csv

# Multiple tickers to single combined CSV file
duk ph AAPL MSFT GOOGL --csv --combine
```

### Advanced Examples
```bash
# Multiple tickers with adjustments
duk ph AAPL MSFT GOOGL --adj --div --split --csv

# Weekly aggregated data for analysis
duk ph AAPL -n 365 --frequency weekly --ohlc --vol --csv

# Monthly data with all adjustments in JSON format
duk ph AAPL --start-date 2020-01-01 --frequency monthly --adj --div --split --json
```

### Analysis Integration Examples
```bash
# Data for technical analysis (to stdout, redirect to file)
duk ph AAPL -n 200 --ohlc --vol > aapl_data.csv

# Dividend analysis
duk ph KO --start-date 2020-01-01 --div --json -o coca_cola_dividends

# Multi-stock comparison
duk ph AAPL MSFT GOOGL AMZN -n 365 --frequency monthly --json --combine -o tech_stocks
```

## Logging and Verbose Mode

Use the `--verbose` flag to enable detailed logging output to stdout:

```bash
# Run with verbose logging
duk ph AAPL --verbose

# View detailed processing information
duk ph AAPL MSFT GOOGL --verbose --combine --csv
```

Verbose mode displays:
- Processing steps for each ticker
- Number of records downloaded
- Field selection logic
- Data processing details
- File save locations
- Error details for troubleshooting

Regular logging is always written to `var/duk.log`.

## Error Handling

The command provides clear error messages for common issues:

- **Invalid ticker symbols**: "No price data found for symbol XYZ"
- **Network connectivity issues**: "Failed to download price data"
- **Invalid date formats**: Use YYYY-MM-DD format
- **No tickers provided**: "Missing argument 'TICKERS...'"
- **Conflicting options**: "Cannot specify both --csv and --json"
- **Invalid date combinations**: "Cannot specify --num-records with both --start-date and --end-date"

## Caching

By default, the ph command caches API responses to improve performance and reduce API calls. To disable caching and always fetch fresh data:

```bash
# Bypass cache and fetch fresh data
duk ph AAPL --no-cache
```

## Data Source

Data is retrieved from Financial Modeling Prep (FMP) APIs:
- **Price Data**: `https://financialmodelingprep.com/stable/historical-price-eod/full`
- **Dividend Data**: `https://financialmodelingprep.com/stable/dividends`
- **Stock Split Data**: `https://financialmodelingprep.com/stable/splits`

## Integration with Data Analysis

The output format is designed to be easily loaded into pandas DataFrames:

### Python Integration
```python
import pandas as pd
import json

# Load CSV data
df = pd.read_csv('price_history_AAPL_20231201.csv')
df['date'] = pd.to_datetime(df['date'])

# Load JSON data  
with open('price_history_AAPL_20231201.json', 'r') as f:
    data = json.load(f)
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
```

### Analysis Examples
```python
# Calculate daily returns
df['returns'] = df['close'].pct_change()

# Calculate moving averages
df['ma_20'] = df['close'].rolling(20).mean()
df['ma_50'] = df['close'].rolling(50).mean()

# Analyze adjusted vs unadjusted prices
df['adjustment_factor'] = df['adjusted_close'] / df['close']
```

## Migration from Old Interface

If you were using the old `ph` command interface, here are the key changes:

### Changed Options
- `--days` → `--num-records` (or `-n`)
- `-f --filename` → `-o --filename`
- `--output` flag → `--csv` or `--json` flags
- `--format` option → use `--csv` or `--json` instead
- File-based ticker input → multiple ticker arguments

### Changed Defaults
- Default output is now **close only** (was OHLC)
- Use `--ohlc` flag to get OHLC data
- `--hlc` and `--ohlcv` flags removed (use `--ohlc --vol` instead)

### New Features
- Multiple tickers as arguments: `duk ph AAPL MSFT GOOGL`
- `--combine` flag for consolidated multi-ticker output
- `--no-close` flag to remove close from output
- `--verbose` flag for detailed logging to stdout

### Migration Examples
```bash
# Old command → New command
duk ph AAPL --days 30 → duk ph AAPL -n 30
duk ph AAPL --output → duk ph AAPL --csv
duk ph AAPL --format json --output → duk ph AAPL --json
duk ph AAPL --ohlcv → duk ph AAPL --ohlc --vol
duk ph tickers.txt → duk ph AAPL MSFT GOOGL (manual expansion)
```

## Notes

- Historical data availability depends on the security and FMP's data coverage
- Adjusted price calculations follow standard financial industry practices
- Frequency aggregation uses pandas resampling with appropriate aggregation rules
- Multiple ticker processing continues even if some tickers fail to download
- API rate limits may apply depending on your FMP subscription tier
- All logging is written to `var/duk.log`, with optional verbose output to stdout