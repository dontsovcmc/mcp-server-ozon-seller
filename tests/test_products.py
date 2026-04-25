"""Тест: ozon_product_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import ProductItem

MOCK_PRODUCT = {
    "product_id": 12345,
    "offer_id": "SKU-001",
    "name": "Тестовый товар",
    "sku": 100500,
    "barcode": "4600000000001",
    "category_id": 17028922,
    "price": "1500.00",
    "old_price": "2000.00",
    "vat": "0.1",
    "visible": True,
}


@pytest.mark.anyio
async def test_product_list():
    ProductItem.model_validate(MOCK_PRODUCT)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_list.return_value = {"result": {"items": [MOCK_PRODUCT], "total": 1, "last_id": ""}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_list", {"limit": 10})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert "result" in data


@pytest.mark.anyio
async def test_product_info():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_info.return_value = {"result": MOCK_PRODUCT}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_info", {"offer_id": "SKU-001"})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["result"]["offer_id"] == "SKU-001"


@pytest.mark.anyio
async def test_product_info_list():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_info_list.return_value = {"result": {"items": [MOCK_PRODUCT]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_info_list", {"offer_ids": "SKU-001"})
            assert not result.isError


@pytest.mark.anyio
async def test_product_import():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_import.return_value = {"result": {"task_id": 999}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_import", {"items_json": "[]"})
            assert not result.isError


@pytest.mark.anyio
async def test_product_prices_update():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_prices_update.return_value = {"result": []}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_prices_update", {"prices_json": "[]"})
            assert not result.isError


@pytest.mark.anyio
async def test_product_stocks_update():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_stocks_update.return_value = {"result": []}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_stocks_update", {"stocks_json": "[]"})
            assert not result.isError


@pytest.mark.anyio
async def test_product_archive():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_archive.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_archive", {"product_ids": "12345"})
            assert not result.isError


@pytest.mark.anyio
async def test_product_delete():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.product_delete.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_product_delete", {"product_ids": "12345"})
            assert not result.isError
