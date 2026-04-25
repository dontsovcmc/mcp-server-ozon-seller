"""Тест: ozon_fbs_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Posting, CancelReason

MOCK_POSTING = {
    "posting_number": "89765432-0001-1",
    "order_number": "89765432-0001",
    "status": "awaiting_packaging",
    "shipment_date": "2026-04-21T10:00:00Z",
    "products": [
        {"name": "Тестовый товар", "sku": 100500, "quantity": 2, "offer_id": "SKU-001", "price": "1500.00", "currency_code": "RUB"},
    ],
}


@pytest.mark.anyio
async def test_fbs_postings_list():
    Posting.model_validate(MOCK_POSTING)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_postings_list.return_value = {"result": {"postings": [MOCK_POSTING], "has_next": False}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_postings_list", {})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert len(data["result"]["postings"]) == 1


@pytest.mark.anyio
async def test_fbs_posting_get():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_posting_get.return_value = {"result": MOCK_POSTING}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_posting_get", {"posting_number": "89765432-0001-1"})
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_posting_cancel():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_posting_cancel.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_posting_cancel", {
                "posting_number": "89765432-0001-1",
                "cancel_reason_id": 352,
            })
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_cancel_reasons():
    mock_reason = {"id": 352, "title": "Товар закончился", "type_id": 1, "is_available_for_cancellation": True}
    CancelReason.model_validate(mock_reason)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_cancel_reasons.return_value = {"result": [mock_reason]}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_cancel_reasons", {})
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_posting_tracking():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_posting_tracking.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_posting_tracking", {
                "posting_number": "89765432-0001-1",
                "tracking_number": "TR123456789",
            })
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_act_create():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_act_create.return_value = {"result": {"id": 42}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_act_create", {
                "delivery_method_id": 100,
                "departure_date": "2026-04-25",
            })
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_act_status():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_act_status.return_value = {"result": {"status": "ready", "added_to_act": ["89765432-0001-1"]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_act_status", {"id": 42})
            assert not result.isError


@pytest.mark.anyio
async def test_fbs_restrictions():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.fbs_restrictions.return_value = {"result": {}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_fbs_restrictions", {"posting_number": "89765432-0001-1"})
            assert not result.isError
