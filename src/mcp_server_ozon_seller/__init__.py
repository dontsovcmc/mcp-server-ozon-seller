"""MCP server for Ozon Seller API."""

__version__ = "1.0.0"


def main():
    from .server import mcp
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
