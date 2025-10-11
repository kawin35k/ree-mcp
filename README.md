# REE MCP Server

A production-ready MCP (Model Context Protocol) server for accessing Red Eléctrica Española (REE) electricity data through the eSios API. Built with Domain-Driven Design principles, comprehensive testing, and modern Python best practices.

## Features

- **Complete REE API Coverage**: Access to 1,967+ electricity indicators including:
  - Real-time and forecasted demand
  - Generation by source (nuclear, wind, solar, hydro, etc.)
  - Market prices (SPOT, PVPC)
  - International exchanges
  - CO₂ emissions

- **Clean Architecture**: Implements DDD with clear separation of concerns:
  - Domain Layer: Pure business logic
  - Application Layer: Use cases and DTOs
  - Infrastructure Layer: External dependencies (API clients, repositories)
  - Interface Layer: MCP server tools and resources

- **Production Ready**:
  - Comprehensive test coverage (unit, integration, e2e)
  - Type safety with mypy strict mode
  - Automatic retry with exponential backoff
  - Error handling and validation
  - Configuration management with pydantic-settings

## Architecture

```
src/ree_mcp/
├── domain/              # Pure business logic
│   ├── entities/        # Indicator, IndicatorValue, IndicatorData
│   ├── value_objects/   # IndicatorId, DateTimeRange, etc.
│   ├── repositories/    # Repository interfaces
│   └── exceptions.py    # Domain exceptions
├── application/         # Use cases
│   ├── dtos/           # Request/Response DTOs
│   └── use_cases/      # GetIndicatorData, ListIndicators, etc.
├── infrastructure/      # External dependencies
│   ├── http/           # REE API client with retry logic
│   ├── repositories/   # Repository implementations
│   └── config/         # Settings management
└── interface/          # MCP server
    └── mcp_server.py   # FastMCP tools and resources
```

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)
- REE API token (already configured in `.env`)

### Setup with uv (Recommended)

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on macOS: brew install uv
```

2. Navigate to the project directory:
```bash
cd /Users/javier.santos/javi-proyectos/ree-mcp
```

3. Create virtual environment and install dependencies with uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

4. Verify installation:
```bash
pytest tests/unit/
```

### Alternative Setup (Standard pip)

If you prefer traditional pip:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Claude Code Setup

### Prerequisites

Before configuring Claude Code, ensure you have:
1. **API Token**: Create a `.env` file in the project root with your REE API token:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your token
   # REE_API_TOKEN=your_actual_token_here
   ```

2. **Installation**: Complete the installation steps above (uv or pip)

### Quick Setup (Recommended)

The easiest way to add the server is using the provided installation script:

```bash
# The script automatically reads the API token from .env
./INSTALL_COMMAND.sh
```

This script will:
- Load the API token from your `.env` file
- Add the MCP server to Claude Code using `claude mcp add-json`
- Configure all necessary environment variables

**Important**: Make sure your `.env` file exists with a valid `REE_API_TOKEN` before running the script.

### Manual Configuration

If you prefer manual setup, we provide two configuration templates in the repository:

#### Option 1: Local Installation (`.claude_mcp_config.json`)

For local development using your virtual environment:

1. Copy your API token from the `.env` file
2. Edit `.claude_mcp_config.json` and replace `YOUR_REE_API_TOKEN_HERE` with your actual token
3. Update the `command` path if your installation directory is different
4. Use `/config-mcp` in Claude Code to load the configuration

#### Option 2: Direct from GitHub with uvx (`.claude_mcp_config_uvx.json`)

For running directly from GitHub without local installation:

1. Edit `.claude_mcp_config_uvx.json` and replace `YOUR_REE_API_TOKEN_HERE` with your token from `.env`
2. Replace `YOUR_USERNAME` with your GitHub username (once published)
3. Use `/config-mcp` in Claude Code to load the configuration

**Security Note**: Never commit configuration files with actual API tokens to version control. The template files in this repository use placeholders that you should replace with your actual token from the `.env` file.

### Environment Variables

Configure the server behavior with these environment variables in the `env` section:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REE_API_TOKEN` | REE API authentication token | - | ✅ Yes |
| `REE_API_BASE_URL` | Base URL for REE API | `https://api.esios.ree.es` | No |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` | No |
| `MAX_RETRIES` | Maximum retry attempts | `3` | No |
| `RETRY_BACKOFF_FACTOR` | Exponential backoff factor | `0.5` | No |

### Getting Your API Token

1. **For Development/Testing**: A demo token is included in the repository's `.env` file
2. **For Production**: Contact REE (consultasios@ree.es) to request your own API token for eSios API
3. **Setup**: Store your token in the `.env` file (never commit this file to version control)

```bash
# .env file (already in .gitignore)
REE_API_TOKEN=your_actual_token_here
```

Use the provided `.env.example` as a template.

## Usage

### Running the MCP Server Standalone

#### STDIO Mode (Default)
```bash
python -m ree_mcp
```

#### HTTP Mode (for testing)
```bash
python -c "from ree_mcp.interface.mcp_server import mcp; mcp.run(transport='http', port=8000)"
```

### Available Tools

#### 1. `get_indicator_data`
Get time-series data for any REE indicator.

```python
# Get hourly real demand for Oct 8, 2025
await get_indicator_data(
    indicator_id=1293,
    start_date="2025-10-08T00:00",
    end_date="2025-10-08T23:59",
    time_granularity="hour"
)

# Get 5-minute wind generation
await get_indicator_data(
    indicator_id=2038,
    start_date="2025-10-08T00:00",
    end_date="2025-10-08T03:00",
    time_granularity="raw"
)
```

