# ⚡ REE MCP Server

<div align="center">

[![CI/CD](https://github.com/ESJavadex/ree-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/ESJavadex/ree-mcp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

</div>

> Talk to Spain's electricity grid through Claude - no API knowledge required

A production-ready **MCP (Model Context Protocol)** server that lets you query Spanish electricity data using natural language. Ask Claude about demand, generation, prices, and emissions - it handles all the technical details.

Built with **Domain-Driven Design**, **Clean Architecture**, and **comprehensive testing** by [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/) - AI & Robotics Specialist with published research in computer vision and LLM interpretability.

---

## 🎯 Why This Exists

**Red Eléctrica de España (REE)** manages Spain's electricity grid 24/7, publishing data every 5 minutes. This MCP server makes that data accessible through natural conversation with Claude.

### Why I Built This

*By [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)*

I wanted to **democratize access** to critical infrastructure data. Instead of writing Python scripts, I wanted conversations like this:

**You:** *"Check what happened on April 28, 2025"*

**Claude:** *Analyzes grid data...*

🚨 **CRITICAL EVENT DETECTED - April 28, 2025 at 12:35h**

**Massive Grid Collapse:**
- **11,000 MW lost in 5 minutes** (43% capacity drop)
- System fell from 25,184 MW → 14,185 MW instantly
- Compatible with cascading blackout scenario
- Recovery took 10+ hours

**Analysis:**
- 11:00-12:30: System stable, no warnings
- 12:30-12:35: Catastrophic instantaneous failure
- 12:35-13:35: Continued degradation to 9,635 MW minimum
- Likely cause: Nuclear plant trip → frequency collapse → cascade

*This would be one of Spain's worst blackouts in modern history.*

---

**That's the power of this MCP server.** You can investigate grid events, analyze renewable vs fossil generation trends, correlate prices with demand, or track Spain's decarbonization progress - all through natural conversation with Claude.

No API documentation. No Python scripts. Just ask.

---

## 🚀 Quick Start

Get up and running in 3 minutes:

### 1️⃣ Clone & Install

```bash
# Clone the repository
git clone https://github.com/ESJavadex/ree-mcp.git
cd ree-mcp

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on macOS: brew install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2️⃣ Configure API Token

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your token (demo token included for testing)
# REE_API_TOKEN=your_token_here
```

**Getting an API Token:**
- **Testing/Demo**: The repository includes a demo token in `.env.example`
- **Production**: Email consultasios@ree.es to request your own REE API token

### 3️⃣ Add to Claude Code

```bash
# Run the installation script (reads token from .env automatically)
./INSTALL_COMMAND.sh

# Verify installation
claude mcp list
```

You should see `ree-mcp: ✓ Connected` in the output.

### 4️⃣ Start Using in Claude!

Open Claude Code and try:
- *"Show me the current electricity demand in Spain"*
- *"What's the generation mix right now?"*
- *"Compare solar vs wind generation today"*
- *"Search for price indicators"*

---

## 💬 What Can You Ask Claude?

Once installed, Claude can answer questions like:

### 📊 Grid Operations
- *"What's Spain's electricity demand right now?"*
- *"Show me the generation mix at noon yesterday"*
- *"How much power did Spain export last Tuesday?"*
- *"Compare demand today vs last week"*

### 🔍 Investigation & Analysis
- *"Investigate what happened on April 28, 2025"* → Claude analyzes grid collapse events
- *"Was there any unusual activity in the grid last month?"*
- *"Find the peak demand day this year and explain why"*
- *"Analyze the correlation between wind generation and prices"*

### 🌱 Renewables & Emissions
- *"How much solar power is Spain generating?"*
- *"Compare renewable vs fossil generation this week"*
- *"What are the current CO₂ emissions?"*
- *"Show me the trend of wind power over the last 30 days"*

### 💰 Market Analysis
- *"What's the SPOT electricity price right now?"*
- *"Find the cheapest hours to consume electricity today"*
- *"Compare PVPC rates between weekdays and weekends"*
- *"When was electricity most expensive this month?"*

### 🔎 Discovery
- *"Search for all indicators related to 'nuclear'"*
- *"What data is available about hydroelectric generation?"*
- *"Show me all price-related indicators"*

Claude automatically uses the right tools, fetches the data, and presents it in context.

---

## 📖 Common Indicator IDs

Quick reference for frequently used indicators:

### ⚡ Demand
- `1293` - Real Demand (Peninsular) - *MW, 5-minute updates*
- `2037` - Real National Demand - *MW, 5-minute updates*
- `1292` - Demand Forecast - *MW, hourly*

### 🔋 Generation Sources
- `549` - Nuclear - *MW, 5-minute*
- `2038` - Wind (National) - *MW, 5-minute*
- `1295` - Solar PV (Peninsular) - *MW, 5-minute*
- `2041` - Combined Cycle (National) - *MW, 5-minute*
- `2042` - Hydroelectric (National) - *MW, 5-minute*

### 💵 Prices
- `600` - SPOT Market Price - *€/MWh, 15-minute*
- `1013` - PVPC Rate - *€/MWh, hourly*

### 🌱 Emissions
- `10355` - CO₂ Emissions - *tCO₂eq, 5-minute*

---

## 🏗️ Architecture

Built following **industry best practices**:

```
📦 ree-mcp
├── 🎯 domain/           # Pure business logic (NO external dependencies)
│   ├── entities/        # Indicator, IndicatorData, IndicatorValue
│   ├── value_objects/   # IndicatorId, DateTimeRange, TimeGranularity
│   ├── repositories/    # Abstract interfaces
│   └── exceptions.py    # Domain-specific errors
├── 🚀 application/      # Use cases & DTOs
│   ├── use_cases/       # GetIndicatorData, ListIndicators, SearchIndicators
│   └── dtos/           # Request/Response objects
├── 🔧 infrastructure/   # External dependencies
│   ├── http/           # REE API client with retry logic
│   ├── repositories/   # Repository implementations
│   └── config/         # Settings management
└── 🌐 interface/       # MCP server
    └── mcp_server.py   # FastMCP tools & resources
```

**Key Principles:**
- ✅ **Domain-Driven Design (DDD)** - Clear separation of concerns
- ✅ **Clean Architecture** - Dependencies point inward
- ✅ **SOLID Principles** - All 5 implemented
- ✅ **Type Safety** - 100% type-annotated with mypy strict mode
- ✅ **NO Mocking** - Domain tests use pure functions
- ✅ **Comprehensive Testing** - 59 tests (unit, integration, e2e)

---

## 🧪 Testing & Development

### Run Tests

```bash
# All tests
pytest

# Unit tests only (fast, no external dependencies)
pytest tests/unit/

# With coverage report
pytest --cov=src/ree_mcp --cov-report=html
```

### Code Quality

```bash
# Type checking (mypy strict mode)
mypy src/ree_mcp/

# Linting
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Run Server Standalone

```bash
# STDIO mode (for MCP)
python -m ree_mcp

# HTTP mode (for testing)
python -c "from ree_mcp.interface.mcp_server import mcp; mcp.run(transport='http', port=8000)"
```

---

## 🎓 Learn AI & Build More Projects

This project was created by **[Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)**, AI & Robotics Specialist with published research in:
- 🔬 Surgical gauze detection using Convolutional Neural Networks
- 🧠 Large Language Model interpretability in diverse knowledge scenarios

### 📚 La Escuela de IA

Want to learn AI **without the fluff** and build projects like this?

Join **[La Escuela de IA](https://skool.com/la-escuela-de-ia-9955)** - the Spanish AI learning community where you'll find:

- 🎯 **Real-world practice** - Build actual AI projects, not toy examples
- 🇪🇸 **Content in Spanish** - Finally, AI education in your language
- 🛠️ **Practical resources** - Code, tutorials, and hands-on examples
- 👥 **Active community** - Learn with other Spanish-speaking AI enthusiasts

👉 **[Join La Escuela de IA](https://skool.com/la-escuela-de-ia-9955)**

### 📺 YouTube Channel

Subscribe to **[JavadexAI](https://www.youtube.com/@JavadexAI)** for:
- 🎥 AI tutorials and project walkthroughs
- 💡 LLM applications and MCP servers
- 🚀 Real-world AI implementation strategies

### 🤝 Connect

- **LinkedIn**: [Javi Santos](https://www.linkedin.com/in/francisco-javier-santos-criado/)
- **YouTube**: [@JavadexAI](https://www.youtube.com/@JavadexAI)
- **Escuela de IA**: [skool.com/la-escuela-de-ia-9955](https://skool.com/la-escuela-de-ia-9955)

---

## ⚙️ Advanced Configuration

### Environment Variables

Create a `.env` file to customize behavior:

```env
# Required
REE_API_TOKEN=your_token_here

# Optional (defaults shown)
REE_API_BASE_URL=https://api.esios.ree.es
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=0.5
```

### Manual Claude Code Setup

If you prefer manual configuration over the installation script:

#### Option 1: Local Installation

1. Edit `.claude_mcp_config.json` with your token
2. Update the `command` path if needed
3. In Claude Code, run `/config-mcp` and paste the configuration

#### Option 2: Direct from GitHub (uvx)

1. Edit `.claude_mcp_config_uvx.json` with your token
2. In Claude Code, run `/config-mcp` and paste the configuration
3. No local installation needed - runs directly from GitHub!

---

## 🔥 Features

### 🎯 Production-Ready

- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive error handling and validation
- ✅ Type-safe configuration with Pydantic
- ✅ Async/await for optimal performance
- ✅ Context managers for proper resource cleanup

### 🧪 Well-Tested

- **59 comprehensive tests** covering all layers
- **Unit tests** - Pure domain logic (no mocks!)
- **Integration tests** - Infrastructure with mocked HTTP
- **E2E tests** - Complete workflow validation
- **High coverage** of critical paths

### 📝 Best Practices

- **Date Ranges**: Max 366 days per request
- **Data Freshness**: Use dates 3+ days old for most reliable data
- **Time Granularity**:
  - `raw` for 5-minute detail
  - `hour` for standard monitoring
  - `day` for long-term trends
- **Rate Limits**: Max ~10 requests/second (automatic retry on failures)

---

## 🤝 Contributing

Contributions are welcome! This codebase follows strict architectural principles:

- **Domain-Driven Design** - Keep domain pure, no external dependencies
- **Clean Architecture** - Respect layer boundaries
- **SOLID Principles** - Single responsibility, open/closed, etc.
- **NO Mocking in Domain** - Domain tests must be pure
- **Type Safety** - All code must pass mypy strict mode
- **Testing** - New features require tests

See `CLAUDE.md` for detailed developer guidance.

---

## 📄 License

This project is for educational and research purposes. The REE API is provided by Red Eléctrica de España.

---

## 🔗 Resources

- **REE eSios API**: https://api.esios.ree.es/
- **REE Portal**: https://www.esios.ree.es/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Model Context Protocol**: https://modelcontextprotocol.io/

---

## 💬 Support

### Issues & Questions

- **MCP Server Issues**: [Open an issue](https://github.com/ESJavadex/ree-mcp/issues)
- **REE API Questions**: consultasios@ree.es
- **FastMCP Help**: https://github.com/jlowin/fastmcp

### Learn More

- 📚 Join [La Escuela de IA](https://skool.com/la-escuela-de-ia-9955) for AI learning in Spanish
- 📺 Subscribe to [JavadexAI on YouTube](https://www.youtube.com/@JavadexAI)
- 🤝 Connect on [LinkedIn](https://www.linkedin.com/in/francisco-javier-santos-criado/)

---

<div align="center">

**Built with ❤️ using Domain-Driven Design and modern Python best practices**

⭐ Star this repo if you find it useful!

</div>
