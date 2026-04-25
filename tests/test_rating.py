"""Тест: ozon_rating_* и ozon_quality_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import RatingSummary

MOCK_RATING = {"groups": [{"group_name": "Доставка", "items": [{"rating": 4.8, "value": 98.5}]}], "premium": True}


@pytest.mark.anyio
async def test_rating_summary():
    RatingSummary.model_validate(MOCK_RATING)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.rating_summary.return_value = {"result": MOCK_RATING}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_rating_summary", {})
            assert not result.isError


@pytest.mark.anyio
async def test_quality_rating():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.quality_rating.return_value = {"result": {}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_quality_rating", {"date_from": "2026-04-01", "date_to": "2026-04-25"})
            assert not result.isError
