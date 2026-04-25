"""MCP server for Ozon Seller API."""

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
DEFAULT_DOCS_DIR = os.path.expanduser("~/.config/mcp-server-ozon-seller/docs")


def _get_api() -> OzonSellerAPI:
    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    if not client_id or not api_key:
        raise RuntimeError("OZON_CLIENT_ID and OZON_API_KEY environment variables are required")
    return OzonSellerAPI(client_id, api_key)


def _j(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def _save_bytes(data: bytes, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return _j({"path": os.path.abspath(path), "size": len(data)})


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


# ── Legacy Tools (backward compatibility) ─────────────────────────


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
        return _j({"count": 0, "postings": [], "message": "Нет несобранных заказов"})

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
    return _j(result)


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
        return _j({"downloaded": 0, "message": "Нет отправлений для скачивания"})

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

    return _j({
        "total": len(numbers),
        "downloaded": downloaded,
        "skipped": skipped,
        "errors": errors,
        "output_dir": os.path.abspath(out),
        "files": results,
    })


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
        return _j({"shipped": 0, "message": "Нет отправлений для сборки"})

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

    return _j({
        "total": len(postings),
        "shipped": shipped,
        "errors": errors,
        "results": results,
    })


# ── Products ───────────────────────────────────────────────────────


@mcp.tool()
def ozon_product_import(items_json: str) -> str:
    """Import/create products. Args: items_json — JSON array of product objects."""
    return _j(_get_api().product_import(json.loads(items_json)))


@mcp.tool()
def ozon_product_import_info(task_id: int) -> str:
    """Check product import status."""
    return _j(_get_api().product_import_info(task_id))


@mcp.tool()
def ozon_product_info(offer_id: str = "", product_id: int = 0, sku: int = 0) -> str:
    """Get product details by offer_id, product_id or sku."""
    return _j(_get_api().product_info(offer_id=offer_id, product_id=product_id, sku=sku))


@mcp.tool()
def ozon_product_info_list(offer_ids: str = "", product_ids: str = "", skus: str = "") -> str:
    """Get multiple products info. Args: comma-separated IDs."""
    oids = [s.strip() for s in offer_ids.split(",") if s.strip()] if offer_ids else None
    pids = [int(s.strip()) for s in product_ids.split(",") if s.strip()] if product_ids else None
    sids = [int(s.strip()) for s in skus.split(",") if s.strip()] if skus else None
    return _j(_get_api().product_info_list(offer_id=oids, product_id=pids, sku=sids))


@mcp.tool()
def ozon_product_list(filter_json: str = "{}", last_id: str = "", limit: int = 100) -> str:
    """List products with filters. Args: filter_json — {offer_id, product_id, visibility}."""
    f = json.loads(filter_json)
    return _j(_get_api().product_list(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_product_update(items_json: str) -> str:
    """Update product fields. Args: items_json — JSON array."""
    return _j(_get_api().product_update(json.loads(items_json)))


@mcp.tool()
def ozon_product_prices_update(prices_json: str) -> str:
    """Update product prices. Args: prices_json — JSON array of {offer_id, price, old_price, min_price}."""
    return _j(_get_api().product_prices_update(json.loads(prices_json)))


@mcp.tool()
def ozon_product_stocks_update(stocks_json: str) -> str:
    """Update FBS stocks. Args: stocks_json — JSON array of {offer_id, product_id, stock, warehouse_id}."""
    return _j(_get_api().product_stocks_update(json.loads(stocks_json)))


@mcp.tool()
def ozon_product_stocks_info(filter_json: str = "{}", last_id: str = "", limit: int = 100) -> str:
    """Get product stock levels."""
    f = json.loads(filter_json)
    return _j(_get_api().product_stocks_info(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_product_prices_info(filter_json: str = "{}", last_id: str = "", limit: int = 100) -> str:
    """Get product prices info."""
    f = json.loads(filter_json)
    return _j(_get_api().product_prices_info(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_product_description(offer_id: str = "", product_id: int = 0) -> str:
    """Get product description."""
    return _j(_get_api().product_description(offer_id=offer_id, product_id=product_id))


@mcp.tool()
def ozon_product_attributes(filter_json: str = "{}", last_id: str = "", limit: int = 100) -> str:
    """Get product attributes."""
    f = json.loads(filter_json)
    return _j(_get_api().product_attributes(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_product_archive(product_ids: str) -> str:
    """Archive products. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().product_archive(ids))


@mcp.tool()
def ozon_product_unarchive(product_ids: str) -> str:
    """Unarchive products. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().product_unarchive(ids))


@mcp.tool()
def ozon_product_delete(product_ids: str) -> str:
    """Delete products. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().product_delete(ids))


@mcp.tool()
def ozon_product_pictures_import(images_json: str) -> str:
    """Import product pictures. Args: images_json — JSON array."""
    return _j(_get_api().product_pictures_import(json.loads(images_json)))


@mcp.tool()
def ozon_product_pictures_info(product_ids: str) -> str:
    """Get pictures import status. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().product_pictures_info(ids))


@mcp.tool()
def ozon_product_geo_restrictions(filter_json: str = "{}", last_id: str = "", limit: int = 100) -> str:
    """Get product geo restrictions."""
    f = json.loads(filter_json)
    return _j(_get_api().product_geo_restrictions(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_product_rating(skus: str) -> str:
    """Get content rating by SKU. Args: skus — comma-separated."""
    ids = [int(s.strip()) for s in skus.split(",")]
    return _j(_get_api().product_rating(ids))


@mcp.tool()
def ozon_product_related_sku(items_json: str) -> str:
    """Get related SKUs (FBO/FBS links). Args: items_json — JSON array."""
    return _j(_get_api().product_related_sku(json.loads(items_json)))


@mcp.tool()
def ozon_product_upload_digital_codes(product_id: int, codes_json: str) -> str:
    """Upload digital activation codes. Args: codes_json — JSON array of strings."""
    return _j(_get_api().product_upload_digital_codes(json.loads(codes_json), product_id))


# ── FBS Postings ───────────────────────────────────────────────────


@mcp.tool()
def ozon_fbs_postings_list(filter_json: str = "{}", dir: str = "ASC",
                           limit: int = 50, offset: int = 0) -> str:
    """List FBS postings with filters. Args: filter_json — {since, to, status, delivery_method_id}."""
    f = json.loads(filter_json)
    return _j(_get_api().fbs_postings_list(filter_dict=f if f else None, dir=dir, limit=limit, offset=offset))


@mcp.tool()
def ozon_fbs_posting_get(posting_number: str) -> str:
    """Get FBS posting details."""
    return _j(_get_api().fbs_posting_get(posting_number))


@mcp.tool()
def ozon_fbs_posting_ship(posting_number: str, items_json: str) -> str:
    """Ship FBS posting. Args: items_json — JSON array of {sku, quantity}."""
    return _j(_get_api().ship_posting(posting_number, json.loads(items_json)))


@mcp.tool()
def ozon_fbs_posting_cancel(posting_number: str, cancel_reason_id: int,
                            cancel_reason_message: str = "") -> str:
    """Cancel FBS posting."""
    return _j(_get_api().fbs_posting_cancel(posting_number, cancel_reason_id, cancel_reason_message))


@mcp.tool()
def ozon_fbs_cancel_reasons() -> str:
    """List FBS cancellation reasons."""
    return _j(_get_api().fbs_cancel_reasons())


@mcp.tool()
def ozon_fbs_posting_tracking(posting_number: str, tracking_number: str) -> str:
    """Set tracking number for FBS posting."""
    return _j(_get_api().fbs_posting_tracking(posting_number, tracking_number))


@mcp.tool()
def ozon_fbs_posting_label(posting_number: str, output_dir: str = "") -> str:
    """Download FBS package label PDF."""
    api = _get_api()
    out = output_dir or DEFAULT_LABELS_DIR
    os.makedirs(out, exist_ok=True)
    filepath = os.path.join(out, f"{posting_number}.pdf")
    pdf_bytes = api.get_label_pdf(posting_number)
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    return _j({"path": os.path.abspath(filepath), "size": len(pdf_bytes)})


@mcp.tool()
def ozon_fbs_act_create(delivery_method_id: int, departure_date: str) -> str:
    """Create shipping act. Args: departure_date — YYYY-MM-DD."""
    return _j(_get_api().fbs_act_create(delivery_method_id, departure_date))


@mcp.tool()
def ozon_fbs_act_status(id: int) -> str:
    """Check act generation status."""
    return _j(_get_api().fbs_act_status(id))


@mcp.tool()
def ozon_fbs_act_pdf(id: int, output_path: str = "") -> str:
    """Download shipping act PDF."""
    data = _get_api().fbs_act_pdf(id)
    path = output_path or os.path.join(DEFAULT_DOCS_DIR, f"act_{id}.pdf")
    return _save_bytes(data, path)


@mcp.tool()
def ozon_fbs_digital_act_pdf(id: int, doc_type: str = "act_of_acceptance", output_path: str = "") -> str:
    """Download digital act PDF."""
    data = _get_api().fbs_digital_act_pdf(id, doc_type)
    path = output_path or os.path.join(DEFAULT_DOCS_DIR, f"digital_act_{id}.pdf")
    return _save_bytes(data, path)


@mcp.tool()
def ozon_fbs_container_labels(id: int, output_path: str = "") -> str:
    """Download container labels."""
    data = _get_api().fbs_container_labels(id)
    path = output_path or os.path.join(DEFAULT_DOCS_DIR, f"container_{id}.pdf")
    return _save_bytes(data, path)


@mcp.tool()
def ozon_fbs_posting_delivered(posting_number: str) -> str:
    """Mark FBS posting as delivered (rFBS)."""
    return _j(_get_api().fbs_posting_delivered(posting_number))


@mcp.tool()
def ozon_fbs_posting_last_mile(posting_number: str, items_json: str) -> str:
    """Ship last mile. Args: items_json — JSON array of {sku, quantity}."""
    return _j(_get_api().fbs_posting_last_mile(posting_number, json.loads(items_json)))


@mcp.tool()
def ozon_fbs_timeslot_restrictions(delivery_method_id: int) -> str:
    """Get timeslot change restrictions."""
    return _j(_get_api().fbs_timeslot_restrictions(delivery_method_id))


@mcp.tool()
def ozon_fbs_restrictions(posting_number: str) -> str:
    """Get posting restrictions."""
    return _j(_get_api().fbs_restrictions(posting_number))


@mcp.tool()
def ozon_fbs_product_country_set(posting_number: str, product_id: int, country_iso_code: str) -> str:
    """Set manufacturing country for posting product."""
    return _j(_get_api().fbs_product_country_set(posting_number, product_id, country_iso_code))


@mcp.tool()
def ozon_fbs_product_country_list() -> str:
    """List available manufacturing countries."""
    return _j(_get_api().fbs_product_country_list())


# ── FBO ────────────────────────────────────────────────────────────


@mcp.tool()
def ozon_fbo_postings_list(filter_json: str = "{}", dir: str = "ASC",
                           limit: int = 50, offset: int = 0) -> str:
    """List FBO postings. Args: filter_json — {since, to, status}."""
    f = json.loads(filter_json)
    return _j(_get_api().fbo_postings_list(filter_dict=f if f else None, dir=dir, limit=limit, offset=offset))


@mcp.tool()
def ozon_fbo_posting_get(posting_number: str) -> str:
    """Get FBO posting details."""
    return _j(_get_api().fbo_posting_get(posting_number))


@mcp.tool()
def ozon_fbo_supply_create(items_json: str, warehouse_id: int) -> str:
    """Create supply to FBO warehouse. Args: items_json — JSON array of {sku, quantity}."""
    return _j(_get_api().fbo_supply_create(json.loads(items_json), warehouse_id))


@mcp.tool()
def ozon_fbo_supply_get(supply_order_id: int) -> str:
    """Get supply order details."""
    return _j(_get_api().fbo_supply_get(supply_order_id))


@mcp.tool()
def ozon_fbo_supply_list(filter_json: str = "{}", page: int = 1, page_size: int = 50) -> str:
    """List supply orders."""
    f = json.loads(filter_json)
    return _j(_get_api().fbo_supply_list(filter_dict=f if f else None, page=page, page_size=page_size))


@mcp.tool()
def ozon_fbo_supply_cancel(supply_order_id: int) -> str:
    """Cancel supply order."""
    return _j(_get_api().fbo_supply_cancel(supply_order_id))


@mcp.tool()
def ozon_fbo_supply_items(supply_order_id: int) -> str:
    """Get supply order items."""
    return _j(_get_api().fbo_supply_items(supply_order_id))


@mcp.tool()
def ozon_fbo_supply_shipments(supply_order_id: int) -> str:
    """List supply shipments."""
    return _j(_get_api().fbo_supply_shipments(supply_order_id))


@mcp.tool()
def ozon_fbo_warehouse_workload(warehouse_id: int) -> str:
    """Get FBO warehouse acceptance workload."""
    return _j(_get_api().fbo_warehouse_workload(warehouse_id))


# ── Categories ─────────────────────────────────────────────────────


@mcp.tool()
def ozon_category_tree(language: str = "DEFAULT") -> str:
    """Get category tree."""
    return _j(_get_api().category_tree(language))


@mcp.tool()
def ozon_category_attributes(description_category_id: int, language: str = "DEFAULT",
                              type_id: int = 0) -> str:
    """Get category attributes."""
    return _j(_get_api().category_attributes(description_category_id, language, type_id))


@mcp.tool()
def ozon_category_attribute_values(attribute_id: int, description_category_id: int,
                                    last_value_id: int = 0, limit: int = 100) -> str:
    """Get attribute dictionary values."""
    return _j(_get_api().category_attribute_values(attribute_id, description_category_id,
                                                    last_value_id=last_value_id, limit=limit))


@mcp.tool()
def ozon_category_attribute_values_search(attribute_id: int, description_category_id: int,
                                           value: str, limit: int = 100) -> str:
    """Search attribute dictionary values."""
    return _j(_get_api().category_attribute_values_search(attribute_id, description_category_id,
                                                          value, limit=limit))


# ── Finance ────────────────────────────────────────────────────────


@mcp.tool()
def ozon_finance_transactions(filter_json: str, page: int = 1, page_size: int = 50) -> str:
    """List financial transactions. Args: filter_json — {date, operation_type, posting_number, transaction_type}."""
    return _j(_get_api().finance_transactions(json.loads(filter_json), page, page_size))


@mcp.tool()
def ozon_finance_totals(filter_json: str) -> str:
    """Get financial totals. Args: filter_json — date range filter."""
    return _j(_get_api().finance_totals(json.loads(filter_json)))


@mcp.tool()
def ozon_finance_cash_flow(filter_json: str, page: int = 1, page_size: int = 50) -> str:
    """Get cash flow statement."""
    return _j(_get_api().finance_cash_flow(json.loads(filter_json), page, page_size))


@mcp.tool()
def ozon_finance_realization(date: str) -> str:
    """Get realization report. Args: date — YYYY-MM."""
    return _j(_get_api().finance_realization(date))


# ── Analytics ──────────────────────────────────────────────────────


@mcp.tool()
def ozon_analytics_data(date_from: str, date_to: str, metrics_json: str, dimensions_json: str,
                        filters_json: str = "[]", sort_json: str = "[]",
                        limit: int = 1000, offset: int = 0) -> str:
    """Get analytics data (sales, views, etc.). Args: metrics_json — JSON array of metric names, dimensions_json — JSON array of dimension names."""
    return _j(_get_api().analytics_data(
        date_from, date_to,
        json.loads(metrics_json), json.loads(dimensions_json),
        filters=json.loads(filters_json) or None,
        sort=json.loads(sort_json) or None,
        limit=limit, offset=offset,
    ))


@mcp.tool()
def ozon_analytics_stock_on_warehouses(limit: int = 100, offset: int = 0,
                                       warehouse_type: str = "") -> str:
    """Get stock on warehouses report."""
    return _j(_get_api().analytics_stock_on_warehouses(limit, offset, warehouse_type))


@mcp.tool()
def ozon_analytics_item_turnover(date_from: str, date_to: str, skus: str = "") -> str:
    """Get item turnover data. Args: skus — optional comma-separated SKUs."""
    sku_list = [int(s.strip()) for s in skus.split(",") if s.strip()] if skus else None
    return _j(_get_api().analytics_item_turnover(date_from, date_to, sku=sku_list))


# ── Warehouses ─────────────────────────────────────────────────────


@mcp.tool()
def ozon_warehouse_list() -> str:
    """List seller warehouses."""
    return _j(_get_api().warehouse_list())


@mcp.tool()
def ozon_warehouse_delivery_methods(filter_json: str = "{}", limit: int = 50, offset: int = 0) -> str:
    """List delivery methods per warehouse."""
    f = json.loads(filter_json)
    return _j(_get_api().delivery_methods(filter_dict=f if f else None, limit=limit, offset=offset))


# ── Returns ────────────────────────────────────────────────────────


@mcp.tool()
def ozon_returns_fbo(filter_json: str = "{}", last_id: int = 0, limit: int = 50) -> str:
    """Get FBO returns."""
    f = json.loads(filter_json)
    return _j(_get_api().returns_fbo(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_returns_fbs(filter_json: str = "{}", last_id: int = 0, limit: int = 50) -> str:
    """Get FBS returns."""
    f = json.loads(filter_json)
    return _j(_get_api().returns_fbs(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_return_get(posting_number: str) -> str:
    """Get return details by posting number."""
    return _j(_get_api().return_get(posting_number))


@mcp.tool()
def ozon_return_rfbs_list(filter_json: str = "{}", last_id: int = 0, limit: int = 50) -> str:
    """List rFBS returns."""
    f = json.loads(filter_json)
    return _j(_get_api().return_rfbs_list(filter_dict=f if f else None, last_id=last_id, limit=limit))


@mcp.tool()
def ozon_return_rfbs_get(return_id: int) -> str:
    """Get rFBS return details."""
    return _j(_get_api().return_rfbs_get(return_id))


@mcp.tool()
def ozon_return_rfbs_approve(return_id: int, comment: str = "") -> str:
    """Approve rFBS return."""
    return _j(_get_api().return_rfbs_approve(return_id, comment))


@mcp.tool()
def ozon_return_rfbs_reject(return_id: int, comment: str = "", reject_reason_id: int = 0) -> str:
    """Reject rFBS return."""
    return _j(_get_api().return_rfbs_reject(return_id, comment, reject_reason_id))


@mcp.tool()
def ozon_return_rfbs_compensate(return_id: int, compensation_amount: float) -> str:
    """Compensate rFBS return."""
    return _j(_get_api().return_rfbs_compensate(return_id, compensation_amount))


# ── Chats ──────────────────────────────────────────────────────────


@mcp.tool()
def ozon_chat_list(chat_ids: str = "", page: int = 1, page_size: int = 30) -> str:
    """List chats. Args: chat_ids — optional comma-separated chat IDs."""
    ids = [s.strip() for s in chat_ids.split(",") if s.strip()] if chat_ids else None
    return _j(_get_api().chat_list(chat_id_list=ids, page=page, page_size=page_size))


@mcp.tool()
def ozon_chat_history(chat_id: str, from_message_id: str = "",
                      limit: int = 50, direction: str = "Forward") -> str:
    """Get chat message history."""
    return _j(_get_api().chat_history(chat_id, from_message_id, limit, direction))


@mcp.tool()
def ozon_chat_start(posting_number: str) -> str:
    """Start chat about a posting."""
    return _j(_get_api().chat_start(posting_number))


@mcp.tool()
def ozon_chat_send_message(chat_id: str, message: str) -> str:
    """Send message to chat."""
    return _j(_get_api().chat_send_message(chat_id, message))


@mcp.tool()
def ozon_chat_send_file(chat_id: str, base64_content: str, name: str = "file") -> str:
    """Send file to chat. Args: base64_content — base64-encoded file."""
    return _j(_get_api().chat_send_file(chat_id, base64_content, name))


@mcp.tool()
def ozon_chat_read(chat_id: str, from_message_id: str) -> str:
    """Mark chat as read up to message."""
    return _j(_get_api().chat_read(chat_id, from_message_id))


# ── Promotions & Strategies ───────────────────────────────────────


@mcp.tool()
def ozon_promo_available() -> str:
    """Get available promotions."""
    return _j(_get_api().promo_available())


@mcp.tool()
def ozon_promo_candidates(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Get products eligible for promotion."""
    return _j(_get_api().promo_candidates(action_id, limit, offset))


@mcp.tool()
def ozon_promo_products(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Get products in promotion."""
    return _j(_get_api().promo_products(action_id, limit, offset))


@mcp.tool()
def ozon_promo_products_add(action_id: int, products_json: str) -> str:
    """Add products to promotion. Args: products_json — JSON array of {product_id, action_price}."""
    return _j(_get_api().promo_products_add(action_id, json.loads(products_json)))


@mcp.tool()
def ozon_promo_products_remove(action_id: int, product_ids: str) -> str:
    """Remove products from promotion. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().promo_products_remove(action_id, ids))


@mcp.tool()
def ozon_promo_hotsale_list() -> str:
    """List Hot Sale promotions."""
    return _j(_get_api().promo_hotsale_list())


@mcp.tool()
def ozon_strategy_list() -> str:
    """List pricing strategies."""
    return _j(_get_api().strategy_list())


@mcp.tool()
def ozon_strategy_create(type: str, update_type: str, name: str = "") -> str:
    """Create pricing strategy."""
    return _j(_get_api().strategy_create(type, update_type, name=name))


@mcp.tool()
def ozon_strategy_update(strategy_id: int, payload_json: str = "{}") -> str:
    """Update pricing strategy."""
    return _j(_get_api().strategy_update(strategy_id, **json.loads(payload_json)))


@mcp.tool()
def ozon_strategy_delete(strategy_id: int) -> str:
    """Delete pricing strategy."""
    return _j(_get_api().strategy_delete(strategy_id))


# ── Rating & Quality ──────────────────────────────────────────────


@mcp.tool()
def ozon_rating_summary() -> str:
    """Get seller rating summary."""
    return _j(_get_api().rating_summary())


@mcp.tool()
def ozon_rating_history(date_from: str, date_to: str, ratings: str = "") -> str:
    """Get rating history. Args: ratings — optional comma-separated rating names."""
    r = [s.strip() for s in ratings.split(",") if s.strip()] if ratings else None
    return _j(_get_api().rating_history(date_from, date_to, ratings=r))


@mcp.tool()
def ozon_quality_rating(date_from: str, date_to: str, warehouse_id: int = 0) -> str:
    """Get quality rating."""
    return _j(_get_api().quality_rating(date_from, date_to, warehouse_id))


# ── Reports ────────────────────────────────────────────────────────


@mcp.tool()
def ozon_report_create(report_type: str, params_json: str = "{}") -> str:
    """Create a report. report_type: seller_products, seller_returns, seller_postings, seller_finance, seller_stock."""
    params = json.loads(params_json)
    return _j(_get_api().report_create(report_type, params=params if params else None))


@mcp.tool()
def ozon_report_info(code: str) -> str:
    """Get report generation status."""
    return _j(_get_api().report_info(code))


@mcp.tool()
def ozon_report_list(page: int = 1, page_size: int = 50, report_type: str = "") -> str:
    """List reports."""
    return _j(_get_api().report_list(page, page_size, report_type))


@mcp.tool()
def ozon_report_download(code: str, output_path: str = "") -> str:
    """Download report file."""
    data = _get_api().report_download(code)
    path = output_path or os.path.join(DEFAULT_DOCS_DIR, f"report_{code}.csv")
    return _save_bytes(data, path)


# ── Reviews ────────────────────────────────────────────────────────


@mcp.tool()
def ozon_reviews_list(filter_json: str = "{}", sort_dir: str = "DESC",
                      limit: int = 50, offset: int = 0) -> str:
    """List product reviews."""
    f = json.loads(filter_json)
    return _j(_get_api().reviews_list(filter_dict=f if f else None, sort_dir=sort_dir, limit=limit, offset=offset))


@mcp.tool()
def ozon_review_info(review_id: int) -> str:
    """Get review details."""
    return _j(_get_api().review_info(review_id))


@mcp.tool()
def ozon_review_count(filter_json: str = "{}") -> str:
    """Get review count."""
    f = json.loads(filter_json)
    return _j(_get_api().review_count(filter_dict=f if f else None))


@mcp.tool()
def ozon_review_comment(review_id: int, text: str) -> str:
    """Reply to a review."""
    return _j(_get_api().review_comment(review_id, text))


# ── Questions ──────────────────────────────────────────────────────


@mcp.tool()
def ozon_questions_list(filter_json: str = "{}", sort_dir: str = "DESC",
                        limit: int = 50, offset: int = 0) -> str:
    """List product questions."""
    f = json.loads(filter_json)
    return _j(_get_api().questions_list(filter_dict=f if f else None, sort_dir=sort_dir, limit=limit, offset=offset))


@mcp.tool()
def ozon_question_answer(question_id: int, answer: str) -> str:
    """Answer a product question."""
    return _j(_get_api().question_answer(question_id, answer))


@mcp.tool()
def ozon_question_update(question_id: int, answer: str) -> str:
    """Update answer to a question."""
    return _j(_get_api().question_update(question_id, answer))


# ── Cancellations ─────────────────────────────────────────────────


@mcp.tool()
def ozon_cancellation_list(filter_json: str = "{}", limit: int = 50, offset: int = 0) -> str:
    """List cancellation requests."""
    f = json.loads(filter_json)
    return _j(_get_api().cancellation_list(filter_dict=f if f else None, limit=limit, offset=offset))


@mcp.tool()
def ozon_cancellation_info(cancellation_id: int) -> str:
    """Get cancellation request details."""
    return _j(_get_api().cancellation_info(cancellation_id))


@mcp.tool()
def ozon_cancellation_approve(cancellation_id: int, comment: str = "") -> str:
    """Approve cancellation request."""
    return _j(_get_api().cancellation_approve(cancellation_id, comment))


@mcp.tool()
def ozon_cancellation_reject(cancellation_id: int, comment: str = "") -> str:
    """Reject cancellation request."""
    return _j(_get_api().cancellation_reject(cancellation_id, comment))


# ── Certificates ──────────────────────────────────────────────────


@mcp.tool()
def ozon_certificate_list(filter_json: str = "{}", page: int = 1, page_size: int = 50) -> str:
    """List product certificates."""
    f = json.loads(filter_json)
    return _j(_get_api().certificate_list(filter_dict=f if f else None, page=page, page_size=page_size))


@mcp.tool()
def ozon_certificate_info(certificate_id: int) -> str:
    """Get certificate details."""
    return _j(_get_api().certificate_info(certificate_id))


@mcp.tool()
def ozon_certificate_create(files_json: str, name: str, type_code: str) -> str:
    """Create certificate. Args: files_json — JSON array of file objects."""
    return _j(_get_api().certificate_create(json.loads(files_json), name, type_code))


@mcp.tool()
def ozon_certificate_delete(certificate_id: int) -> str:
    """Delete certificate."""
    return _j(_get_api().certificate_delete(certificate_id))


@mcp.tool()
def ozon_certificate_bind(certificate_id: int, product_ids: str) -> str:
    """Bind certificate to products. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().certificate_bind(certificate_id, ids))


@mcp.tool()
def ozon_certificate_unbind(certificate_id: int, product_ids: str) -> str:
    """Unbind certificate from products. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().certificate_unbind(certificate_id, ids))


# ── Barcodes ──────────────────────────────────────────────────────


@mcp.tool()
def ozon_barcode_generate(product_ids: str) -> str:
    """Generate barcodes. Args: product_ids — comma-separated."""
    ids = [int(s.strip()) for s in product_ids.split(",")]
    return _j(_get_api().barcode_generate(ids))


@mcp.tool()
def ozon_barcode_add(barcodes_json: str) -> str:
    """Bind barcodes to products. Args: barcodes_json — JSON array of {barcode, product_id}."""
    return _j(_get_api().barcode_add(json.loads(barcodes_json)))


# ── Brands ─────────────────────────────────────────────────────────


@mcp.tool()
def ozon_brand_list(page: int = 1, page_size: int = 100) -> str:
    """List brands."""
    return _j(_get_api().brand_list(page, page_size))
