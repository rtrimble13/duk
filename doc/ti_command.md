# Technical Indicators Command (ti)

The `ti` command group provides technical indicator calculations for financial time series data. These indicators help traders and analysts identify trends, momentum, and potential trading signals.

## Overview

```bash
duk ti <indicator> [OPTIONS]
```

Available indicators:
- **sma** - Simple Moving Average
- **ema** - Exponential Moving Average  
- **rsi** - Relative Strength Index
- **macd** - Moving Average Convergence Divergence

All indicator commands share common options:
- `-i, --input PATH` - Input file containing price data (CSV or JSON) [required]
- `-c, --column TEXT` - Column name to calculate indicator on (e.g., 'close', 'high', 'low') [required]
- `-o, --output PATH` - Write results to file
- `--csv` - Output data as CSV (default)
- `--json` - Output data as JSON
- `-p, --precision INTEGER` - Decimal precision for output values (default: 3)
- `-q, --quiet` - Suppress printing data to stdout
- `-v, --verbose` - Print detailed logging to stdout
- `--summary` - Print summary statistics instead of data observations

## MACD (Moving Average Convergence Divergence)

The MACD is a trend-following momentum indicator that shows the relationship between two exponential moving averages (EMAs) of a security's price.

### Usage

```bash
duk ti macd --input PRICE_FILE --column COLUMN_NAME [OPTIONS]
```

### Options

- `--fast-window INTEGER` - Fast EMA window size (default: 12)
- `--slow-window INTEGER` - Slow EMA window size (default: 26)
- `--signal-window INTEGER` - Signal line EMA window size (default: 9)

### Output Columns

The MACD command adds three new columns to your data:

1. **{column}_macd** - The MACD line (fast EMA - slow EMA)
2. **{column}_macd_signal** - The signal line (EMA of MACD)
3. **{column}_macd_hist** - The histogram (MACD - signal)

### Interpretation

- **Bullish Signal**: MACD crosses above the signal line
- **Bearish Signal**: MACD crosses below the signal line
- **Divergence**: When price and MACD move in opposite directions (potential trend reversal)
- **Histogram**: Shows the strength of momentum
  - Positive histogram: MACD is above signal (bullish momentum)
  - Negative histogram: MACD is below signal (bearish momentum)

### Example 1: Calculate MACD with Default Parameters

Calculate MACD on closing prices using standard settings (12, 26, 9):

```bash
duk ti macd --input prices.csv --column close --output macd_result.csv
```

Input file (`prices.csv`):
```csv
date,close
2024-01-01,100
2024-01-02,102
2024-01-03,101
...
```

Output file includes original data plus MACD columns:
```csv
date,close,close_macd,close_macd_signal,close_macd_hist
2024-01-01,100,,,
2024-01-02,102,,,
...
2024-02-03,133,6.008,5.738,0.270
2024-02-04,135,6.164,5.823,0.340
```

### Example 2: Calculate MACD with Custom Windows

Use faster settings for more responsive signals (5, 10, 3):

```bash
duk ti macd --input prices.csv --column close \
  --fast-window 5 --slow-window 10 --signal-window 3 \
  --output macd_fast.csv
```

This produces more frequent crossovers and is useful for short-term trading.

### Example 3: Calculate MACD with JSON Output

```bash
duk ti macd --input prices.csv --column close --json --output macd.json
```

### Example 4: View MACD Summary Statistics

```bash
duk ti macd --input prices.csv --column close --summary
```

Output shows statistics for MACD line, signal line, and histogram:
```
Number of results: 50

Column: close_macd
  count: 25
  mean: 6.234
  std: 0.432
  min: 5.316
  max: 6.773
  ...
```

### Example 5: Calculate MACD on Multiple Price Columns

If your data has multiple price columns (high, low, close), you can calculate MACD for each:

```bash
# Calculate MACD on closing prices
duk ti macd --input ohlc.csv --column close --output macd_close.csv

# Calculate MACD on high prices
duk ti macd --input ohlc.csv --column high --output macd_high.csv
```

### Data Requirements

- **Minimum data points**: At least `slow_window + signal_window` records for complete MACD calculation
  - With defaults (26 + 9 = 35 records minimum)
- **Date column**: Optional but recommended for time series analysis
- **Numeric column**: The specified column must contain numeric price data

### Tips and Best Practices

