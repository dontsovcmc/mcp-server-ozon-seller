"""Tests for search + execute MCP tools."""

import json
import os

import pytest
from unittest.mock import patch

from mcp.shared.memory import create_connected_server_and_client_session
from mcp_server_ozon_seller.server import mcp


PATCH = "mcp_server_ozon_seller.ozon_api.OzonSellerAPI"


# ── ozon_search ──────────────────────────────────────────────────

@pytest.mark.anyio
async def test_search_returns_results():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "cancel fbs posting"})
        assert not r.isError
        results = json.loads(r.content[0].text)
        assert len(results) > 0
        assert results[0]["id"] == "fbs-posting-cancel"


@pytest.mark.anyio
async def test_search_with_domain_filter():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "list", "domain": "fbs"})
        results = json.loads(r.content[0].text)
        for item in results:
            assert item["domain"] == "fbs"


@pytest.mark.anyio
async def test_search_returns_params_schema():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "fbs-posting-cancel"})
        results = json.loads(r.content[0].text)
        top = results[0]
        assert "params_schema" in top
        assert top["params_schema"] is not None
        assert "properties" in top["params_schema"]


@pytest.mark.anyio
async def test_search_empty_query():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": ""})
        results = json.loads(r.content[0].text)
        assert results == []


@pytest.mark.anyio
async def test_search_no_match():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "xyznonexistent123"})
        results = json.loads(r.content[0].text)
        assert results == []


@pytest.mark.anyio
async def test_search_file_actions():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "download act pdf"})
        results = json.loads(r.content[0].text)
        file_results = [r for r in results if r["is_file"]]
        assert len(file_results) > 0


@pytest.mark.anyio
async def test_search_destructive_flag():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_search", {"query": "fbs-posting-cancel"})
        results = json.loads(r.content[0].text)
        assert results[0]["is_destructive"] is True


# ── ozon_execute — no-param actions ──────────────────────────────

@pytest.mark.anyio
async def test_execute_warehouse_list():
    with patch(PATCH) as M:
        M.return_value.warehouse_list.return_value = {"result": []}
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute", {
                "action": "warehouse-list",
                "params_json": "{}",
            })
            assert not r.isError
            data = json.loads(r.content[0].text)
            assert "result" in data


@pytest.mark.anyio
async def test_execute_fbs_cancel_reasons():
    with patch(PATCH) as M:
        M.return_value.fbs_cancel_reasons.return_value = {"result": []}
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute", {
                "action": "fbs-cancel-reasons",
                "params_json": "{}",
            })
            assert not r.isError


# ── ozon_execute — actions with params ───────────────────────────

@pytest.mark.anyio
async def test_execute_product_list():
    with patch(PATCH) as M:
        M.return_value.product_list.return_value = {"result": {"items": []}}
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute", {
                "action": "product-list",
                "params_json": '{"limit": 10}',
            })
            assert not r.isError
            M.return_value.product_list.assert_called_once()


@pytest.mark.anyio
async def test_execute_fbs_posting_cancel():
    with patch(PATCH) as M:
        M.return_value.fbs_posting_cancel.return_value = {}
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute", {
                "action": "fbs-posting-cancel",
                "params_json": json.dumps({
                    "posting_number": "12345678-0001-1",
                    "cancel_reason_id": 352,
                }),
            })
            assert not r.isError
            M.return_value.fbs_posting_cancel.assert_called_once()


# ── ozon_execute — error cases ───────────────────────────────────

@pytest.mark.anyio
async def test_execute_unknown_action():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_execute", {
            "action": "nonexistent_action",
            "params_json": "{}",
        })
        assert not r.isError  # returns error in JSON, not MCP error
        data = json.loads(r.content[0].text)
        assert "error" in data


@pytest.mark.anyio
async def test_execute_file_action_via_execute():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_execute", {
            "action": "report-download",
            "params_json": '{"code": "test"}',
        })
        data = json.loads(r.content[0].text)
        assert "error" in data
        assert "ozon_execute_file" in data["error"]


@pytest.mark.anyio
async def test_execute_invalid_json():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_execute", {
            "action": "product-list",
            "params_json": "not-json",
        })
        assert r.isError
        assert "Invalid JSON" in r.content[0].text


@pytest.mark.anyio
async def test_execute_api_error():
    with patch(PATCH) as M:
        M.return_value.product_list.side_effect = RuntimeError("POST /v2/product/list -> 500")
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute", {
                "action": "product-list",
                "params_json": "{}",
            })
            assert r.isError
            assert "500" in r.content[0].text


# ── ozon_execute_file ────────────────────────────────────────────

@pytest.mark.anyio
async def test_execute_file_download(tmp_path):
    with patch(PATCH) as M:
        M.return_value.report_download.return_value = b"col1,col2\n1,2\n"
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            out = str(tmp_path / "report.csv")
            r = await s.call_tool("ozon_execute_file", {
                "action": "report-download",
                "file_path": out,
                "params_json": '{"code": "RPT-001"}',
            })
            assert not r.isError
            data = json.loads(r.content[0].text)
            assert data["size"] == 14
            assert (tmp_path / "report.csv").read_bytes() == b"col1,col2\n1,2\n"


@pytest.mark.anyio
async def test_execute_file_non_file_action():
    async with create_connected_server_and_client_session(mcp._mcp_server) as s:
        r = await s.call_tool("ozon_execute_file", {
            "action": "warehouse-list",
            "file_path": "/tmp/test.bin",
            "params_json": "{}",
        })
        data = json.loads(r.content[0].text)
        assert "error" in data
        assert "ozon_execute" in data["error"]


@pytest.mark.anyio
async def test_execute_file_unsafe_path():
    with patch(PATCH) as M:
        M.return_value.fbs_act_pdf.return_value = b"PDF"
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            r = await s.call_tool("ozon_execute_file", {
                "action": "fbs-act-pdf",
                "file_path": "/etc/evil.pdf",
                "params_json": '{"id": 1}',
            })
            assert r.isError
            assert "not allowed" in r.content[0].text.lower()


@pytest.mark.anyio
async def test_execute_file_hidden_path():
    with patch(PATCH) as M:
        M.return_value.fbs_act_pdf.return_value = b"PDF"
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            home = os.path.expanduser("~")
            r = await s.call_tool("ozon_execute_file", {
                "action": "fbs-act-pdf",
                "file_path": f"{home}/.ssh/evil.pdf",
                "params_json": '{"id": 1}',
            })
            assert r.isError
            assert "dotfiles" in r.content[0].text.lower() or "not allowed" in r.content[0].text.lower()


# ── Catalog completeness ─────────────────────────────────────────

def test_all_actions_have_api_method():
    from mcp_server_ozon_seller.actions import ACTIONS
    from mcp_server_ozon_seller.ozon_api import OzonSellerAPI

    api_methods = {name for name in dir(OzonSellerAPI) if not name.startswith("_")}
    for action in ACTIONS.values():
        assert action.api_method in api_methods, (
            f"Action {action.id} references missing API method: {action.api_method}"
        )


def test_tools_registered():
    """Verify exactly 3 MCP tools are registered."""
    from mcp_server_ozon_seller.server import mcp
    tool_names = set()
    for tool in mcp._tool_manager._tools.values():
        tool_names.add(tool.name)
    assert "ozon_search" in tool_names
    assert "ozon_execute" in tool_names
    assert "ozon_execute_file" in tool_names
    assert len(tool_names) == 3
