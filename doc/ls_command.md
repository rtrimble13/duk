# duk ls Command

## Overview

The `ls` command retrieves company and market information from the Financial Modeling Prep (FMP) API and outputs it to stdout or a file.

## Command Signature

```bash
duk ls [options]
```

## Options

### List Type Options

These options control what type of list is returned. Only one can be specified at a time.

- `--sectors`: List all market sectors
- `--industries`: List all industries

If no list type option is specified, the command returns actively trading securities.

### Output Options

- `--csv`: Output data as CSV format (default)
- `--json`: Output data as JSON format
- `-o, --output PATH`: Write data to file instead of stdout
- `-q, --quiet`: Suppress printing list data to stdout
- `-v, --verbose`: Print all logging to stdout (debug level)

### Filter Options

- `-n, --limit INTEGER`: Maximum number of records to return

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

### Example 1: Get Actively Trading Securities

```bash
duk ls
```

Retrieves all actively trading securities with symbol and name fields.

### Example 2: Get Limited Number of Securities

```bash
duk ls -n 10
```

Retrieves the first 10 actively trading securities.

### Example 3: Get All Market Sectors

```bash
duk ls --sectors
```

Retrieves a list of all market sectors.

### Example 4: Get All Industries

```bash
duk ls --industries
```

Retrieves a list of all industries.

### Example 5: Write Securities to a File

```bash
duk ls -o securities.csv
```

Retrieves actively trading securities and writes them to `securities.csv`.

### Example 6: Get Sectors in JSON Format

```bash
duk ls --sectors --json
```

Retrieves market sectors and outputs them in JSON format.

### Example 7: Quiet Mode with File Output

```bash
duk ls --sectors -o sectors.csv -q
```

Retrieves sectors and writes to file without printing data to stdout. Only the confirmation message is printed.

### Example 8: Verbose Mode for Debugging

```bash
duk ls --industries -v
```

Retrieves industries with debug logging enabled, showing detailed information about the API request and processing.

### Example 9: Limited Sectors to JSON File

```bash
duk ls --sectors -n 5 --json -o sectors.json
```

Retrieves the first 5 sectors and writes them to a JSON file.

### Example 10: Get Limited Industries

```bash
duk ls --industries -n 20
```

Retrieves the first 20 industries.

## Output Format

The command can output data in two formats: CSV (default) or JSON.

### CSV Output Format

CSV output has the following characteristics:

- Column names are based on the list type
- Data is not sorted (returned in API order)
- Numeric values are not quoted

#### Actively Trading Securities (Default)

```csv
symbol,name
AAPL,Apple Inc.
MSFT,Microsoft Corporation
GOOGL,Alphabet Inc.
```

#### Sectors (--sectors)

```csv
sector
Technology
Healthcare
Financial Services
```

#### Industries (--industries)

```csv
industry
Software
Pharmaceuticals
Banking
```

### JSON Output Format

JSON output has the following characteristics:

- Array of objects, one per record
- Column names are based on the list type
- Data is not sorted (returned in API order)

#### Actively Trading Securities (Default)

```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc."
  },
  {
    "symbol": "MSFT",
    "name": "Microsoft Corporation"
  }
]
```

#### Sectors (--sectors)

```json
[
  {
    "sector": "Technology"
  },
  {
    "sector": "Healthcare"
  }
]
```

#### Industries (--industries)

```json
[
  {
    "industry": "Software"
  },
  {
    "industry": "Pharmaceuticals"
  }
]
```

## Error Handling

The command will exit with an error (exit code 1) in the following cases:

1. **Missing API Key**: FMP API key not configured
   ```
   Error: FMP API key not configured. Set FMP_API_KEY environment variable
   or add fmp_key to [api] section in ~/.dukrc
   ```

2. **Multiple List Types**: More than one list type option specified
   ```
   Error: Only one of --sectors or --industries can be specified
   ```

3. **Multiple Output Formats**: Both --csv and --json specified
   ```
   Error: Only one of --csv or --json can be specified
   ```

4. **API Error**: Failed to fetch data from the API
   ```
   Error: Failed to fetch list data: <error message>
   ```

When no data is available, the command exits successfully (exit code 0) with a message:
```
No data found
```

## Tips and Best Practices

1. **Use Environment Variables**: Set `FMP_API_KEY` as an environment variable to avoid storing sensitive data in config files:
   ```bash
   export FMP_API_KEY="your_api_key_here"
   duk ls
   ```

2. **Combine with Unix Tools**: The CSV output can be easily processed with standard Unix tools:
   ```bash
   # Count securities
   duk ls | wc -l
   
   # Filter with grep
   duk ls | grep "Apple"
   
   # Search for specific symbols
   duk ls | grep "^AAPL,"
   ```

3. **Use JSON with jq**: JSON output works well with jq for advanced data processing:
   ```bash
   # Extract all symbols
   duk ls --json | jq '.[].symbol'
   
   # Filter by name
   duk ls --json | jq '.[] | select(.name | contains("Apple"))'
   
   # Count records
   duk ls --json | jq 'length'
   ```

4. **Quiet Mode for Scripts**: Use `-q` flag in scripts to suppress data output while still getting status messages:
   ```bash
   duk ls -o securities.csv -q && echo "Securities downloaded successfully"
   ```

5. **Verbose Mode for Troubleshooting**: Use `-v` flag to see detailed logging when debugging issues:
   ```bash
   duk ls -v
   ```

6. **Use Limit for Testing**: Use `--limit` to get a small sample when testing:
   ```bash
   duk ls --sectors -n 5
   ```

## Related Functions

- `actively_trading_list_api()`: API function for actively trading securities
- `sector_list_api()`: API function for sectors
- `industry_list_api()`: API function for industries

## See Also

- Main duk documentation: `man duk`
- [ph Command Documentation](ph_command.md)
- [yc Command Documentation](yc_command.md)
