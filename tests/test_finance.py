"""Тест: ozon_finance_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Transaction

MOCK_TRANSACTION = {
    "operation_id": 1001,
    "operation_type": "OperationAgentDeliveredToCustomer",
    "operation_date": "2026-04-20T10:00:00Z",
    "amount": 1500.0,
    "payout": 1350.0,
}


@pytest.mark.anyio
async def test_finance_transactions():
    Transaction.model_validate(MOCK_TRANSACTION)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.finance_transactions.return_value = {"result": {"operations": [MOCK_TRANSACTION], "page_count": 1, "row_count": 1}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_finance_transactions", {"filter_json": "{}"})
            assert not result.isError


@pytest.mark.anyio
async def test_finance_totals():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.finance_totals.return_value = {"result": {"accruals_for_sale": 10000.0}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_finance_totals", {"filter_json": "{}"})
            assert not result.isError


@pytest.mark.anyio
async def test_finance_realization():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.finance_realization.return_value = {"result": {"rows": []}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_finance_realization", {"date": "2026-04"})
            assert not result.isError
