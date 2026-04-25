"""Тест: ozon_report_* tools."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp
from mcp_server_ozon_seller.models import ReportInfo

MOCK_REPORT = {"code": "RPT-001", "status": "success", "file": "https://example.com/report.csv", "report_type": "seller_products"}


@pytest.mark.anyio
async def test_report_create():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.report_create.return_value = {"result": {"code": "RPT-001"}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_report_create", {"report_type": "seller_products"})
            assert not result.isError


@pytest.mark.anyio
async def test_report_info():
    ReportInfo.model_validate(MOCK_REPORT)
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.report_info.return_value = {"result": MOCK_REPORT}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_report_info", {"code": "RPT-001"})
            assert not result.isError


@pytest.mark.anyio
async def test_report_list():
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.report_list.return_value = {"result": {"reports": [MOCK_REPORT]}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_report_list", {})
            assert not result.isError
