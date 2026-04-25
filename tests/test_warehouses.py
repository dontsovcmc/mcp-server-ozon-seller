"""Тест: ozon_warehouse_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Warehouse, DeliveryMethod

MOCK_WAREHOUSE = {"warehouse_id": 22222, "name": "Склад FBS Москва", "is_rfbs": False, "status": "active"}
MOCK_DELIVERY = {"id": 333, "name": "Курьер Ozon", "warehouse_id": 22222, "status": "active"}


@pytest.mark.anyio
async def test_warehouse_list():
    Warehouse.model_validate(MOCK_WAREHOUSE)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.warehouse_list.return_value = {"result": [MOCK_WAREHOUSE]}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_warehouse_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_delivery_methods():
    DeliveryMethod.model_validate(MOCK_DELIVERY)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.delivery_methods.return_value = {"result": {"items": [MOCK_DELIVERY]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_warehouse_delivery_methods", {})
            assert not result.isError
