"""Shared MCP instance and helpers for Ozon Seller tools."""

import json
import logging
import os
import sys
import tempfile

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

mcp = FastMCP(
    "ozon-seller",
    instructions=(
        "Ozon Seller API server. "
        "Use ozon_search to discover available actions and their parameter schemas. "
        "Use ozon_execute to run actions by ID. "
        "Use ozon_execute_file for actions that download files (labels, acts, reports)."
    ),
)

_api = None


def _get_api():
    global _api
    if _api is None:
        from .ozon_api import OzonSellerAPI

        client_id = os.getenv("OZON_CLIENT_ID")
        api_key = os.getenv("OZON_API_KEY")
        if not client_id or not api_key:
            raise RuntimeError(
                "OZON_CLIENT_ID and OZON_API_KEY environment variables are required"
            )
        timeout = int(os.getenv("OZON_TIMEOUT", "30"))
        file_timeout = int(os.getenv("OZON_FILE_TIMEOUT", "60"))
        _api = OzonSellerAPI(client_id, api_key, timeout=timeout, file_timeout=file_timeout)
    return _api


def _to_json(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def _parse_json(raw: str, label: str) -> dict:
    """Parse JSON string with a user-friendly error message."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError(f"Invalid JSON in {label}: {exc}") from exc


def _safe_output_path(path: str) -> str:
    """Validate and resolve file path for writing.

    Only allows paths under home directory or system temp.
    Rejects dotfiles/dotdirs under home.
    """
    real = os.path.realpath(os.path.expanduser(path))
    home = os.path.realpath(os.path.expanduser("~"))
    tmp = os.path.realpath(tempfile.gettempdir())

    if not (real.startswith(home + os.sep) or real.startswith(tmp + os.sep) or real == tmp):
        raise RuntimeError(f"Path not allowed: {path}. Only home directory or temp allowed.")

    if real.startswith(home + os.sep):
        relative = real[len(home):]
        if os.sep + "." in relative:
            raise RuntimeError(f"Writing to dotfiles/dotdirs is not allowed: {path}")

    return real


def _save_bytes(data: bytes, path: str) -> str:
    safe = _safe_output_path(path)
    os.makedirs(os.path.dirname(safe) or ".", exist_ok=True)
    with open(safe, "wb") as f:
        f.write(data)
    return _to_json({"path": safe, "size": len(data)})
