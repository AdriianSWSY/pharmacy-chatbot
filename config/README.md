# Configuration System

This document describes the configuration system for the AI Agent Call Assistant API.

## Overview

The application uses a hierarchical configuration system that supports multiple environments (development, staging, production) with environment variable overrides.

## Configuration Structure

```
config/
├── __init__.py
├── base.py           # Base configuration classes
├── development.py    # Development environment config
├── staging.py        # Staging environment config
├── production.py     # Production environment config
├── settings.py       # Configuration factory and manager
└── README.md         # This documentation
```

## Environment Variables

The following environment variables can be used to override default configuration values:

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment name (development/staging/production) |
| `APP_NAME` | `AI Agent Call Assistant API` | Application name |
| `DEBUG` | `false` | Enable debug mode |

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server host address |
| `SERVER_PORT` | `8000` | Server port number |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warning/error) |

### Pharmacy API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PHARMACY_API_BASE_URL` | `https://67e14fb758cc6bf785254550.mockapi.io` | External pharmacy API base URL |
| `PHARMACY_API_TIMEOUT` | `30` | Request timeout in seconds |
| `PHARMACY_API_RETRY_COUNT` | `3` | Number of retry attempts |
| `PHARMACY_API_RETRY_DELAY` | `1.0` | Initial retry delay in seconds |

### Cache Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_TTL` | `3600` | Cache time-to-live in seconds |

## Environment-Specific Defaults

### Development
- Debug mode: `true`
- Log level: `debug`
- Cache TTL: `300` seconds (5 minutes)

### Staging
- Debug mode: `false`
- Log level: `info`
- Cache TTL: `1800` seconds (30 minutes)
- API timeout: `45` seconds
- Retry count: `5`

### Production
- Debug mode: `false`
- Log level: `warning`
- Cache TTL: `3600` seconds (1 hour)
- API timeout: `60` seconds
- Retry count: `5`
- Retry delay: `3.0` seconds

## Usage

### Setting Environment

Set the `ENVIRONMENT` variable to control which configuration is loaded:

```bash
# Development (default)
export ENVIRONMENT=development

# Staging
export ENVIRONMENT=staging

# Production
export ENVIRONMENT=production
```

### Overriding Specific Values

You can override any configuration value using environment variables:

```bash
# Override server port
export SERVER_PORT=9000

# Override API timeout
export PHARMACY_API_TIMEOUT=60

# Override cache TTL
export CACHE_TTL=7200
```

### Example .env Files

#### Development (.env.development)
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
CACHE_TTL=300
```

#### Staging (.env.staging)
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=info
SERVER_PORT=8000
PHARMACY_API_TIMEOUT=45
CACHE_TTL=1800
```

#### Production (.env.production)
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
SERVER_PORT=8000
PHARMACY_API_TIMEOUT=60
PHARMACY_API_RETRY_COUNT=5
CACHE_TTL=3600
```

## Security Considerations

### Sensitive Data
- Never commit sensitive data like API keys, passwords, or secrets to the repository
- Use environment variables for all sensitive configuration
- Consider using secret management systems in production

### API URLs
- The current pharmacy API URL is a mock API for development/testing
- In production, this should point to the actual pharmacy API endpoint
- API URLs should be configurable per environment

### Best Practices
1. Always use environment variables for environment-specific values
2. Provide sensible defaults in configuration classes
3. Document all configuration options
4. Validate configuration values on startup
5. Use different API endpoints for different environments
6. Keep sensitive configuration separate from code

## Adding New Configuration

To add a new configuration option:

1. Add the field to the appropriate config class in `base.py`
2. Update environment-specific configs if needed
3. Add environment variable support in `BaseConfig.from_env()`
4. Document the new variable in this README
5. Update the application code to use the new setting

Example:
```python
# In base.py
class ApiConfig(BaseModel):
    new_setting: str = Field(default="default_value", description="New setting")

# In BaseConfig.from_env()
api=ApiConfig(
    new_setting=os.getenv("NEW_SETTING", "default_value")
)
```
