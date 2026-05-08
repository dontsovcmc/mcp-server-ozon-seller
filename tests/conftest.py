"""Test fixtures for MCP server Ozon Seller."""

import os

import pytest

os.environ.setdefault("OZON_CLIENT_ID", "test-fake-client-id")
os.environ.setdefault("OZON_API_KEY", "test-fake-api-key")


@pytest.fixture(autouse=True)
def _reset_api_singleton():
    """Reset cached API instance between tests."""
    import mcp_server_ozon_seller._shared as shared
    shared._api = None
    yield
    shared._api = None
