"""Тест: ozon_certificate_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import Certificate

MOCK_CERTIFICATE = {"certificate_id": 12001, "name": "Сертификат соответствия", "type": "conformity", "status": "active"}


@pytest.mark.anyio
async def test_certificate_list():
    Certificate.model_validate(MOCK_CERTIFICATE)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.certificate_list.return_value = {"result": {"items": [MOCK_CERTIFICATE]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_certificate_list", {})
            assert not result.isError


@pytest.mark.anyio
async def test_certificate_info():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.certificate_info.return_value = {"result": MOCK_CERTIFICATE}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_certificate_info", {"certificate_id": 12001})
            assert not result.isError


@pytest.mark.anyio
async def test_certificate_delete():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.certificate_delete.return_value = {"result": True}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_certificate_delete", {"certificate_id": 12001})
            assert not result.isError
