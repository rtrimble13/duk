# duk ph Command

## Overview

The `ph` command retrieves historical price data for securities from the Financial Modeling Prep (FMP) API and outputs it to stdout or a file.

## Command Signature

```bash
duk ph <symbol> [options]
```

## Arguments

- **symbol**: The ticker symbol for the security (e.g., AAPL, MSFT, GOOGL). Case insensitive.

## Options

### Date and Frequency Options

- `-s, --start-date TEXT`: Start date in YYYY-MM-DD format (e.g., "2023-01-01")
- `-e, --end-date TEXT`: End date in YYYY-MM-DD format (e.g., "2023-12-31")
- `-n, --limit INTEGER`: Maximum number of records to return
- `-f, --frequency`: Data frequency. Valid values:
  - `day` (default): Daily data
  - `week`: Weekly data
  - `month`: Monthly data
  - `quarter`: Quarterly data
  - `semi-annual`: Semi-annual data
  - `annual`: Annual data

### Field Filter Options

These options control which price fields are returned. Only one field filter can be used at a time.

- `--ohlc`: Return Date, Open, High, Low, and Close fields
- `--hlc`: Return Date, High, Low, and Close fields
- `--close`: Return Date and Close fields only
- `--hlcv`: Return Date, High, Low, Close, and Volume fields
- `--cv`: Return Date and Volume fields only

If no field filter is specified, all available fields are returned (Date, Open, High, Low, Close, Volume).

### Output Options

- `--csv`: Output data as CSV format (default)
- `--json`: Output data as JSON format
- `-o, --output PATH`: Write data to file instead of stdout
  - If PATH is a file, data is written to that file with appropriate extension
  - If PATH is a directory, filename is formatted as `<symbol>_<start>_<end>.<ext>` where ext is csv or json
- `-q, --quiet`: Suppress printing price history data to stdout
- `-v, --verbose`: Print all logging to stdout (debug level)

**Note**: Only one of `--csv` or `--json` can be specified at a time. If neither is specified, CSV format is used by default.

## Configuration

The command requires an FMP API key, which can be provided in two ways:

1. Environment variable: `FMP_API_KEY`
2. Configuration file (`~/.dukrc`):
   ```toml
   [api]
   fmp_key = "your_api_key_here"
   ```

The environment variable takes precedence over the configuration file.

## Usage Examples

### Example 1: Get All Available Daily Data

```bash
duk ph AAPL
```

Retrieves all available daily price data for Apple stock.

### Example 2: Get Data for a Specific Date Range

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31
```

Retrieves daily price data for Apple stock for the entire year 2023.

### Example 3: Get Last 30 Daily Records

```bash
duk ph AAPL -n 30
```

Retrieves the last 30 daily records for Apple stock.

### Example 4: Get First 10 Records from a Date

```bash
duk ph AAPL -s 2023-01-01 -n 10
```

Retrieves the first 10 daily records starting from January 1, 2023.

### Example 5: Get Weekly Data

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -f week
```

Retrieves weekly price data for Apple stock for 2023.

### Example 6: Get Monthly Data with Limit

```bash
duk ph AAPL -f month -n 12
```

Retrieves the last 12 months of monthly price data for Apple stock.

### Example 7: Get Only Closing Prices

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 --close
```

Retrieves only the date and closing price for Apple stock in 2023.

### Example 8: Get OHLC Data (No Volume)

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 --ohlc
```

Retrieves Date, Open, High, Low, and Close data (without Volume) for Apple stock in 2023.

### Example 9: Get High, Low, Close, and Volume

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 --hlcv
```

Retrieves Date, High, Low, Close, and Volume data for Apple stock in 2023.

### Example 10: Write Data to a File

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -o aapl_2023.csv
```

Retrieves Apple stock data for 2023 and writes it to `aapl_2023.csv`.

### Example 11: Write Data to a Directory

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -o ./data/
```

Retrieves Apple stock data for 2023 and writes it to `./data/AAPL_2023-01-01_2023-12-31.csv`.

### Example 12: Quiet Mode with File Output

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -o output.csv -q
```

Retrieves data and writes to file without printing data to stdout. Only the confirmation message is printed.

### Example 13: Verbose Mode for Debugging

```bash
duk ph AAPL -s 2023-01-01 -e 2023-12-31 -v
```

Retrieves data with debug logging enabled, showing detailed information about the API request and processing.

### Example 14: Case Insensitive Symbol

```bash
duk ph aapl
duk ph AAPL
duk ph AaPl
```

All three commands are equivalent. Symbol names are case-insensitive.

### Example 15: Quarterly Data for Multiple Years

```bash
duk ph MSFT -s 2020-01-01 -e 2023-12-31 -f quarter
```

Retrieves quarterly price data for Microsoft stock from 2020 to 2023.

### Example 16: Annual Data for Last 5 Years

```bash
duk ph GOOGL -f annual -n 5
```

Retrieves the last 5 years of annual price data for Google stock.

### Example 17: Volume and Close Data Only

```bash
duk ph TSLA -s 2023-01-01 -e 2023-12-31 --cv
```

Retrieves only Date and Volume fields for Tesla stock in 2023, useful for volume analysis.

## Output Format

The command can output data in two formats: CSV (default) or JSON.

### CSV Output Format

CSV output has the following characteristics:

