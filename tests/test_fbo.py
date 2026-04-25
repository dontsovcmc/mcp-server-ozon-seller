"""Тест: ozon_fbo_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import FboPosting, SupplyOrder

MOCK_FBO_POSTING = {
    "posting_number": "FBO-0001",
    "order_number": "FBO-ORDER-001",
    "status": "delivered",
    "created_at": "2026-04-20T10:00:00Z",
    "products": [{"name": "Товар FBO", "sku": 200100, "quantity": 1, "offer_id": "FBO-SKU-001"}],
}

MOCK_SUPPLY = {
    "supply_order_id": 5001,
    "state": "ACTIVE",
    "created_at": "2026-04-15T08:00:00Z",
    "total_items_count": 50,
}


@pytest.mark.anyio
async def test_fbo_postings_list():
    FboPosting.model_validate(MOCK_FBO_POSTING)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbo_postings_list.return_value = {"result": {"postings": [MOCK_FBO_POSTING]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbo_postings_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_fbo_posting_get():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbo_posting_get.return_value = {"result": MOCK_FBO_POSTING}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbo_posting_get", {"posting_number": "FBO-0001"})
            assert not result.isError


@pytest.mark.anyio
async def test_fbo_supply_list():
    SupplyOrder.model_validate(MOCK_SUPPLY)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbo_supply_list.return_value = {"result": {"items": [MOCK_SUPPLY]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbo_supply_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_fbo_supply_get():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbo_supply_get.return_value = {"result": MOCK_SUPPLY}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbo_supply_get", {"supply_order_id": 5001})
            assert not result.isError


@pytest.mark.anyio
async def test_fbo_supply_cancel():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbo_supply_cancel.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbo_supply_cancel", {"supply_order_id": 5001})
            assert not result.isError
