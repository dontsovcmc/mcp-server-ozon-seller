"""Тест: ozon_barcode_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp


@pytest.mark.anyio
async def test_barcode_generate():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.barcode_generate.return_value = {"result": {"barcodes": ["4600000000001"]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_barcode_generate", {"product_ids": "12345"})
            assert not result.isError


@pytest.mark.anyio
async def test_barcode_add():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.barcode_add.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_barcode_add", {"barcodes_json": "[]"})
            assert not result.isError
