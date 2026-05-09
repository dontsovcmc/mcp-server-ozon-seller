"""MCP server for Ozon Seller API."""

import sys

__version__ = "0.3.1"


def main():
    # Parse --env before dispatching (both MCP and CLI modes)
    if "--env" in sys.argv:
        idx = sys.argv.index("--env")
        if idx + 1 < len(sys.argv):
            env_path = sys.argv[idx + 1]
            sys.argv = sys.argv[:idx] + sys.argv[idx + 2:]
            from .cli import _load_env
            _load_env(env_path)

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
