"""Тест: ozon_promo_* и ozon_strategy_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Promotion, Strategy

MOCK_PROMO = {
    "action_id": 3001,
    "title": "Весенняя распродажа",
    "date_start": "2026-04-01T00:00:00Z",
    "date_end": "2026-04-30T23:59:59Z",
    "participating_products_count": 5,
    "is_participating": True,
    "action_type": "DISCOUNT",
}

MOCK_STRATEGY = {
    "strategy_id": 4001,
    "type": "COMP_PRICE",
    "name": "Конкурентная цена",
    "enabled": True,
    "products_count": 10,
}


@pytest.mark.anyio
async def test_promo_available():
    Promotion.model_validate(MOCK_PROMO)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.promo_available.return_value = {"result": [MOCK_PROMO]}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_promo_available", {})
            assert not result.isError


@pytest.mark.anyio
async def test_promo_products():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.promo_products.return_value = {"result": {"products": [], "total": 0}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_promo_products", {"action_id": 3001})
            assert not result.isError


@pytest.mark.anyio
async def test_strategy_list():
    Strategy.model_validate(MOCK_STRATEGY)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.strategy_list.return_value = {"result": {"items": [MOCK_STRATEGY]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_strategy_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_strategy_delete():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.strategy_delete.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_strategy_delete", {"strategy_id": 4001})
            assert not result.isError
