"""Тест: ozon_return* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import ReturnItem, RfbsReturn

MOCK_RETURN = {
    "return_id": 7001,
    "posting_number": "89765432-0001-1",
    "status": "returned_to_seller",
    "return_reason_name": "Брак",
    "created_at": "2026-04-18T12:00:00Z",
    "product_id": 12345,
    "sku": 100500,
    "product_name": "Тестовый товар",
    "quantity": 1,
}

MOCK_RFBS_RETURN = {
    "return_id": 8001,
    "order_id": 9001,
    "order_number": "ORDER-9001",
    "posting_number": "RFBS-0001-1",
    "status": "created",
    "return_reason": "defect",
    "return_reason_name": "Дефект",
    "created_at": "2026-04-19T10:00:00Z",
}


@pytest.mark.anyio
async def test_returns_fbs():
    ReturnItem.model_validate(MOCK_RETURN)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.returns_fbs.return_value = {"result": {"returns": [MOCK_RETURN], "last_id": 0}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_returns_fbs", {})
            assert not result.isError


@pytest.mark.anyio
async def test_returns_fbo():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.returns_fbo.return_value = {"result": {"returns": [], "last_id": 0}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_returns_fbo", {})
            assert not result.isError


@pytest.mark.anyio
async def test_return_rfbs_list():
    RfbsReturn.model_validate(MOCK_RFBS_RETURN)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.return_rfbs_list.return_value = {"result": {"returns": [MOCK_RFBS_RETURN]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_return_rfbs_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_return_rfbs_approve():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.return_rfbs_approve.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_return_rfbs_approve", {"return_id": 8001})
            assert not result.isError
