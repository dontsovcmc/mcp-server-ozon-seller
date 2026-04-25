"""Тест: ozon_cancellation_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Cancellation

MOCK_CANCELLATION = {
    "cancellation_id": 11001,
    "posting_number": "89765432-0001-1",
    "state": "PENDING",
    "cancel_reason": "По просьбе покупателя",
    "cancellation_initiator": "buyer",
}


@pytest.mark.anyio
async def test_cancellation_list():
    Cancellation.model_validate(MOCK_CANCELLATION)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.cancellation_list.return_value = {"result": {"items": [MOCK_CANCELLATION]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_cancellation_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_cancellation_approve():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.cancellation_approve.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_cancellation_approve", {"cancellation_id": 11001})
            assert not result.isError


@pytest.mark.anyio
async def test_cancellation_reject():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.cancellation_reject.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_cancellation_reject", {"cancellation_id": 11001, "comment": "Нет"})
            assert not result.isError
