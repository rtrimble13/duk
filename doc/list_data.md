# List Subprogram (`duk ls`)

The `ls` subprogram provides access to various financial lists and market data through the Financial Modeling Prep (FMP) API. It allows you to retrieve information about indexes, sectors, industries, exchanges, ETFs, funds, and stocks.

## Prerequisites

An FMP API key is required to use this subprogram. You can obtain a free API key at [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs).

Configure your API key in one of these locations (in order of precedence):
- Project-specific: `etc/tb.rc`
- User-specific: `~/.tbrc`  
- System-wide: `/usr/local/etc/tb.rc`
- Environment variable: `FMP_API_KEY`

## Usage

```bash
duk ls [LIST_TYPE] [OPTIONS]
```

## Available List Types

### Basic Usage
```bash
# Show all available list types
duk ls
```

### Index Lists
```bash
# List all USD indexes
duk ls index
```
Returns indexes with symbol, name, and exchange. Automatically filters for USD currency only.

### Sector Lists
```bash
# List all available sectors
duk ls sector
```
Returns all sectors available in the FMP database.

### Industry Lists
```bash
# List all available industries
duk ls industry
```
Returns all industries available in the FMP database.

### Exchange Lists
```bash
# List US exchanges
duk ls exchange
```
Returns US exchanges only (filtered by country code "US").

### ETF Lists
```bash
# List US ETFs
duk ls etf
```
Returns ETFs with symbol, company name, sector, and industry. Automatically filters for US exchanges.

### Fund Lists
```bash
# List US funds
duk ls fund
```
Returns mutual funds with symbol, company name, sector, and industry. Automatically filters for US exchanges.

### Stock Lists
```bash
# List all US stocks
duk ls stock

# List S&P 500 stocks only
duk ls stock --sp500

# List NASDAQ 100 stocks only
duk ls stock --nasdaq
```
Returns stocks with symbol, company name, sector, and industry. Can be filtered to specific indexes.

## Options

### Stock Filtering
- `--sp500`, `--s&p`: Filter stocks to S&P 500 constituents only
- `--nasdaq`: Filter stocks to NASDAQ 100 constituents only

### Output Options

#### Output to File
```bash
# Output to file with default naming
duk ls sector --output
duk ls sector -o

# Output to file with custom filename
duk ls sector --filename my_sectors
duk ls sector -f my_sectors

# Specify output directory
duk ls sector --output --directory /path/to/output
duk ls sector -o -D /path/to/output
```

#### Output Formats

##### CSV Format (Default)
```bash
# CSV output to stdout
duk ls sector

# CSV output to file
duk ls sector --output --format csv
```

##### JSON Format
```bash
# JSON output to stdout
duk ls sector --format json

# JSON output to file
duk ls sector --output --format json
```

### Caching
```bash
# Use cached data (default)
duk ls sector

# Disable caching and always fetch fresh data
duk ls sector --no-cache
```

## Examples

### Basic Examples
```bash
# Show available list types
duk ls

# List USD indexes
duk ls index

# List available sectors
duk ls sector

# List US exchanges
duk ls exchange
```

### Output Format Examples
```bash
# Get sectors in JSON format
duk ls sector --format json

# Get ETFs and save to CSV file
duk ls etf --output

# Get exchanges and save to custom JSON file
duk ls exchange --filename exchanges --format json --output
```

### Stock Filtering Examples
```bash
# Get all US stocks
duk ls stock

# Get S&P 500 stocks only
duk ls stock --sp500

# Get NASDAQ 100 stocks and save to file
duk ls stock --nasdaq --output

# Get S&P 500 stocks in JSON format
duk ls stock --sp500 --format json
```

### Advanced Examples
```bash
# Get all ETFs with custom output directory
duk ls etf --output --directory /data/financial

# Get fund data without caching
duk ls fund --no-cache --format json

# Get industry list and save with custom filename
duk ls industry --filename industry_categories --output
```

## File Naming

When saving to files, the default naming convention is:
- `{list_type}_list.{format}` (e.g., `sector_list.csv`)
- For stock filters: `stock_list_{filter}.{format}` (e.g., `stock_list_sp500.csv`)

## Output Fields

### Index Lists
- symbol
- name  
- exchange

### Sector/Industry Lists
- sector/industry (string values)

### Exchange Lists
- All available exchange fields from the API

### ETF/Fund/Stock Lists
- symbol
- companyName
- sector
- industry

## Data Sources

All data is sourced from Financial Modeling Prep APIs:
- Index data: `/stable/index-list`
- Sector data: `/stable/available-sectors`
- Industry data: `/stable/available-industries`
- Exchange data: `/stable/available-exchanges`
- ETF/Fund/Stock data: `/stable/company-screener`
- S&P 500 data: `/stable/sp500-constituent`
- NASDAQ 100 data: `/stable/nasdaq-constituent`

## Caching

The `ls` subprogram includes intelligent caching to improve performance:
- Data is cached locally in SQLite database
- Cache is used by default to reduce API calls
- Use `--no-cache` to force fresh data retrieval
- Cache keys are generated based on list type and filters

## Integration with Data Analysis

The output format is designed to be easily loaded into pandas DataFrames:

### Python Integration
```python
import pandas as pd
import subprocess
import json

# Get sector data as JSON
result = subprocess.run(['duk', 'ls', 'sector', '--format', 'json'], 
                       capture_output=True, text=True)
sectors = json.loads(result.stdout)
df = pd.DataFrame(sectors)

# Get S&P 500 stocks as CSV
df_sp500 = pd.read_csv('stock_list_sp500.csv')  # After running: duk ls stock --sp500 --output
```

### CSV Integration
```bash
# Direct import into spreadsheet applications
duk ls etf --output
# Opens etf_list.csv in Excel, LibreOffice, etc.

# Pipe to other command-line tools
duk ls stock --sp500 | grep Technology
```

## Error Handling

The command provides clear error messages for common issues:
- Invalid list types
- API key configuration problems
- Network connectivity issues
- Invalid filter combinations
- File permission issues

## Performance Considerations

- First run of each list type will be slower due to API calls
- Subsequent runs use cached data for improved performance
- Large lists (like all stocks) may take longer to download initially
- Use `--no-cache` sparingly to avoid unnecessary API calls