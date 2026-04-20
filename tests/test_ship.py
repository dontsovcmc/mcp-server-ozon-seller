"""Тест: ozon_ship_orders."""

import json
from unittest.mock import patch, call

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
]


@pytest.mark.anyio
async def test_ship_all():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_unfulfilled_orders.return_value = MOCK_POSTINGS
        instance.ship_posting.return_value = {"result": True}

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_ship_orders", {"posting_numbers": "all"})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["shipped"] == 1
            assert data["errors"] == 0

            instance.ship_posting.assert_called_once_with(
                "89765432-0001-1",
                [{"sku": 100500, "quantity": 1}],
            )


@pytest.mark.anyio
async def test_ship_specific():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_posting.return_value = MOCK_POSTINGS[0]
        instance.ship_posting.return_value = {"result": True}

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_ship_orders", {
                "posting_numbers": "89765432-0001-1",
            })
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["shipped"] == 1

            instance.get_posting.assert_called_once_with("89765432-0001-1")


@pytest.mark.anyio
async def test_ship_error():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_unfulfilled_orders.return_value = MOCK_POSTINGS
        instance.ship_posting.side_effect = RuntimeError("API error")

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_ship_orders", {"posting_numbers": "all"})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["shipped"] == 0
            assert data["errors"] == 1
            assert "API error" in data["results"][0]["error"]
