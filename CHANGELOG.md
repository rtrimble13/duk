# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Contributor-facing trust files (CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md)
- Documentation index (doc/index.md)

## [0.2.0] - 2024-12-XX

### Added
- Initial implementation of duk CLI tool and library
- `get_price_history()` function for retrieving historical price data
- `get_yield_curve()` function for retrieving yield curve data
- CLI commands:
  - `duk ls`: List securities, sectors, and industries
  - `duk ph`: Get historical price data
  - `duk yc`: Get yield curve data
- Configuration file support (`~/.dukrc`)
- Environment variable support for API keys
- Flexible output formats (CSV and JSON)
- Data resampling for different frequencies (day, week, month, quarter, semi-annual, annual)
- Field selection for price history data
- Comprehensive logging system
- Unit test suite with pytest
- Documentation for all commands and functions

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Secure API key handling through environment variables and configuration files
- Input validation for all user inputs
- API response validation

## Version History

- [0.2.0] - Initial public release

---

## Changelog Guidelines

### Types of Changes

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

### Version Format

Versions follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### How to Update This File

When making changes to the project:

1. Add your changes under the `[Unreleased]` section
2. Categorize changes appropriately (Added, Changed, Fixed, etc.)
3. Provide clear, concise descriptions
4. Include issue/PR numbers when applicable
5. When releasing, move items from Unreleased to a new version section

### Example Entry Format

```markdown
### Added
- New `transform` command for data transformations (#123)
- Support for additional data providers (#124)

### Fixed
- Fixed date parsing issue in yield curve data (#125)
- Corrected CSV output formatting for special characters (#126)
```

[Unreleased]: https://github.com/rtrimble13/duk/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/rtrimble13/duk/releases/tag/v0.2.0
