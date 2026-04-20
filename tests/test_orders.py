"""Тест: ozon_unfulfilled_orders."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp

MOCK_POSTINGS = [
    {
        "posting_number": "89765432-0001-1",
        "order_number": "89765432-0001",
        "status": "awaiting_packaging",
        "shipment_date": "2026-04-21T10:00:00Z",
        "products": [
            {"name": "Ватериус WiFi", "sku": 100500, "quantity": 1, "offer_id": "WTR-WIFI-01"},
        ],
    },
    {
        "posting_number": "89765432-0002-1",
        "order_number": "89765432-0002",
        "status": "awaiting_packaging",
        "shipment_date": "2026-04-21T10:00:00Z",
        "products": [
            {"name": "Ватериус WiFi", "sku": 100500, "quantity": 1, "offer_id": "WTR-WIFI-01"},
            {"name": "Адаптер 1/2", "sku": 100501, "quantity": 2, "offer_id": "WTR-ADAPT-12"},
        ],
    },
]


@pytest.mark.anyio
async def test_unfulfilled_orders():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_unfulfilled_orders.return_value = MOCK_POSTINGS

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_unfulfilled_orders", {})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["count"] == 2
            assert data["postings"][0]["posting_number"] == "89765432-0001-1"
            assert data["postings"][1]["products"][1]["name"] == "Адаптер 1/2"


@pytest.mark.anyio
async def test_unfulfilled_orders_empty():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_unfulfilled_orders.return_value = []

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_unfulfilled_orders", {})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["count"] == 0
