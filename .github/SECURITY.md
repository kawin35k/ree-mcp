# Security Policy

## Supported Versions

As a hobby project, only the latest version receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project:

1. **DO NOT** open a public issue
2. Email: [Your contact] or open a private security advisory on GitHub
3. Provide details about the vulnerability and steps to reproduce

### What to Expect

- **Response Time**: Best effort (this is a hobby project)
- **Fix Timeline**: No guaranteed timeline, but critical issues will be prioritized
- **Disclosure**: We follow responsible disclosure practices

## Security Best Practices

### For Users

1. **Never commit API tokens**: Always use `.env` files (already in `.gitignore`)
2. **Keep dependencies updated**: Run `uv pip install -e ".[dev]"` regularly
3. **Review configuration**: Check MCP configuration before adding to Claude Code
4. **Use latest version**: Always use the latest release for security fixes

### For Contributors

1. **No hardcoded secrets**: Use environment variables for all sensitive data
2. **Validate inputs**: All user inputs must be validated (Pydantic handles this)
3. **Follow type safety**: All code must pass `mypy --strict`
4. **Test security**: Run `bandit` before committing

## Known Limitations

This is a hobby project with the following security considerations:

1. **No security team**: Single maintainer, limited time
2. **Best effort**: Security updates on a best-effort basis
3. **Third-party dependencies**: Relies on REE API security
4. **No SLA**: No guaranteed response or fix times

## Security Features

Current security measures:

- ✅ Type safety with mypy strict mode
- ✅ Input validation with Pydantic
- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ `.env` files in `.gitignore`
- ✅ Automatic retry with exponential backoff (prevents abuse)
- ✅ CI/CD security scanning with Bandit
- ✅ Dependency scanning in CI/CD

## Disclaimer

This software is provided "as is" without any warranties. See LICENSE for full details.
