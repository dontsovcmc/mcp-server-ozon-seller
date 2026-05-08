"""MCP server for Ozon Seller API."""

import sys

__version__ = "0.3.0"


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        from .cli import main as cli_main
        cli_main()
    elif "--version" in sys.argv:
        print(f"mcp-server-ozon-seller {__version__}")
    elif len(sys.argv) == 1:
        from .server import mcp
        mcp.run(transport="stdio")
    else:
        from .cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
