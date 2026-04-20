"""MCP server for Ozon Seller API — FBS orders, labels, shipping."""

import json
import logging
import os
import sys

from mcp.server.fastmcp import FastMCP

from .ozon_api import OzonSellerAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stderr)
log = logging.getLogger(__name__)

mcp = FastMCP("ozon-seller")

DEFAULT_LABELS_DIR = os.path.expanduser("~/.config/mcp-server-ozon-seller/labels")


def _get_api() -> OzonSellerAPI:
    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    if not client_id or not api_key:
        raise RuntimeError("OZON_CLIENT_ID and OZON_API_KEY environment variables are required")
    return OzonSellerAPI(client_id, api_key)


def _format_posting(p: dict) -> str:
    """Форматирует одно отправление в читаемую строку."""
    products = []
    for prod in p.get("products", []):
        name = prod.get("name", "?")
        qty = prod.get("quantity", 1)
        products.append(f"{name} x{qty}")
    products_str = ", ".join(products) if products else "—"
    shipment_date = p.get("shipment_date", "")[:10]
    return f"{p.get('posting_number', '?')}  |  {products_str}  |  {shipment_date}"


# ── Unfulfilled orders ──────────────────────────────────────────────


@mcp.tool()
def ozon_unfulfilled_orders(days: int = 7) -> str:
    """Get list of unshipped FBS orders (status: awaiting_packaging).

    Returns posting numbers, product names, quantities, and shipment dates.

    Args:
        days: How many days back to search (default 7)
    """
    api = _get_api()
    postings = api.get_unfulfilled_orders(days=days)

    if not postings:
        return json.dumps({"count": 0, "postings": [], "message": "Нет несобранных заказов"}, ensure_ascii=False)

    result = {
        "count": len(postings),
        "postings": [
            {
                "posting_number": p.get("posting_number"),
                "order_number": p.get("order_number"),
                "shipment_date": p.get("shipment_date", "")[:10],
                "products": [
                    {
                        "name": prod.get("name"),
                        "sku": prod.get("sku"),
                        "quantity": prod.get("quantity"),
                        "offer_id": prod.get("offer_id"),
                    }
                    for prod in p.get("products", [])
                ],
            }
            for p in postings
        ],
    }
    return json.dumps(result, ensure_ascii=False)


# ── Labels PDF ──────────────────────────────────────────────────────


@mcp.tool()
def ozon_labels_pdf(posting_numbers: str = "all", days: int = 7, output_dir: str = "") -> str:
    """Download FBS package label PDFs for given postings.

    Args:
        posting_numbers: Comma-separated posting numbers, or "all" for all unfulfilled orders
        days: How many days back to search when using "all" (default 7)
        output_dir: Directory to save PDFs (default ~/.config/mcp-server-ozon-seller/labels)
    """
    api = _get_api()
    out = output_dir or DEFAULT_LABELS_DIR
    os.makedirs(out, exist_ok=True)

    if posting_numbers.strip().lower() == "all":
        postings = api.get_unfulfilled_orders(days=days)
        numbers = [p["posting_number"] for p in postings]
    else:
        numbers = [n.strip() for n in posting_numbers.split(",") if n.strip()]

    if not numbers:
        return json.dumps({"downloaded": 0, "message": "Нет отправлений для скачивания"}, ensure_ascii=False)

    results = []
    for pn in numbers:
        filepath = os.path.join(out, f"{pn}.pdf")
        if os.path.exists(filepath):
            results.append({"posting_number": pn, "path": os.path.abspath(filepath), "status": "skipped"})
            continue
        try:
            pdf_bytes = api.get_label_pdf(pn)
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
            results.append({"posting_number": pn, "path": os.path.abspath(filepath), "status": "downloaded"})
        except RuntimeError as e:
            results.append({"posting_number": pn, "path": "", "status": "error", "error": str(e)})

    downloaded = sum(1 for r in results if r["status"] == "downloaded")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")

    return json.dumps({
        "total": len(numbers),
        "downloaded": downloaded,
        "skipped": skipped,
        "errors": errors,
        "output_dir": os.path.abspath(out),
        "files": results,
    }, ensure_ascii=False)


# ── Ship orders ─────────────────────────────────────────────────────


@mcp.tool()
def ozon_ship_orders(posting_numbers: str = "all", days: int = 7) -> str:
    """Mark FBS orders as assembled (awaiting_packaging -> awaiting_deliver).

    Automatically fetches product SKUs and quantities for each posting.

    Args:
        posting_numbers: Comma-separated posting numbers, or "all" for all unfulfilled orders
        days: How many days back to search when using "all" (default 7)
    """
    api = _get_api()

    if posting_numbers.strip().lower() == "all":
        postings = api.get_unfulfilled_orders(days=days)
    else:
        numbers = [n.strip() for n in posting_numbers.split(",") if n.strip()]
        postings = [api.get_posting(pn) for pn in numbers]

    if not postings:
        return json.dumps({"shipped": 0, "message": "Нет отправлений для сборки"}, ensure_ascii=False)

    results = []
    for p in postings:
        pn = p.get("posting_number", "")
        items = [
            {"sku": prod["sku"], "quantity": prod["quantity"]}
            for prod in p.get("products", [])
        ]
        try:
            api.ship_posting(pn, items)
            results.append({"posting_number": pn, "status": "shipped"})
        except RuntimeError as e:
            results.append({"posting_number": pn, "status": "error", "error": str(e)})

    shipped = sum(1 for r in results if r["status"] == "shipped")
    errors = sum(1 for r in results if r["status"] == "error")

    return json.dumps({
        "total": len(postings),
        "shipped": shipped,
        "errors": errors,
        "results": results,
    }, ensure_ascii=False)