1. **Standard Settings (12, 26, 9)**
   - Most widely used parameters
   - Good for medium-term trend analysis
   - Works well on daily timeframes

2. **Faster Settings (5, 10, 3)**
   - More responsive to price changes
   - Generates more frequent signals
   - Better for short-term trading
   - More prone to false signals

3. **Slower Settings (19, 39, 9)**
   - Less sensitive to price changes
   - Generates fewer but more reliable signals
   - Better for long-term trend following
   - Slower to react to trend changes

4. **Combining with Other Indicators**
   - Use with RSI to confirm overbought/oversold conditions
   - Combine with volume indicators for validation
   - Look for divergences with price action

### Common Workflow

```bash
# Step 1: Get price data
duk ph AAPL --start-date 2024-01-01 --close > aapl_prices.csv

# Step 2: Calculate MACD
duk ti macd --input aapl_prices.csv --column close --output aapl_macd.csv

# Step 3: View results with summary
duk ti macd --input aapl_prices.csv --column close --summary
```

## SMA (Simple Moving Average)

Calculate the arithmetic mean of data points over a specified window period.

### Usage

```bash
duk ti sma --input PRICE_FILE --column COLUMN_NAME --window WINDOW [OPTIONS]
```

### Options

- `-w, --window INTEGER` - Window size for SMA calculation [required]

### Example

```bash
duk ti sma --input prices.csv --column close --window 20 --output sma_result.csv
```

## EMA (Exponential Moving Average)

Calculate a weighted moving average that gives more weight to recent data points.

### Usage

```bash
duk ti ema --input PRICE_FILE --column COLUMN_NAME --window WINDOW [OPTIONS]
```

### Options

- `-w, --window INTEGER` - Window size for EMA calculation [required]

### Example

```bash
duk ti ema --input prices.csv --column close --window 20 --output ema_result.csv
```

## RSI (Relative Strength Index)

Calculate the momentum oscillator that measures the speed and magnitude of price changes.

### Usage

```bash
duk ti rsi --input PRICE_FILE --column COLUMN_NAME [OPTIONS]
```

### Options

- `-w, --window INTEGER` - Window size for RSI calculation (default: 14)

### Example

```bash
duk ti rsi --input prices.csv --column close --window 14 --output rsi_result.csv
```

### Interpretation

- **RSI > 70**: Overbought condition (potential sell signal)
- **RSI < 30**: Oversold condition (potential buy signal)
- **RSI = 50**: Neutral momentum

## Input File Format

All technical indicator commands accept CSV or JSON files with the following requirements:

### CSV Format

```csv
date,close,high,low,volume
2024-01-01,100,102,98,1000000
2024-01-02,102,104,100,1100000
```

### JSON Format

```json
[
  {"date": "2024-01-01", "close": 100, "high": 102, "low": 98, "volume": 1000000},
  {"date": "2024-01-02", "close": 102, "high": 104, "low": 100, "volume": 1100000}
]
```

### Requirements

- Files must contain at least one numeric column for calculation
- Column names are case-sensitive
- Date column is optional but recommended for time series data
- CSV files should have headers in the first row

## Error Handling

Common errors and solutions:

1. **"Column not found in input data"**
   - Check column name spelling (case-sensitive)
   - Use `head -1 input.csv` to see available columns

2. **"Window must be greater than 0"**
   - Ensure window parameters are positive integers

3. **"Fast window must be less than slow window"** (MACD only)
   - Verify fast_window < slow_window

4. **"Input file contains no data"**
   - Check that input file is not empty
   - Verify file format (CSV or JSON)

5. **"Not enough data points"**
   - Ensure sufficient records for calculation
   - MACD needs at least slow_window + signal_window records

## Performance Considerations

- **Large files**: For files with millions of rows, consider:
  - Processing in chunks
  - Using appropriate precision (fewer decimal places = faster)
  - Writing to file instead of stdout

- **Memory usage**: All data is loaded into memory
  - Typical usage: 1MB file ≈ 10MB memory

## Related Commands

- `duk ph` - Get price history data
- `duk rc` - Calculate returns from price data
- `duk ls` - List securities for analysis

## See Also

- [Price History Command](ph_command.md)
- [Return Calculations Command](rc_command.md)
- [duk Documentation Index](index.md)

---

**Last Updated**: January 2026
