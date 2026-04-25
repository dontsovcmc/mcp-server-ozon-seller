"""Тест: ozon_analytics_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import StockOnWarehouseItem

MOCK_STOCK_ITEM = {
    "sku": 100500,
    "item_code": "SKU-001",
    "item_name": "Тестовый товар",
    "free_to_sell_amount": 10,
    "promised_amount": 2,
    "reserved_amount": 1,
    "warehouse_name": "Склад Москва",
}


@pytest.mark.anyio
async def test_analytics_data():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.analytics_data.return_value = {"result": {"data": [], "totals": []}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_analytics_data", {
                "date_from": "2026-04-01",
                "date_to": "2026-04-25",
                "metrics_json": '["revenue"]',
                "dimensions_json": '["day"]',
            })
            assert not result.isError


@pytest.mark.anyio
async def test_analytics_stock_on_warehouses():
    StockOnWarehouseItem.model_validate(MOCK_STOCK_ITEM)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.analytics_stock_on_warehouses.return_value = {"result": {"rows": [MOCK_STOCK_ITEM]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_analytics_stock_on_warehouses", {})
            assert not result.isError
