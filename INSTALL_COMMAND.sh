#!/bin/bash
# Command to add REE MCP Server to Claude Code using add-json
#
# IMPORTANT: Replace YOUR_REE_API_TOKEN_HERE with your actual API token
# You can find it in the .env file or get one from REE (consultasios@ree.es)

# Load API token from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$REE_API_TOKEN" ]; then
  echo "Error: REE_API_TOKEN not found in .env file"
  echo "Please create a .env file with: REE_API_TOKEN=your_token_here"
  exit 1
fi

claude mcp add-json ree-mcp "{
  \"command\": \"$(pwd)/venv/bin/python\",
  \"args\": [\"-m\", \"ree_mcp\"],
  \"env\": {
    \"REE_API_TOKEN\": \"$REE_API_TOKEN\"
  }
}"

echo ""
echo "✅ REE MCP Server added to Claude Code!"
echo "Please restart Claude Code to load the server."
echo ""
echo "To verify, run: claude mcp list"
