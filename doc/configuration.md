# Configuration Management (.tbrc)

The `duk` CLI tool uses a flexible configuration system based on `.tbrc` files to manage API keys and other settings. This system supports multiple configuration file locations with a clear priority order to accommodate different deployment scenarios.

## Configuration File Locations

Configuration files are loaded in the following priority order (highest priority first):

1. **Project Configuration**: `duk/etc/tb.rc` (highest priority)
   - Project-specific settings that override all other configurations
   - Located in the `etc/` directory of your duk installation/project
   - Best for project-specific API keys and settings

2. **User Configuration**: `~/.tbrc` (medium priority)
   - User-specific settings that apply to all duk usage for this user
   - Located in the user's home directory
   - Overrides system settings but not project settings

3. **System Configuration**: `/usr/local/etc/tb.rc` (lowest priority)
   - System-wide settings that apply to all users
   - Located in the system configuration directory
   - Provides default settings that can be overridden by user or project configs

## Configuration File Format

Configuration files use the TOML format, which is modern, standardized, and easy to read. Here's an example configuration:

```toml
# TurningBull Configuration File (.tbrc)

[api_keys]
# Financial Modeling Prep API key
# Get your free API key at: https://financialmodelingprep.com/developer/docs
fmp_api_key = "your_fmp_api_key_here"

# Add other API keys as needed
# example_api_key = "your_example_key_here"

[settings]
# General application settings
log_level = "INFO"
default_output_directory = "var"
```

## API Key Configuration

### Financial Modeling Prep (FMP) API Key

The `tr` and `ph` subcommands require a Financial Modeling Prep API key. Configure it in any of these ways:

#### Method 1: Configuration File (Recommended)
Add to any `.tbrc` file:
```toml
[api_keys]
fmp_api_key = "your_actual_api_key_here"
```

#### Method 2: Environment Variable (Backward Compatible)
```bash
export FMP_API_KEY="your_actual_api_key_here"
```

**Note**: Configuration files take precedence over environment variables when both are present.

## Setup Instructions

### Quick Setup
1. Create a user configuration file:
   ```bash
   touch ~/.tbrc
   ```

2. Add your API key:
   ```bash
   cat >> ~/.tbrc << 'EOF'
   [api_keys]
   fmp_api_key = "your_actual_api_key_here"
   EOF
   ```

3. Test the configuration:
   ```bash
   duk tr --help  # Should not show API key errors
   ```

### Project-Specific Setup
For project-specific configurations, edit the `etc/tb.rc` file in your duk installation:

```bash
# Navigate to your duk directory
cd /path/to/duk

# Edit the project configuration
vi etc/tb.rc
```

## Configuration Validation

The duk CLI automatically validates required API keys on startup. If a required key is missing, it will show helpful error messages indicating:

- Which API keys are missing
- All possible configuration file locations
- Alternative environment variable names

Example error message:
```
ERROR: Missing required API keys: ['fmp_api_key']
Configure API keys in one of the following locations:
  - /usr/local/etc/tb.rc
  - ~/.tbrc
  - duk/etc/tb.rc
Or set environment variables (e.g., FMP_API_KEY)
```

## Configuration Priority Examples

### Example 1: Multiple Configuration Files
If you have:
- System config: `/usr/local/etc/tb.rc` with `fmp_api_key = "system_key"`
- User config: `~/.tbrc` with `fmp_api_key = "user_key"`
- Project config: `duk/etc/tb.rc` with `fmp_api_key = "project_key"`

Result: `"project_key"` will be used (highest priority).

### Example 2: Mixed Configuration Sources
If you have:
- User config: `~/.tbrc` with `fmp_api_key = "file_key"`
- Environment variable: `FMP_API_KEY="env_key"`

Result: `"file_key"` will be used (file configs override environment variables).

### Example 3: Partial Configuration Override
System config:
```toml
[api_keys]
fmp_api_key = "system_fmp_key"
other_api_key = "system_other_key"

[settings]
log_level = "WARNING"
```

User config:
```toml
[api_keys]
fmp_api_key = "user_fmp_key"

[settings]
log_level = "INFO"
```

Result:
- `fmp_api_key = "user_fmp_key"` (overridden)
- `other_api_key = "system_other_key"` (inherited)
- `log_level = "INFO"` (overridden)

## Security Best Practices

1. **File Permissions**: Ensure configuration files containing API keys have appropriate permissions:
   ```bash
   chmod 600 ~/.tbrc
   ```

2. **Version Control**: Never commit API keys to version control. Add configuration files to `.gitignore`:
   ```gitignore
   .tbrc
   etc/tb.rc
   ```

3. **Environment-Specific Keys**: Use different API keys for development, testing, and production environments.

## Troubleshooting

### Common Issues

1. **"FMP API key not found" error**
   - Check that your configuration file exists and has the correct format
   - Verify the `[api_keys]` section exists
   - Ensure the key name is `fmp_api_key` (not `FMP_API_KEY`)

2. **Configuration not loading**
   - Verify file permissions (readable by the user running duk)
   - Check TOML syntax with a TOML validator
   - Ensure file encoding is UTF-8

3. **Wrong API key being used**
   - Check configuration priority order
   - Use debug logging to see which files are loaded: `duk -v tr --help`

### Debug Configuration Loading

To see which configuration files are being loaded, use verbose mode:

```bash
duk -v tr --help 2>&1 | grep -E "(Loaded configuration|Found.*API)"
```

This will show debug messages about configuration file loading and API key sources.

## Migrating from Environment Variables

If you're currently using environment variables, you can easily migrate to configuration files:

1. Check your current environment variable:
   ```bash
   echo $FMP_API_KEY
   ```

2. Create a configuration file with the same value:
   ```bash
   cat > ~/.tbrc << EOF
   [api_keys]
   fmp_api_key = "$FMP_API_KEY"
   EOF
   ```

3. Test that it works:
   ```bash
   unset FMP_API_KEY  # Temporarily remove env var
   duk tr --help      # Should still work
   ```

4. Remove the environment variable from your shell profile once confirmed.

## Future Extensions

The configuration system is designed to be extensible. Future versions may support:
- Additional API providers
- Advanced logging configuration
- Output format preferences
- Custom data source endpoints
- Plugin configuration settings

## Technical Details

- **Format**: TOML (Tom's Obvious, Minimal Language)
- **Python Support**: Uses `tomllib` (Python 3.11+) or `tomli` (older versions)
- **Encoding**: UTF-8
- **Merging Strategy**: Deep merge with higher priority configs overriding lower priority ones
- **Validation**: Performed at application startup before API calls