- Column names are capitalized (e.g., "Date", "Open", "High", "Low", "Close", "Volume")
- Dates are in YYYY-MM-DD format
- Data is sorted in ascending order by date
- Numeric values are not quoted

Example CSV output:

```csv
Date,Open,High,Low,Close,Volume
2023-01-03,149.0,155.0,148.0,154.0,1000000
2023-01-04,154.0,158.0,153.0,157.0,1100000
2023-01-05,157.0,160.0,156.0,159.0,1050000
```

### JSON Output Format

JSON output has the following characteristics:

- Array of objects, one per record
- Column names are capitalized (same as CSV)
- Dates are in ISO 8601 format
- Data is sorted in ascending order by date

Example JSON output:

```json
[
  {
    "Date": "2023-01-03T00:00:00.000Z",
    "Open": 149.0,
    "High": 155.0,
    "Low": 148.0,
    "Close": 154.0,
    "Volume": 1000000
  },
  {
    "Date": "2023-01-04T00:00:00.000Z",
    "Open": 154.0,
    "High": 158.0,
    "Low": 153.0,
    "Close": 157.0,
    "Volume": 1100000
  }
]
```

## Data Resampling

When using frequencies other than "day", the command automatically resamples the data:

- **Open**: First value in the period
- **High**: Maximum value in the period
- **Low**: Minimum value in the period
- **Close**: Last value in the period
- **Volume**: Sum of volumes in the period

This ensures proper OHLC (Open-High-Low-Close) aggregation for financial data.

## Limit Behavior

The `--limit` parameter behaves differently based on which dates are provided:

### With start_date (no end_date)
Returns the **first N records** starting from start_date.

```bash
duk ph AAPL -s 2023-01-01 -n 10
# Returns: First 10 records starting from 2023-01-01
```

### With end_date (no start_date)
Returns the **last N records** before end_date.

```bash
duk ph AAPL -e 2023-12-31 -n 10
# Returns: Last 10 records before 2023-12-31
```

### With neither start_date nor end_date
Returns the **last N records** available.

```bash
duk ph AAPL -n 30
# Returns: Last 30 records available
```

### Example 18: Output as JSON

```bash
duk ph AAPL -s 2023-01-01 -e 2023-01-31 --json
```

Retrieves data for Apple stock in January 2023 and outputs it in JSON format.

### Example 19: Output JSON to File

```bash
duk ph MSFT -s 2023-01-01 -e 2023-12-31 --json -o msft_2023.json
```

Retrieves Microsoft stock data for 2023 and writes it to a JSON file.

### Example 20: JSON Output to Directory

```bash
duk ph GOOGL -s 2023-01-01 -e 2023-12-31 --json -o ./data/
```

Retrieves Google stock data for 2023 and writes it to `./data/GOOGL_2023-01-01_2023-12-31.json`.

## Error Handling

The command will exit with an error (exit code 1) in the following cases:

1. **Missing API Key**: FMP API key not configured
   ```
   Error: FMP API key not configured. Set FMP_API_KEY environment variable
   or add fmp_key to [api] section in ~/.dukrc
   ```

2. **Multiple Field Filters**: More than one field filter option specified
   ```
   Error: Only one of --ohlc, --hlc, --close, --hlcv, --cv can be specified
   ```

3. **Multiple Output Formats**: Both --csv and --json specified
   ```
   Error: Only one of --csv or --json can be specified
   ```

4. **API Error**: Failed to fetch data from the API
   ```
   Error: Failed to fetch price history: <error message>
   ```

When no data is available for the symbol, the command exits successfully (exit code 0) with a message:
```
No data found for SYMBOL
```

## Tips and Best Practices

1. **Use Environment Variables**: Set `FMP_API_KEY` as an environment variable to avoid storing sensitive data in config files:
   ```bash
   export FMP_API_KEY="your_api_key_here"
   duk ph AAPL
   ```

2. **Combine with Unix Tools**: The CSV output can be easily processed with standard Unix tools:
   ```bash
   # Count records
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 | wc -l
   
   # Filter with grep
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 | grep "2023-01"
   
   # Use with awk for calculations
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 --close | awk -F, 'NR>1 {sum+=$2; count++} END {print "Average:", sum/count}'
   ```

3. **Use JSON with jq**: JSON output works well with jq for advanced data processing:
   ```bash
   # Extract closing prices
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 --json | jq '.[].Close'
   
   # Calculate average closing price
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 --json | jq '[.[].Close] | add/length'
   
   # Filter records by date
   duk ph AAPL -s 2023-01-01 -e 2023-12-31 --json | jq '.[] | select(.Date | startswith("2023-01"))'
   ```

4. **Use Field Filters for Performance**: Request only the fields you need to reduce data transfer and processing time:
   ```bash
   # For simple price analysis
   duk ph AAPL --close
   
   # For OHLC charting
   duk ph AAPL --ohlc
   ```

5. **Quiet Mode for Scripts**: Use `-q` flag in scripts to suppress data output while still getting status messages:
   ```bash
   duk ph AAPL -o data.csv -q && echo "Data downloaded successfully"
   ```

6. **Verbose Mode for Troubleshooting**: Use `-v` flag to see detailed logging when debugging issues:
   ```bash
   duk ph AAPL -v
   ```

## Related Functions

- `get_price_history()`: Python function used internally by the command
- `price_history_api()`: Lower-level API function for raw data access

## See Also

- [get_price_history Function Documentation](get_price_history.md)
- Main duk documentation: `man duk`
