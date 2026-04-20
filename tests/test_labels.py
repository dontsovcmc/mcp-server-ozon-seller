"""Тест: ozon_labels_pdf."""

import json
from unittest.mock import patch

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_server_ozon_seller.server import mcp

MOCK_POSTINGS = [
    {
        "posting_number": "89765432-0001-1",
        "order_number": "89765432-0001",
        "status": "awaiting_packaging",
        "shipment_date": "2026-04-21T10:00:00Z",
        "products": [{"name": "Товар", "sku": 100500, "quantity": 1, "offer_id": "T-01"}],
    },
]

MOCK_PDF = b"%PDF-1.4 fake content"


@pytest.mark.anyio
async def test_labels_pdf_all(tmp_path):
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_unfulfilled_orders.return_value = MOCK_POSTINGS
        instance.get_label_pdf.return_value = MOCK_PDF

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_labels_pdf", {
                "posting_numbers": "all",
                "output_dir": str(tmp_path),
            })
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["downloaded"] == 1
            assert data["errors"] == 0

            pdf_file = tmp_path / "89765432-0001-1.pdf"
            assert pdf_file.exists()
            assert pdf_file.read_bytes() == MOCK_PDF


@pytest.mark.anyio
async def test_labels_pdf_specific(tmp_path):
    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value
        instance.get_label_pdf.return_value = MOCK_PDF

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_labels_pdf", {
                "posting_numbers": "89765432-0001-1",
                "output_dir": str(tmp_path),
            })
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["downloaded"] == 1


@pytest.mark.anyio
async def test_labels_pdf_skip_existing(tmp_path):
    # Создаём файл заранее
    (tmp_path / "89765432-0001-1.pdf").write_bytes(b"existing")

    with patch("mcp_server_ozon_seller.server.OzonSellerAPI") as MockAPI:
        instance = MockAPI.return_value

        async with create_connected_server_and_client_session(mcp._mcp_server) as session:
            result = await session.call_tool("ozon_labels_pdf", {
                "posting_numbers": "89765432-0001-1",
                "output_dir": str(tmp_path),
            })
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["skipped"] == 1
            assert data["downloaded"] == 0
