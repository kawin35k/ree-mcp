# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

REE MCP Server: A production-ready MCP (Model Context Protocol) server for accessing Red Eléctrica Española (REE) electricity data through the eSios API. Built with strict Domain-Driven Design (DDD) principles, Clean Architecture, and comprehensive testing.

**Key Constraint**: This codebase follows a NO MOCKING policy in the domain layer. Domain logic must remain pure and testable without mocks.

## Development Commands

### Environment Setup
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Using standard pip
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run only unit tests (domain layer)
pytest tests/unit/

# Run integration tests (infrastructure with mocked HTTP)
pytest tests/integration/

# Run e2e tests
pytest tests/e2e/

# Run with coverage report
pytest --cov=src/ree_mcp --cov-report=html

# Run specific test file
pytest tests/unit/domain/test_value_objects.py

# Run specific test function
pytest tests/unit/domain/test_value_objects.py::test_indicator_id_validation
```

### Type Checking
```bash
# Type check entire codebase (mypy strict mode enabled)
mypy src/ree_mcp/

# Type check specific module
mypy src/ree_mcp/domain/
```

### Linting and Formatting
```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code (line length: 100)
ruff format .
```

### Running the Server
```bash
# STDIO mode (default for MCP)
python -m ree_mcp

# HTTP mode for testing/debugging
python -c "from ree_mcp.interface.mcp_server import mcp; mcp.run(transport='http', port=8000)"
```

## Architecture Overview

This project implements **Clean Architecture** with **Domain-Driven Design (DDD)** in four distinct layers:

### 1. Domain Layer (`src/ree_mcp/domain/`)
**Pure business logic with ZERO external dependencies. No I/O, no frameworks, no mocking in tests.**

- **Value Objects** (`value_objects/`): Immutable domain concepts
  - `IndicatorId`: Strongly-typed IDs with validation (must be > 0)
  - `DateTimeRange`: Date ranges with business rules (max 366 days, start < end)
  - `TimeGranularity`: Enum for aggregation levels (raw/hour/day/fifteen_minutes)
  - `MeasurementUnit`: Power (MW), Price (€/MWh), Emissions (tCO₂eq)
  - `GeographicScope`: Peninsular, National, Canarias, etc.

- **Entities** (`entities/`): Business objects with identity
  - `Indicator`: Electricity indicator with metadata + helper methods (is_demand, is_generation)
  - `IndicatorValue`: Single time-series data point
  - `IndicatorData`: **Aggregate Root** - indicator + values + computed statistics

- **Repository Interface** (`repositories/`): Abstract contract defined in domain
  - `IndicatorRepository`: Interface for data access (implemented in infrastructure)

- **Domain Exceptions** (`exceptions.py`): Business rule violations
  - `InvalidIndicatorIdError`, `InvalidDateRangeError`
  - `IndicatorNotFoundError`, `NoDataAvailableError`

**Critical Rule**: Domain tests (`tests/unit/domain/`) test pure logic without mocks, HTTP, or external dependencies.

### 2. Application Layer (`src/ree_mcp/application/`)
**Orchestrates domain objects to fulfill use cases. Depends only on domain.**

- **Use Cases** (`use_cases/`): Business workflows
  - `GetIndicatorDataUseCase`: Fetch time-series data via repository
  - `ListIndicatorsUseCase`: Retrieve all indicators
  - `SearchIndicatorsUseCase`: Find indicators by keyword

- **DTOs** (`dtos/`): Data Transfer Objects for boundaries
  - `GetIndicatorDataRequest`: Input validation with Pydantic
  - `IndicatorDataResponse`: Structured output
  - Uses Pydantic for validation and serialization

### 3. Infrastructure Layer (`src/ree_mcp/infrastructure/`)
**Implements domain interfaces. Handles external dependencies.**

- **HTTP Client** (`http/ree_api_client.py`):
  - Async httpx client with context manager
  - **Exponential backoff retry** for transient failures (HTTP 500, timeouts)
  - Configurable via Settings (timeout, max_retries, backoff_factor)

- **Repository Implementation** (`repositories/ree_indicator_repository.py`):
  - Implements `IndicatorRepository` interface
  - Maps API responses to domain entities
  - Handles data parsing and transformation

- **Configuration** (`config/settings.py`):
  - Pydantic-settings for type-safe env config
  - Loads from `.env` file with defaults
  - Required: `REE_API_TOKEN`
  - Optional: `REE_API_BASE_URL`, `REQUEST_TIMEOUT`, `MAX_RETRIES`, `RETRY_BACKOFF_FACTOR`

**Integration Tests** (`tests/integration/`): Test infrastructure with mocked HTTP (pytest-httpx).

### 4. Interface Layer (`src/ree_mcp/interface/`)
**Exposes domain functionality via MCP protocol.**

- **MCP Server** (`mcp_server.py`): FastMCP integration
  - **6 MCP Tools**: `get_indicator_data`, `list_indicators`, `search_indicators`, `get_demand_summary`, `get_generation_mix`
  - **2 MCP Resources**: `ree://indicators`, `ree://indicators/{id}`
  - Dependency injection via `_get_repository()`
  - Comprehensive error handling (DomainException → JSON errors)

## Key Design Principles

### Dependency Inversion Principle (DIP)
- Domain defines `IndicatorRepository` interface
- Infrastructure implements the interface
- Application depends on domain abstraction, NOT concrete implementation
- High-level modules (domain) never depend on low-level modules (infrastructure)

### Repository Pattern
- Domain defines "what" (interface)
- Infrastructure defines "how" (implementation)
- Enables swapping implementations (e.g., switch from REE API to database)