**Parameters:**
- `indicator_id` (int): Indicator ID from REE API
- `start_date` (str): Start datetime (ISO format: YYYY-MM-DDTHH:MM)
- `end_date` (str): End datetime (ISO format)
- `time_granularity` (str): `raw`, `hour`, `day`, or `fifteen_minutes` (default: `raw`)

#### 2. `list_indicators`
List all available indicators with pagination.

```python
# Get first 50 indicators
await list_indicators(limit=50, offset=0)

# Get all indicators
await list_indicators()
```

#### 3. `search_indicators`
Search indicators by keyword.

```python
# Find demand indicators
await search_indicators("demanda", limit=10)

# Find price indicators
await search_indicators("precio")

# Find solar generation
await search_indicators("solar")
```

#### 4. `get_demand_summary`
Get demand summary for a specific date (convenience tool).

```python
await get_demand_summary("2025-10-08")
```

#### 5. `get_generation_mix`
Get electricity generation breakdown by source at a specific time.

```python
# Get generation mix at noon
await get_generation_mix(date="2025-10-08", hour="12")

# Get overnight generation
await get_generation_mix(date="2025-10-08", hour="02")
```

### Available Resources

#### `ree://indicators`
Get complete list of all indicators.

#### `ree://indicators/{indicator_id}`
Get metadata for a specific indicator.

## Common Indicator IDs

| ID | Name | Unit | Frequency |
|----|------|------|-----------|
| **Demand** |||
| 1293 | Real Demand | MW | 5 min |
| 2037 | Real National Demand | MW | 5 min |
| 1292 | Demand Forecast | MW | Hour |
| **Generation - Synchronous** |||
| 549 | Nuclear | MW | 5 min |
| 2041 | Combined Cycle (National) | MW | 5 min |
| 2042 | Hydroelectric (National) | MW | 5 min |
| 547 | Coal | MW | 5 min |
| **Generation - Renewables** |||
| 2038 | Wind (National) | MW | 5 min |
| 1295 | Solar PV (Peninsular) | MW | 5 min |
| 2044 | Solar PV (National) | MW | 5 min |
| 1294 | Solar Thermal (Peninsular) | MW | 5 min |
| **Prices** |||
| 600 | SPOT Market Price | €/MWh | 15 min |
| 1013 | PVPC Rate | €/MWh | Hour |
| **Emissions** |||
| 10355 | CO₂ Emissions | tCO₂eq | 5 min |
| **Exchanges** |||
| 2072 | Total Exports | MW | 5 min |
| 2077 | Total Imports | MW | 5 min |

See `ree_docs.md` for complete indicator reference.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src/ree_mcp --cov-report=html

# Run integration tests (requires API)
pytest -m integration
```

### Type Checking

```bash
mypy src/ree_mcp/
```

### Linting and Formatting

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Project Structure

The project follows Clean Architecture and DDD principles:

- **Domain Layer**: Contains business entities, value objects, and interfaces. No external dependencies.
- **Application Layer**: Implements use cases that orchestrate domain objects.
- **Infrastructure Layer**: Implements repository interfaces and handles external API calls.
- **Interface Layer**: Exposes MCP tools and resources using FastMCP.

### Adding New Indicators

1. Check `ree_docs.md` for indicator ID and details
2. Use existing tools (`get_indicator_data`) - no code changes needed
3. Optionally add convenience wrapper in `mcp_server.py` (like `get_demand_summary`)

## Configuration

Configuration is managed through environment variables (`.env` file):

```env
REE_API_TOKEN=your_api_token_here
REE_API_BASE_URL=https://api.esios.ree.es
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=0.5
```

## Error Handling

The server implements comprehensive error handling:

- **Domain Errors**: `InvalidIndicatorIdError`, `InvalidDateRangeError`, `IndicatorNotFoundError`, `NoDataAvailableError`
- **Infrastructure Errors**: Automatic retry on transient failures (HTTP 500, timeouts)
- **Validation Errors**: Pydantic validation for all inputs

All errors are returned as JSON with descriptive messages.

## API Rate Limits

- No official rate limits documented by REE
- Recommended: Max 10 requests per second
- The client implements automatic retry with exponential backoff

## Best Practices

1. **Date Ranges**:
   - Maximum 366 days per request
   - Use dates 3+ days old for most reliable data
   - Recent data may not be finalized

2. **Time Granularity**:
   - Use `raw` for detailed 5-minute data
   - Use `hour` for standard monitoring
   - Use `day` for long-term trends

3. **Indicator Selection**:
   - Prefer "T.Real" (real-time) indicators
   - Use `search_indicators` to find relevant indicators
   - Check `ree_docs.md` for full catalog

## Testing

The project includes three levels of testing:

- **Unit Tests** (`tests/unit/`): Test domain logic in isolation
- **Integration Tests** (`tests/integration/`): Test infrastructure with mocked HTTP
- **E2E Tests** (`tests/e2e/`): Test complete workflows

All tests use pytest and achieve high coverage of critical paths.

## Contributing

This is a production-ready implementation following industry best practices:

- Domain-Driven Design (DDD)
- SOLID principles
- Clean Architecture
- Type safety (mypy strict)
- Comprehensive testing
- No mocking in domain layer (pure functions)

## License

This project is for educational and research purposes. The REE API is provided by Red Eléctrica de España.

## Resources

- **REE eSios API**: https://api.esios.ree.es/
- **REE Portal**: https://www.esios.ree.es/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **API Documentation**: See `ree_docs.md`

## Support

For issues with:
- **This MCP Server**: Open an issue in this repository
- **REE API**: Contact consultasios@ree.es
- **FastMCP**: See https://github.com/jlowin/fastmcp

---

Built with ❤️ using Domain-Driven Design and modern Python best practices.
