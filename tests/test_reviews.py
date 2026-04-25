"""Тест: ozon_review* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Review

MOCK_REVIEW = {"review_id": 6001, "rating": 5, "text": "Отличный товар!", "created_at": "2026-04-18T14:00:00Z", "product_id": 12345, "sku": 100500}


@pytest.mark.anyio
async def test_reviews_list():
    Review.model_validate(MOCK_REVIEW)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.reviews_list.return_value = {"result": {"reviews": [MOCK_REVIEW]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_reviews_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_review_info():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.review_info.return_value = {"result": MOCK_REVIEW}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_review_info", {"review_id": 6001})
            assert not result.isError


@pytest.mark.anyio
async def test_review_comment():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.review_comment.return_value = {"result": {"comment_id": 7001}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_review_comment", {"review_id": 6001, "text": "Спасибо за отзыв!"})
            assert not result.isError
