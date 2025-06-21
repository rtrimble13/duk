# Price History Downloader (`duk ph`)

The `duk ph` subprogram downloads historical security price data using the Financial Modeling Prep (FMP) API.

Note: An FMP API key is required. You can provide the key in one of two ways:
1. Set the `FMP_API_KEY` environment variable (recommended for CI/automated environments)
2. Place your key in `etc/.fmp_api.key` file

## Overview

The price history downloader retrieves historical OHLCV (Open, High, Low, Close, Volume) data for securities, with support for:

- Single ticker symbols or multiple tickers from a file
- Various date range options and observation counts
- Multiple output field combinations
- Dividend and stock split data integration
- Adjusted price calculations
- Frequency aggregation (daily, weekly, monthly, quarterly, semiannual, annual)
- CSV and JSON output formats

## Basic Usage

```bash
# Get latest 5 days of OHLC data for AAPL
duk ph AAPL

# Get last 30 days of data
duk ph AAPL --days 30

# Get specific date range
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

## Ticker Input Options

### Single Ticker
```bash
# Download data for Apple Inc.
duk ph AAPL

# Ticker symbols are case-insensitive
duk ph aapl
```

### Multiple Tickers from File
```bash
# Create a file with ticker symbols (one per line)
echo -e "AAPL\nMSFT\nGOOGL" > tickers.txt

# Download data for all tickers in the file
duk ph tickers.txt
```

## Date Options

### Specific Date Range
```bash
# Download data for a specific date range
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Short form
duk ph AAPL -s 2023-01-01 -e 2023-12-31
```

### Number of Observations
```bash
# Download last 10 days of data
duk ph AAPL --days 10
duk ph AAPL -n 10

# Download 30 days starting from a specific date
duk ph AAPL --start-date 2023-01-01 --days 30

# Download 30 days ending at a specific date
duk ph AAPL --end-date 2023-12-31 --days 30
```

## Output Field Combinations

### Default Output (OHLC)
```bash
# Returns Open, High, Low, Close prices
duk ph AAPL
duk ph AAPL --ohlc
```

### Alternative Field Combinations
```bash
# High, Low, Close only
duk ph AAPL --hlc

# Open, High, Low, Close, Volume
duk ph AAPL --ohlcv

# Add volume to any combination
duk ph AAPL --ohlc --vol
```

### Special Data Fields

#### Adjusted Prices
```bash
# Include adjusted close prices (factors in dividends and splits)
duk ph AAPL --adj

# Adjusted prices only
duk ph AAPL --adj  # (without other field flags)

# OHLC with adjusted close
duk ph AAPL --ohlc --adj
```

#### Dividend Data
```bash
# Include dividend payments
duk ph AAPL --div

# Dividends only
duk ph AAPL --div  # (without other field flags)

# OHLC with dividends
duk ph AAPL --ohlc --div
```

#### Stock Split Data
```bash
# Include stock split ratios
duk ph AAPL --split

# Splits only
duk ph AAPL --split  # (without other field flags)

# OHLC with splits
duk ph AAPL --ohlc --split
```

#### Combined Adjustments
```bash
# Include adjusted prices with dividend and split data
duk ph AAPL --adj --div --split
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
duk ph AAPL --days 365 --frequency monthly

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
# CSV output to stdout
duk ph AAPL

# JSON output to stdout
duk ph AAPL --format json
```

### Output to File
```bash
# Save to file with default naming (price_history_AAPL_YYYYMMDD.csv)
duk ph AAPL --output
duk ph AAPL -o

# Save with custom filename
duk ph AAPL --filename my_apple_data
duk ph AAPL -f my_apple_data

# Specify output directory
duk ph AAPL --output --directory ./data
duk ph AAPL -o -D ./data

# JSON format to file
duk ph AAPL --output --format json
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
symbol,date,open,high,low,close
AAPL,2023-12-01,150.0,155.0,148.0,152.0
AAPL,2023-11-30,148.0,151.0,147.0,150.0
```

### JSON Output Format
```json
[
  {
    "symbol": "AAPL",
    "date": "2023-12-01",
    "open": 150.0,
    "high": 155.0,
    "low": 148.0,
    "close": 152.0
  },
  {
    "symbol": "AAPL",
    "date": "2023-11-30",
    "open": 148.0,
    "high": 151.0,
    "low": 147.0,
    "close": 150.0
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
# Latest 5 days OHLC for Apple
duk ph AAPL

# Last 30 days with volume
duk ph AAPL --days 30 --ohlcv

# Year 2023 data
duk ph AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

### File Output Examples
```bash
# Save last 30 days to default file
duk ph AAPL --days 30 --output

# Save custom data to JSON file
duk ph AAPL --days 90 --ohlcv --adj --filename apple_q4 --format json --output

# Save to specific directory
duk ph AAPL --output --directory ./market_data
```

### Advanced Examples
```bash
# Multiple tickers with adjustments
duk ph tickers.txt --adj --div --split --output

# Weekly aggregated data for analysis
duk ph AAPL --days 365 --frequency weekly --ohlcv --output

# Monthly data with all adjustments in JSON format
duk ph AAPL --start-date 2020-01-01 --frequency monthly --adj --div --split --format json --output
```

### Analysis Integration Examples
```bash
# Data for technical analysis
duk ph AAPL --days 200 --ohlcv --format json > aapl_data.json

# Dividend analysis
duk ph "KO" --start-date 2020-01-01 --div --format json > coca_cola_dividends.json

# Multi-stock comparison
echo -e "AAPL\nMSFT\nGOOGL\nAMZN" > tech_stocks.txt
duk ph tech_stocks.txt --days 365 --frequency monthly --format json --output
```

## Error Handling

The command provides clear error messages for common issues:

- **Invalid ticker symbols**: "No price data found for symbol XYZ"
- **Network connectivity issues**: "Failed to download price data"
- **Invalid date formats**: Use YYYY-MM-DD format
- **Empty ticker files**: "File contains no valid ticker symbols"
- **Invalid date combinations**: Cannot specify conflicting date parameters

## Logging

When run with the `-v` flag, detailed logging information is written to `var/duk.log` and displayed on stderr, including:

- API request details for each ticker
- Number of records downloaded
- Data processing steps
- File save locations
- Error details for troubleshooting

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

## Notes

- Historical data availability depends on the security and FMP's data coverage
- Adjusted price calculations follow standard financial industry practices
- Frequency aggregation uses pandas resampling with appropriate aggregation rules
- Multiple ticker processing continues even if some tickers fail to download
- API rate limits may apply depending on your FMP subscription tier