### Value Objects
- Immutable (frozen dataclasses)
- Self-validating (validation in `__post_init__`)
- Examples: `IndicatorId(42)` raises `InvalidIndicatorIdError` if < 1

### Aggregate Roots
- `IndicatorData` is an aggregate root
- Ensures consistency boundary for indicator + values + statistics
- Single entry point for data access

## Testing Strategy

### Unit Tests (`tests/unit/domain/`)
**Test domain logic in isolation. NO mocking allowed.**

- `test_value_objects.py`: 26 tests
  - Validation (invalid IDs raise errors)
  - Conversions (to_api_params, from_iso_string)
  - Factory methods (last_n_days, last_n_hours)
  - Enum parsing

- `test_entities.py`: 15 tests
  - Entity equality (by ID)
  - Business methods (is_demand_indicator, is_generation_indicator)
  - Statistics (min, max, avg)
  - Geographic filtering

### Integration Tests (`tests/integration/infrastructure/`)
**Test infrastructure with mocked HTTP (pytest-httpx).**

- `test_ree_api_client.py`: 10 tests
  - Successful API calls
  - Error handling (404, 500, timeouts)
  - Retry logic with exponential backoff
  - Context manager usage

### E2E Tests (`tests/e2e/`)
**Test complete workflows end-to-end.**

- `test_mcp_server.py`: 8 tests
  - All MCP tool invocations
  - Error scenarios
  - Real API tests (marked for manual execution)

**Coverage**: 59 tests covering all layers.

## Configuration Management

### Environment Variables (`.env` file)
```env
REE_API_TOKEN=your_token_here          # Required
REE_API_BASE_URL=https://api.esios.ree.es  # Optional
REQUEST_TIMEOUT=30                     # Optional
MAX_RETRIES=3                          # Optional
RETRY_BACKOFF_FACTOR=0.5              # Optional
```

**Security**: `.env` is gitignored. Use `.env.example` as template.

### Settings Class (`settings.py`)
- Uses Pydantic-settings for type-safe config
- Cached via `@lru_cache` in `get_settings()`
- Field validation (e.g., timeout: 1-300 seconds)

## Common Patterns

### Adding a New Use Case
1. Define DTO in `application/dtos/` (request + response)
2. Create use case in `application/use_cases/` (depends on repository interface)
3. Add MCP tool in `interface/mcp_server.py`
4. Write unit tests (domain logic) + e2e test (tool invocation)

### Adding a New Domain Concept
1. Create value object or entity in `domain/`
2. Add validation in `__post_init__`
3. Write unit tests (validation, equality, methods)
4. NO external dependencies allowed in domain

### Error Handling Pattern
```python
try:
    # Use case execution
    response = await use_case.execute(request)
    return response.model_dump_json(indent=2)
except DomainException as e:
    return json.dumps({"error": str(e), "type": type(e).__name__}, indent=2)
except Exception as e:
    return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
```

## Important Indicator IDs

Commonly used indicators from the REE API (1,967+ total available):

### Demand
- `1293`: Real Demand (Peninsular) - MW, 5 min
- `2037`: Real National Demand - MW, 5 min
- `1292`: Demand Forecast - MW, hourly

### Generation
- `549`: Nuclear - MW, 5 min
- `2038`: Wind (National) - MW, 5 min
- `1295`: Solar PV (Peninsular) - MW, 5 min
- `2041`: Combined Cycle (National) - MW, 5 min
- `2042`: Hydroelectric (National) - MW, 5 min

### Prices
- `600`: SPOT Market Price - €/MWh, 15 min
- `1013`: PVPC Rate - €/MWh, hourly

### Emissions
- `10355`: CO₂ Emissions - tCO₂eq, 5 min

See `ree_docs.md` for complete indicator reference (gitignored).

## MCP Tools Reference

### `get_indicator_data`
Fetch time-series data for any indicator.
```python
await get_indicator_data(
    indicator_id=1293,           # Required: REE indicator ID
    start_date="2025-10-08T00:00",  # Required: ISO format
    end_date="2025-10-08T23:59",    # Required: ISO format
    time_granularity="hour"      # Optional: raw/hour/day/fifteen_minutes
)
```

### `list_indicators`
List all 1,967+ available indicators with pagination.
```python
await list_indicators(limit=50, offset=0)
```

### `search_indicators`
Search indicators by keyword.
```python
await search_indicators("demanda", limit=20)
```

### `get_demand_summary`
Convenience tool for demand data.
```python
await get_demand_summary("2025-10-08")
```

### `get_generation_mix`
Get generation breakdown by source.
```python
await get_generation_mix(date="2025-10-08", hour="12")
```

## Code Quality Standards

- **Type Safety**: mypy strict mode (100% type-annotated)
- **Line Length**: 100 characters (ruff configured)
- **Testing**: All new code requires tests (unit + integration/e2e)
- **No Mocking**: Domain tests must be pure (no mocks/stubs)
- **Immutability**: Value objects are frozen dataclasses
- **Validation**: All inputs validated (Pydantic for DTOs, domain for value objects)

## Tools Configuration

### pytest (`pyproject.toml`)
- `asyncio_mode = "auto"`: Automatic async test detection
- Coverage enabled by default
- Testpaths: `["tests"]`

### mypy
- Strict mode enabled
- Python 3.11+ target
- `fastmcp` imports ignored (no type stubs)

### ruff
- Selects: pycodestyle, pyflakes, isort, flake8-bugbear, comprehensions, pyupgrade
- Per-file ignores: tests can use asserts (S101)

## Installation Script

Use `./INSTALL_COMMAND.sh` to add server to Claude Code:
- Reads `REE_API_TOKEN` from `.env`
- Runs `claude mcp add-json` with proper configuration
- Verifies token exists before proceeding
