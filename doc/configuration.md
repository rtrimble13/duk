# Configuration Management (duk.rc)

The `duk` CLI tool uses a configuration system based on `configistate` to manage API keys and settings. Configuration is stored in a single user configuration file: `~/.dukrc`.

## Configuration File Location

The configuration file is located at:

**`~/.dukrc`** - User configuration file in your home directory

## Configuration File Format

Configuration files use the TOML format, which is modern, standardized, and easy to read. Here's an example configuration:

```toml
# TurningBull Configuration File (duk.rc)

[api_keys]
# Financial Modeling Prep API key
# Get your free API key at: https://financialmodelingprep.com/developer/docs
fmp_api_key = "your_fmp_api_key_here"

# API keys can also be read from files for better security
# fmp_api_key = "file:///path/to/secret/fmp_key.txt"

# Add other API keys as needed
# example_api_key = "your_example_key_here"

[settings]
# General application settings
log_level = "INFO"
default_output_directory = "var"
```

## API Key Configuration

### Financial Modeling Prep (FMP) API Key

The `tr`, `ph`, and `ls` subcommands require a Financial Modeling Prep API key. Configure it in any of these ways:

#### Method 1: Configuration File (Recommended)
Add to `~/.dukrc`:
```toml
[api_keys]
fmp_api_key = "your_actual_api_key_here"
```

#### Method 2: File-based API Key (Most Secure)
Store your API key in a separate file and reference it using the `file://` prefix:
```toml
[api_keys]
fmp_api_key = "file:///path/to/your/secret/fmp_key.txt"
```

The file should contain only the API key (whitespace will be automatically trimmed).

#### Method 3: Environment Variable (Backward Compatible)
```bash
export FMP_API_KEY="your_actual_api_key_here"
```

**Note**: Configuration file values take precedence over environment variables when both are present.

## Setup Instructions

### Quick Setup
1. Create a user configuration file:
   ```bash
   touch ~/.dukrc
   ```

2. Add your API key:
   ```bash
   cat >> ~/.dukrc << 'EOF'
   [api_keys]
   fmp_api_key = "your_actual_api_key_here"
   EOF
   ```

3. Test the configuration:
   ```bash
   duk tr --help  # Should not show API key errors
   ```

### File-based API Key Setup (Most Secure)
1. Create a secure file for your API key:
   ```bash
   mkdir -p ~/.duk/secrets
   echo "your_actual_api_key_here" > ~/.duk/secrets/fmp_key.txt
   chmod 600 ~/.duk/secrets/fmp_key.txt
   ```

2. Reference the file in your configuration:
   ```bash
   cat >> ~/.dukrc << 'EOF'
   [api_keys]
   fmp_api_key = "file://~/.duk/secrets/fmp_key.txt"
   EOF
   ```

   Note: The `file://` prefix tells configistate to read the key from the specified file. Both absolute paths and paths with `~` for home directory are supported.

## Configuration Validation

The duk CLI automatically validates required API keys on startup. If a required key is missing, it will show helpful error messages indicating:

- Which API keys are missing
- The configuration file location
- Alternative environment variable names

Example error message:
```
ERROR: Missing required API keys: ['fmp_api_key']
Configure API keys in:
  - ~/.dukrc
Or set environment variables (e.g., FMP_API_KEY)
```

## Configuration Features

### File References with configistate

The configuration system uses the `configistate` package, which provides powerful features:

- **Automatic File Reading**: Use `file://` prefix to read values from files
- **Path Expansion**: Supports `~` expansion in file paths
- **TOML Validation**: Full TOML format support with proper error messages

### Settings Configuration

You can configure various application settings:

```toml
[settings]
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_level = "INFO"

# Default output directory for data files
default_output_directory = "var"
```

The `log_level` setting controls the verbosity of log messages written to `var/duk.log`.

## Security Best Practices

1. **File Permissions**: Ensure configuration files containing API keys have appropriate permissions:
   ```bash
   chmod 600 ~/.dukrc
   ```

2. **Version Control**: Never commit API keys to version control. Add configuration files to `.gitignore`:
   ```gitignore
   .dukrc
   ```

3. **Environment-Specific Keys**: Use different API keys for development, testing, and production environments.

4. **File-based Keys**: For maximum security, store API keys in separate files with restricted permissions:
   ```bash
   mkdir -p ~/.duk/secrets
   chmod 700 ~/.duk/secrets
   echo "your_api_key" > ~/.duk/secrets/fmp_key.txt
   chmod 600 ~/.duk/secrets/fmp_key.txt
   ```

   Then reference in `~/.dukrc`:
   ```toml
   [api_keys]
   fmp_api_key = "file://~/.duk/secrets/fmp_key.txt"
   ```

## Troubleshooting

### Common Issues

1. **"FMP API key not found" error**
   - Check that your configuration file exists at `~/.dukrc`
   - Verify the `[api_keys]` section exists
   - Ensure the key name is `fmp_api_key` (not `FMP_API_KEY`)
   - If using file-based keys, ensure the file exists and is readable

2. **Configuration not loading**
   - Verify file permissions (readable by the user running duk)
   - Check TOML syntax with a TOML validator
   - Ensure file encoding is UTF-8

3. **File-based API key not working**
   - Ensure the file path is correct and the file exists
   - Check file permissions (must be readable)
   - Verify the file contains only the API key (no extra formatting)
   - Make sure to use the `file://` prefix in the config file

### Debug Configuration Loading

To see which configuration files are being loaded, use verbose mode:

```bash
duk -v tr --help 2>&1 | grep -E "(Loaded configuration|Found.*API)"
```

This will show debug messages about configuration file loading and API key sources.

## Migrating from Previous Versions

If you're migrating from a previous version that used multiple config file locations:

1. Check for existing configuration files:
   ```bash
   # Old locations (no longer used)
   cat ~/.duk/duk.rc 2>/dev/null
   cat duk/etc/duk.rc 2>/dev/null
   ```

2. Copy your configuration to the new location:
   ```bash
   # If you had a config at ~/.duk/duk.rc
   cp ~/.duk/duk.rc ~/.dukrc
   
   # Or create from scratch
   cat > ~/.dukrc << 'EOF'
   [api_keys]
   fmp_api_key = "your_actual_api_key_here"
   EOF
   ```

3. Test that it works:
   ```bash
   duk tr --help  # Should not show API key errors
   ```

## Technical Details

- **Configuration Package**: Uses `configistate` >= 1.0.0 from PyPI
- **Format**: TOML (Tom's Obvious, Minimal Language)
- **Python Support**: Uses built-in TOML parsing via configistate
- **Encoding**: UTF-8
- **File Reference**: Supports `file://` prefix for reading values from external files
- **Validation**: Performed at application startup before API calls

## Future Extensions

The configuration system is designed to be extensible. Future versions may support:
- Additional API providers
- Advanced logging configuration
- Output format preferences
- Custom data source endpoints
- Plugin configuration settings
