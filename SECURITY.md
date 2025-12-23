# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2.0 | :x:                |

## Reporting a Vulnerability

The duk team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **GitHub Security Advisories** (Preferred):
   - Navigate to the repository's [Security tab](https://github.com/rtrimble13/duk/security)
   - Click "Report a vulnerability"
   - Fill out the form with details about the vulnerability

2. **Email**:
   - Send an email to the project maintainer
   - Include "SECURITY" in the subject line
   - Provide detailed information about the vulnerability

### What to Include

Please include as much of the following information as possible:

- **Type of vulnerability** (e.g., injection, authentication bypass, data exposure)
- **Full paths of affected source file(s)**
- **Location of the affected code** (tag/branch/commit or direct URL)
- **Step-by-step instructions to reproduce the issue**
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit it
- **Any potential mitigations** you've identified

### What to Expect

After you submit a vulnerability report, you can expect:

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 3 business days
- **Status updates**: We will provide status updates on the progress of addressing the vulnerability
- **Resolution timeline**: We aim to resolve critical vulnerabilities within 30 days
- **Credit**: If you wish, we will credit you for the discovery in our security advisory

### Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our services
- Only interact with accounts you own or with explicit permission of the account holder
- Do not exploit a security issue for any reason (this includes demonstrating additional risk)
- Report vulnerabilities to us before disclosing them publicly

We will not pursue legal action against security researchers who follow these guidelines.

## Security Best Practices for Users

### API Key Management

**Never commit API keys to source control**:

- Use environment variables for API keys:
  ```bash
  export FMP_API_KEY="your_api_key_here"
  ```

- Or use the configuration file with restricted permissions:
  ```bash
  chmod 600 ~/.dukrc
  ```

- Add `.dukrc` and any files containing secrets to `.gitignore`

### Configuration File Security

The default configuration file `~/.dukrc` may contain sensitive information:

- Set restrictive permissions: `chmod 600 ~/.dukrc`
- Do not share your configuration file
- Do not commit configuration files with real credentials

### Dependencies

Keep your dependencies up to date:

```bash
pip install --upgrade duk
```

### Log Files

Log files may contain sensitive information:

- Regularly review log files in `var/duk/log/`
- Set appropriate permissions on log directories
- Do not share log files publicly without reviewing their contents

## Known Security Considerations

### API Key Exposure

- API keys are passed as parameters to API functions
- Ensure API keys are not logged at INFO level (only at DEBUG level if needed)
- API keys should never appear in error messages or output files

### Data Validation

- All user inputs are validated before processing
- Date formats are strictly validated
- API responses are validated before processing

### Dependency Security

We use the following practices to maintain secure dependencies:

- Regular dependency updates
- Security scanning of dependencies
- Minimal dependency footprint

## Disclosure Policy

When we receive a security vulnerability report:

1. We will confirm the vulnerability and determine its severity
2. We will develop and test a fix
3. We will release a security advisory and patch
4. We will credit the reporter (unless they wish to remain anonymous)

Public disclosure will be made:

- After a fix is available
- At least 30 days after the initial report (unless agreed otherwise)
- Coordinated with the reporter when possible

## Comments on This Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue.

## Security Updates

Subscribe to security updates:

- Watch the repository for security advisories
- Check the [CHANGELOG](CHANGELOG.md) for security-related updates
- Follow release notes for security patches

Thank you for helping keep duk and its users safe!
