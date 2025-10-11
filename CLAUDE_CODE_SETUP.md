# Adding REE MCP Server to Claude Code

This guide shows you how to add the REE MCP Server to Claude Code.

## Prerequisites

Before setting up, make sure you have:
1. A valid REE API token (get yours from consultasios@ree.es or use the demo token from .env file)
2. The MCP server installed (see main README.md)

## Method 1: Using Claude Code CLI (Recommended)

Run this command to add the server with your API key:

```bash
# First, get your API token from the .env file
source .env

# Then add the MCP server with the token
claude mcp add ree-mcp \
  --command "/Users/javier.santos/javi-proyectos/ree-mcp/venv/bin/python" \
  --arg "-m" \
  --arg "ree_mcp" \
  --env "REE_API_TOKEN=$REE_API_TOKEN" \
  --description "REE (Red Eléctrica Española) API server for Spanish electricity data"
```

**Important**: The API token is read from your `.env` file. Make sure it exists and contains `REE_API_TOKEN=your_token_here`

## Method 2: Manual Configuration

### Step 1: Locate your MCP configuration file

The configuration file is typically at:
- **macOS/Linux**: `~/.claude/mcp.json`
- **Windows**: `%APPDATA%\Claude\mcp.json`

### Step 2: Add the server configuration

Add this to your `mcp.json` file:

```json
{
  "mcpServers": {
    "ree-mcp": {
      "command": "/Users/javier.santos/javi-proyectos/ree-mcp/venv/bin/python",
      "args": ["-m", "ree_mcp"],
      "env": {
        "REE_API_TOKEN": "YOUR_REE_API_TOKEN_HERE"
      }
    }
  }
}
```

**Important**: Replace `YOUR_REE_API_TOKEN_HERE` with your actual API token from the `.env` file.

**Key Points:**
- **command**: Full path to Python in the virtual environment
- **args**: Arguments to run the server (`-m ree_mcp`)
- **env**: Environment variables, including your API token

### Step 3: Restart Claude Code

After adding the configuration, restart Claude Code to load the new MCP server.

## Verifying the Setup

Once configured, you should see "REE MCP Server" in your available MCP servers in Claude Code.

You can test it by asking Claude:
- "List the first 10 REE indicators"
- "Search for price indicators in REE"
- "Get real demand data for October 8, 2025"

## Configuration Options

You can customize the server behavior with additional environment variables:

```json
{
  "mcpServers": {
    "ree-mcp": {
      "command": "/Users/javier.santos/javi-proyectos/ree-mcp/venv/bin/python",
      "args": ["-m", "ree_mcp"],
      "env": {
        "REE_API_TOKEN": "YOUR_REE_API_TOKEN_HERE",
        "REE_API_BASE_URL": "https://api.esios.ree.es",
        "REQUEST_TIMEOUT": "30",
        "MAX_RETRIES": "3",
        "RETRY_BACKOFF_FACTOR": "0.5"
      }
    }
  }
}
```

### Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REE_API_TOKEN` | REE API authentication token | **Required** |
| `REE_API_BASE_URL` | Base URL for REE API | `https://api.esios.ree.es` |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` |
| `MAX_RETRIES` | Maximum retry attempts | `3` |
| `RETRY_BACKOFF_FACTOR` | Exponential backoff factor | `0.5` |

## Using a Different Python Installation

If you don't want to use the virtual environment, you can use your system Python:

```bash
claude mcp add ree-mcp \
  --command "python3" \
  --arg "-m" \
  --arg "ree_mcp" \
  --working-directory "/Users/javier.santos/javi-proyectos/ree-mcp" \
  --env "REE_API_TOKEN=your_token_here"
```

Make sure the dependencies are installed:
```bash
pip install -e /Users/javier.santos/javi-proyectos/ree-mcp
```

## Troubleshooting

### Server doesn't appear in Claude Code

1. Check that the path to Python is correct
2. Verify the API token is valid
3. Restart Claude Code completely
4. Check Claude Code logs for errors

### API errors

- Verify your API token is correct
- Check internet connectivity
- Ensure the REE API is accessible (not blocked by firewall)

### Permission errors

Make sure the Python binary is executable:
```bash
chmod +x /Users/javier.santos/javi-proyectos/ree-mcp/venv/bin/python
```

## Example Usage

Once configured, you can interact with the REE API through Claude Code:

**Get electricity demand:**
```
Get the real electricity demand for October 8, 2025 from 00:00 to 23:59 with hourly granularity
```

**Search indicators:**
```
Search for all indicators related to solar energy
```

**Get generation mix:**
```
Show me the electricity generation mix at noon on October 8, 2025
```

**List indicators:**
```
List the first 50 electricity indicators available in the REE API
```

## Security Note

**IMPORTANT**:
1. Your API token is stored in the `.env` file (never commit this to version control)
2. The `.env` file is already in `.gitignore` to prevent accidental commits
3. For production use, get your own API token from REE (contact: consultasios@ree.es)
4. Use the `.env.example` file as a template for setting up your token

## Support

For issues:
- **MCP Server**: Open an issue in the repository
- **REE API**: Contact consultasios@ree.es
- **Claude Code**: Check https://claude.ai/docs

---

**Need help?** Check the main README.md for more details about the server capabilities and available tools.
