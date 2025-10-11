"""Main entry point for REE MCP Server."""

from .interface.mcp_server import mcp


def main() -> None:
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
