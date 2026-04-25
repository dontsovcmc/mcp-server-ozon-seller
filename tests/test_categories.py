"""Тест: ozon_category_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Category, CategoryAttribute, AttributeValue

MOCK_CATEGORY = {"category_id": 17028922, "title": "Электроника", "children": []}
MOCK_ATTRIBUTE = {"id": 85, "name": "Бренд", "type": "String", "is_required": True, "dictionary_id": 28732849}
MOCK_VALUE = {"id": 971082156, "value": "Samsung", "info": "", "picture": ""}


@pytest.mark.anyio
async def test_category_tree():
    Category.model_validate(MOCK_CATEGORY)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.category_tree.return_value = {"result": [MOCK_CATEGORY]}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_category_tree", {})
            assert not result.isError


@pytest.mark.anyio
async def test_category_attributes():
    CategoryAttribute.model_validate(MOCK_ATTRIBUTE)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.category_attributes.return_value = {"result": [MOCK_ATTRIBUTE]}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_category_attributes", {"description_category_id": 17028922})
            assert not result.isError


@pytest.mark.anyio
async def test_category_attribute_values():
    AttributeValue.model_validate(MOCK_VALUE)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.category_attribute_values.return_value = {"result": [MOCK_VALUE], "has_next": False}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_category_attribute_values", {
                "attribute_id": 85, "description_category_id": 17028922,
            })
            assert not result.isError
