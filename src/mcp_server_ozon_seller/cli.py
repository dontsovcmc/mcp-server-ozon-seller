"""CLI for Ozon Seller API.

Usage: ozon-seller-cli <command> [options]
Without arguments starts MCP server (stdio transport).
"""

import argparse
import json
import logging
import os
import sys

from . import __version__

log = logging.getLogger(__name__)

DEFAULT_LABELS_DIR = os.path.expanduser("~/mcp-server-ozon-seller/labels")
DEFAULT_DOCS_DIR = os.path.expanduser("~/mcp-server-ozon-seller/docs")


# ── Helpers ────────────────────────────────────────────────────────


def _load_env(path: str) -> None:
    """Load .env file without external dependencies."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Env file not found: {path}")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)
    log.info("Loaded env from %s", path)


def _load_json(raw: str) -> dict | list:
    """Parse a JSON string, exit on error."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)


def _to_json(data) -> str:
    """Pretty-print data as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _api():
    """Create OzonSellerAPI from environment variables."""
    from .ozon_api import OzonSellerAPI

    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    if not client_id or not api_key:
        print(
            "Error: OZON_CLIENT_ID and OZON_API_KEY environment variables are required",
            file=sys.stderr,
        )
        sys.exit(1)
    timeout = int(os.getenv("OZON_TIMEOUT", "30"))
    file_timeout = int(os.getenv("OZON_FILE_TIMEOUT", "60"))
    return OzonSellerAPI(client_id, api_key, timeout=timeout, file_timeout=file_timeout)


def _download(data: bytes, path: str) -> str:
    """Save binary data to file, return JSON with path and size."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return _to_json({"path": os.path.abspath(path), "size": len(data)})


# ── Entry point ────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ozon-seller-cli",
        description="Ozon Seller: MCP server and CLI",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
        help="Show version and exit",
    )
    parser.add_argument("--env", help="Path to .env file")

    sub = parser.add_subparsers(dest="command")

    # ── Products ───────────────────────────────────────────────────

    p = sub.add_parser("product-list", help="List products")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {offer_id, product_id, visibility}")
    p.add_argument("--last-id", default="", help="Cursor for pagination")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    p = sub.add_parser("product-info", help="Get product info")
    p.add_argument("--offer-id", default="", help="Offer ID (seller SKU)")
    p.add_argument("--product-id", type=int, default=0, help="Ozon product ID")
    p.add_argument("--sku", type=int, default=0, help="Ozon SKU")

    p = sub.add_parser("product-info-list", help="Get info for multiple products")
    p.add_argument("--offer-ids", default="", help="Comma-separated offer IDs")
    p.add_argument("--product-ids", default="", help="Comma-separated product IDs")
    p.add_argument("--skus", default="", help="Comma-separated SKUs")

    p = sub.add_parser("product-import", help="Import products")
    p.add_argument("items_json", help="JSON array of product items: [{name, offer_id, ...}]")

    p = sub.add_parser("product-import-info", help="Get product import status")
    p.add_argument("task_id", type=int, help="Import task ID")

    p = sub.add_parser("product-update", help="Update products")
    p.add_argument("items_json", help="JSON array of items to update")

    p = sub.add_parser("product-prices-update", help="Update product prices")
    p.add_argument("prices_json", help="JSON array of prices: [{offer_id, price, ...}]")

    p = sub.add_parser("product-stocks-update", help="Update product stocks")
    p.add_argument("stocks_json", help="JSON array of stocks: [{offer_id, stock, ...}]")

    p = sub.add_parser("product-stocks-info", help="Get product stocks info")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {offer_id, product_id, visibility}")
    p.add_argument("--last-id", default="", help="Cursor for pagination")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    p = sub.add_parser("product-prices-info", help="Get product prices info")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {offer_id, product_id, visibility}")
    p.add_argument("--last-id", default="", help="Cursor for pagination")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    p = sub.add_parser("product-description", help="Get product description")
    p.add_argument("--offer-id", default="", help="Offer ID (seller SKU)")
    p.add_argument("--product-id", type=int, default=0, help="Ozon product ID")

    p = sub.add_parser("product-attributes", help="Get product attributes")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {offer_id, product_id, visibility}")
    p.add_argument("--last-id", default="", help="Cursor for pagination")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    p = sub.add_parser("product-archive", help="Archive products")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("product-unarchive", help="Unarchive products")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("product-delete", help="Delete products")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("product-pictures-import", help="Import product pictures")
    p.add_argument("images_json", help="JSON array of images: [{url, product_id, ...}]")

    p = sub.add_parser("product-pictures-info", help="Get product pictures status")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("product-geo-restrictions", help="Get product geo-restrictions")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--last-id", default="", help="Cursor for pagination")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    p = sub.add_parser("product-rating", help="Get content rating by SKU")
    p.add_argument("skus", help="Comma-separated list of SKUs")

    p = sub.add_parser("product-related-sku", help="Get related SKUs (FBO/FBS)")
    p.add_argument("items_json", help="JSON array of items: [{sku, ...}]")

    p = sub.add_parser("product-digital-codes", help="Upload digital activation codes")
    p.add_argument("product_id", type=int, help="Ozon product ID")
    p.add_argument("codes_json", help="JSON array of digital codes")

    # ── FBS Postings ───────────────────────────────────────────────

    p = sub.add_parser("fbs-list", help="List FBS postings")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {since, to, status, ...}")
    p.add_argument("--dir", default="ASC", help="Sort direction: ASC or DESC (default ASC)")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("fbs-get", help="Get FBS posting details")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("fbs-cancel", help="Cancel FBS posting")
    p.add_argument("posting_number", help="Posting number")
    p.add_argument("cancel_reason_id", type=int, help="Cancellation reason ID")
    p.add_argument("--message", default="", help="Cancellation message")

    p = sub.add_parser("fbs-cancel-reasons", help="List FBS cancellation reasons")

    p = sub.add_parser("fbs-tracking", help="Set tracking number for FBS posting")
    p.add_argument("posting_number", help="Posting number")
    p.add_argument("tracking_number", help="Tracking number")

    p = sub.add_parser("fbs-label", help="Download FBS posting label PDF")
    p.add_argument("posting_number", help="Posting number")
    p.add_argument("--output-dir", default=DEFAULT_LABELS_DIR, help="Output directory for label PDF")

    p = sub.add_parser("fbs-act-create", help="Create acceptance act")
    p.add_argument("delivery_method_id", type=int, help="Delivery method ID")
    p.add_argument("departure_date", help="Departure date (YYYY-MM-DD)")

    p = sub.add_parser("fbs-act-status", help="Get acceptance act status")
    p.add_argument("id", type=int, help="Act ID")

    p = sub.add_parser("fbs-act-pdf", help="Download acceptance act PDF")
    p.add_argument("id", type=int, help="Act ID")
    p.add_argument("--output-path", default="", help="Output file path for PDF")

    p = sub.add_parser("fbs-digital-act-pdf", help="Download digital acceptance act PDF")
    p.add_argument("id", type=int, help="Act ID")
    p.add_argument("--doc-type", default="act_of_acceptance", help="Document type (default act_of_acceptance)")
    p.add_argument("--output-path", default="", help="Output file path for PDF")

    p = sub.add_parser("fbs-container-labels", help="Download container labels PDF")
    p.add_argument("id", type=int, help="Act ID")
    p.add_argument("--output-path", default="", help="Output file path for PDF")

    p = sub.add_parser("fbs-delivered", help="Confirm posting delivery (rFBS)")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("fbs-last-mile", help="Ship last-mile posting")
    p.add_argument("posting_number", help="Posting number")
    p.add_argument("items_json", help="JSON array of items: [{quantity, sku}]")

    p = sub.add_parser("fbs-timeslot-restrictions", help="Get timeslot change restrictions")
    p.add_argument("delivery_method_id", type=int, help="Delivery method ID")

    p = sub.add_parser("fbs-restrictions", help="Get posting restrictions")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("fbs-country-set", help="Set product country of origin")
    p.add_argument("posting_number", help="Posting number")
    p.add_argument("product_id", type=int, help="Ozon product ID")
    p.add_argument("country_iso_code", help="Country ISO code (e.g. RU, CN)")

    p = sub.add_parser("fbs-country-list", help="List product countries of origin")

    # ── FBO ────────────────────────────────────────────────────────

    p = sub.add_parser("fbo-list", help="List FBO postings")
    p.add_argument("--filter-json", default="{}", help="JSON filter: {since, to, status, ...}")
    p.add_argument("--dir", default="ASC", help="Sort direction: ASC or DESC (default ASC)")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("fbo-get", help="Get FBO posting details")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("fbo-supply-create", help="Create supply order")
    p.add_argument("items_json", help="JSON array of supply items: [{sku, quantity}]")
    p.add_argument("warehouse_id", type=int, help="Warehouse ID")

    p = sub.add_parser("fbo-supply-get", help="Get supply order details")
    p.add_argument("supply_order_id", type=int, help="Supply order ID")

    p = sub.add_parser("fbo-supply-list", help="List supply orders")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")

    p = sub.add_parser("fbo-supply-cancel", help="Cancel supply order")
    p.add_argument("supply_order_id", type=int, help="Supply order ID")

    p = sub.add_parser("fbo-supply-items", help="Get supply order items")
    p.add_argument("supply_order_id", type=int, help="Supply order ID")

    p = sub.add_parser("fbo-supply-shipments", help="Get supply order shipments")
    p.add_argument("supply_order_id", type=int, help="Supply order ID")

    p = sub.add_parser("fbo-warehouse-workload", help="Get FBO warehouse workload")
    p.add_argument("warehouse_id", type=int, help="Warehouse ID")

    # ── Categories ─────────────────────────────────────────────────

    p = sub.add_parser("categories", help="Get category tree")
    p.add_argument("--language", default="DEFAULT", help="Language code (default DEFAULT)")

    p = sub.add_parser("category-attributes", help="Get category attributes")
    p.add_argument("description_category_id", type=int, help="Description category ID")
    p.add_argument("--language", default="DEFAULT", help="Language code (default DEFAULT)")
    p.add_argument("--type-id", type=int, default=0, help="Product type ID")

    p = sub.add_parser("category-values", help="Get attribute dictionary values")
    p.add_argument("attribute_id", type=int, help="Attribute ID")
    p.add_argument("description_category_id", type=int, help="Description category ID")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")
    p.add_argument("--last-value-id", type=int, default=0, help="Last value ID for pagination")

    p = sub.add_parser("category-values-search", help="Search attribute dictionary values")
    p.add_argument("attribute_id", type=int, help="Attribute ID")
    p.add_argument("description_category_id", type=int, help="Description category ID")
    p.add_argument("value", help="Search value")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")

    # ── Finance ────────────────────────────────────────────────────

    p = sub.add_parser("finance-transactions", help="List financial transactions")
    p.add_argument("filter_json", help="JSON filter: {date, transaction_type, ...}")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")

    p = sub.add_parser("finance-totals", help="Get transaction totals")
    p.add_argument("filter_json", help="JSON filter: {date, transaction_type, ...}")

    p = sub.add_parser("finance-cash-flow", help="Get cash flow statement")
    p.add_argument("filter_json", help="JSON filter: {date, ...}")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")

    p = sub.add_parser("finance-realization", help="Get realization report")
    p.add_argument("date", help="Report date (YYYY-MM-DD)")

    # ── Analytics ──────────────────────────────────────────────────

    p = sub.add_parser("analytics", help="Get analytics data")
    p.add_argument("date_from", help="Start date (YYYY-MM-DD)")
    p.add_argument("date_to", help="End date (YYYY-MM-DD)")
    p.add_argument("metrics_json", help='JSON array of metrics: ["revenue", "ordered_units", ...]')
    p.add_argument("dimensions_json", help='JSON array of dimensions: ["sku", "day", ...]')
    p.add_argument("--filters-json", default="", help="JSON array of filters")
    p.add_argument("--sort-json", default="", help="JSON array of sort rules")
    p.add_argument("--limit", type=int, default=1000, help="Max results (default 1000)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("analytics-stock", help="Get stock on warehouses")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")
    p.add_argument("--warehouse-type", default="", help="Warehouse type filter")

    p = sub.add_parser("analytics-turnover", help="Get item turnover")
    p.add_argument("date_from", help="Start date (YYYY-MM-DD)")
    p.add_argument("date_to", help="End date (YYYY-MM-DD)")
    p.add_argument("--skus", default="", help="Comma-separated list of SKUs")

    # ── Warehouses ─────────────────────────────────────────────────

    p = sub.add_parser("warehouses", help="List seller warehouses")

    p = sub.add_parser("delivery-methods", help="List delivery methods")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    # ── Returns ────────────────────────────────────────────────────

    p = sub.add_parser("returns-fbo", help="List FBO returns")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--last-id", type=int, default=0, help="Last ID for pagination")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")

    p = sub.add_parser("returns-fbs", help="List FBS returns")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--last-id", type=int, default=0, help="Last ID for pagination")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")

    p = sub.add_parser("return-get", help="Get return details")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("returns-rfbs", help="List rFBS returns")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--last-id", type=int, default=0, help="Last ID for pagination")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")

    p = sub.add_parser("return-rfbs-get", help="Get rFBS return details")
    p.add_argument("return_id", type=int, help="Return ID")

    p = sub.add_parser("return-rfbs-approve", help="Approve rFBS return")
    p.add_argument("return_id", type=int, help="Return ID")
    p.add_argument("--comment", default="", help="Approval comment")

    p = sub.add_parser("return-rfbs-reject", help="Reject rFBS return")
    p.add_argument("return_id", type=int, help="Return ID")
    p.add_argument("--comment", default="", help="Rejection comment")
    p.add_argument("--reject-reason-id", type=int, default=0, help="Rejection reason ID")

    p = sub.add_parser("return-rfbs-compensate", help="Compensate rFBS return")
    p.add_argument("return_id", type=int, help="Return ID")
    p.add_argument("compensation_amount", type=float, help="Compensation amount")

    # ── Chats ──────────────────────────────────────────────────────

    p = sub.add_parser("chats", help="List chats")
    p.add_argument("--chat-ids", default="", help="Comma-separated list of chat IDs")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=30, help="Page size (default 30)")

    p = sub.add_parser("chat-history", help="Get chat message history")
    p.add_argument("chat_id", help="Chat ID")
    p.add_argument("--from-message-id", default="", help="Start from this message ID")
    p.add_argument("--limit", type=int, default=50, help="Max messages (default 50)")
    p.add_argument("--direction", default="Forward", help="Direction: Forward or Backward (default Forward)")

    p = sub.add_parser("chat-start", help="Start a chat for a posting")
    p.add_argument("posting_number", help="Posting number")

    p = sub.add_parser("chat-send", help="Send a chat message")
    p.add_argument("chat_id", help="Chat ID")
    p.add_argument("message", help="Message text")

    p = sub.add_parser("chat-send-file", help="Send a file in chat")
    p.add_argument("chat_id", help="Chat ID")
    p.add_argument("base64_content", help="Base64-encoded file content")
    p.add_argument("--name", default="file", help="File name (default file)")

    p = sub.add_parser("chat-read", help="Mark chat as read")
    p.add_argument("chat_id", help="Chat ID")
    p.add_argument("from_message_id", help="Mark read from this message ID")

    # ── Promotions ─────────────────────────────────────────────────

    p = sub.add_parser("promos", help="List available promotions")

    p = sub.add_parser("promo-candidates", help="List promotion candidate products")
    p.add_argument("action_id", type=int, help="Promotion action ID")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("promo-products", help="List products in promotion")
    p.add_argument("action_id", type=int, help="Promotion action ID")
    p.add_argument("--limit", type=int, default=100, help="Max results (default 100)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("promo-products-add", help="Add products to promotion")
    p.add_argument("action_id", type=int, help="Promotion action ID")
    p.add_argument("products_json", help="JSON array of products: [{product_id, action_price}]")

    p = sub.add_parser("promo-products-remove", help="Remove products from promotion")
    p.add_argument("action_id", type=int, help="Promotion action ID")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("promo-hotsale", help="List Hot Sale promotions")

    # ── Strategies ─────────────────────────────────────────────────

    p = sub.add_parser("strategies", help="List pricing strategies")

    p = sub.add_parser("strategy-create", help="Create pricing strategy")
    p.add_argument("type", help="Strategy type")
    p.add_argument("update_type", help="Update type")
    p.add_argument("--name", default="", help="Strategy name")

    p = sub.add_parser("strategy-update", help="Update pricing strategy")
    p.add_argument("strategy_id", type=int, help="Strategy ID")
    p.add_argument("payload_json", help="JSON of fields to update")

    p = sub.add_parser("strategy-delete", help="Delete pricing strategy")
    p.add_argument("strategy_id", type=int, help="Strategy ID")

    # ── Rating ─────────────────────────────────────────────────────

    p = sub.add_parser("rating", help="Get seller rating summary")

    p = sub.add_parser("rating-history", help="Get rating history")
    p.add_argument("date_from", help="Start date (YYYY-MM-DD)")
    p.add_argument("date_to", help="End date (YYYY-MM-DD)")
    p.add_argument("--ratings", default="", help="Comma-separated list of rating names")

    p = sub.add_parser("quality-rating", help="Get quality rating")
    p.add_argument("date_from", help="Start date (YYYY-MM-DD)")
    p.add_argument("date_to", help="End date (YYYY-MM-DD)")
    p.add_argument("--warehouse-id", type=int, default=0, help="Warehouse ID filter")

    # ── Reports ────────────────────────────────────────────────────

    p = sub.add_parser("report-create", help="Create a report")
    p.add_argument("report_type", help="Report type")
    p.add_argument("--params-json", default="{}", help="JSON report parameters")

    p = sub.add_parser("report-info", help="Get report status")
    p.add_argument("code", help="Report code")

    p = sub.add_parser("report-list", help="List reports")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")
    p.add_argument("--report-type", default="", help="Filter by report type")

    p = sub.add_parser("report-download", help="Download report file")
    p.add_argument("code", help="Report code")
    p.add_argument("--output-path", default="", help="Output file path")

    # ── Reviews ────────────────────────────────────────────────────

    p = sub.add_parser("reviews", help="List reviews")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--sort-dir", default="DESC", help="Sort direction: ASC or DESC (default DESC)")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("review-info", help="Get review details")
    p.add_argument("review_id", type=int, help="Review ID")

    p = sub.add_parser("review-count", help="Get review count")
    p.add_argument("--filter-json", default="{}", help="JSON filter")

    p = sub.add_parser("review-comment", help="Reply to a review")
    p.add_argument("review_id", type=int, help="Review ID")
    p.add_argument("text", help="Reply text")

    # ── Questions ──────────────────────────────────────────────────

    p = sub.add_parser("questions", help="List questions")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--sort-dir", default="DESC", help="Sort direction: ASC or DESC (default DESC)")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("question-answer", help="Answer a question")
    p.add_argument("question_id", type=int, help="Question ID")
    p.add_argument("answer", help="Answer text")

    p = sub.add_parser("question-update", help="Update answer to a question")
    p.add_argument("question_id", type=int, help="Question ID")
    p.add_argument("answer", help="Updated answer text")

    # ── Cancellations ──────────────────────────────────────────────

    p = sub.add_parser("cancellations", help="List cancellation requests")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    p.add_argument("--offset", type=int, default=0, help="Offset for pagination (default 0)")

    p = sub.add_parser("cancellation-info", help="Get cancellation request details")
    p.add_argument("cancellation_id", type=int, help="Cancellation ID")

    p = sub.add_parser("cancellation-approve", help="Approve cancellation request")
    p.add_argument("cancellation_id", type=int, help="Cancellation ID")
    p.add_argument("--comment", default="", help="Approval comment")

    p = sub.add_parser("cancellation-reject", help="Reject cancellation request")
    p.add_argument("cancellation_id", type=int, help="Cancellation ID")
    p.add_argument("--comment", default="", help="Rejection comment")

    # ── Certificates ───────────────────────────────────────────────

    p = sub.add_parser("certificates", help="List certificates")
    p.add_argument("--filter-json", default="{}", help="JSON filter")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")

    p = sub.add_parser("certificate-info", help="Get certificate details")
    p.add_argument("certificate_id", type=int, help="Certificate ID")

    p = sub.add_parser("certificate-create", help="Create a certificate")
    p.add_argument("files_json", help="JSON array of files: [{url, name}]")
    p.add_argument("name", help="Certificate name")
    p.add_argument("type_code", help="Certificate type code")

    p = sub.add_parser("certificate-delete", help="Delete a certificate")
    p.add_argument("certificate_id", type=int, help="Certificate ID")

    p = sub.add_parser("certificate-bind", help="Bind certificate to products")
    p.add_argument("certificate_id", type=int, help="Certificate ID")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("certificate-unbind", help="Unbind certificate from products")
    p.add_argument("certificate_id", type=int, help="Certificate ID")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    # ── Barcodes ───────────────────────────────────────────────────

    p = sub.add_parser("barcode-generate", help="Generate barcodes for products")
    p.add_argument("product_ids", help="Comma-separated list of product IDs")

    p = sub.add_parser("barcode-add", help="Add barcodes to products")
    p.add_argument("barcodes_json", help="JSON array of barcodes: [{barcode, product_id}]")

    # ── Brands ─────────────────────────────────────────────────────

    p = sub.add_parser("brands", help="List brands")
    p.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    p.add_argument("--page-size", type=int, default=100, help="Page size (default 100)")

    # ── Parse & dispatch ───────────────────────────────────────────

    args = parser.parse_args(argv)

    if args.env:
        _load_env(args.env)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Helper: parse optional filter JSON, returns dict or None
    def _filt(raw: str) -> dict | None:
        d = _load_json(raw)
        return d or None

    handlers = {
        # Products
        "product-list": lambda: _to_json(
            _api().product_list(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "product-info": lambda: _to_json(
            _api().product_info(
                offer_id=args.offer_id,
                product_id=args.product_id,
                sku=args.sku,
            )
        ),
        "product-info-list": lambda: _to_json(
            _api().product_info_list(
                offer_id=[s.strip() for s in args.offer_ids.split(",") if s.strip()] or None,
                product_id=[int(s) for s in args.product_ids.split(",") if s.strip()] or None,
                sku=[int(s) for s in args.skus.split(",") if s.strip()] or None,
            )
        ),
        "product-import": lambda: _to_json(
            _api().product_import(_load_json(args.items_json))
        ),
        "product-import-info": lambda: _to_json(
            _api().product_import_info(args.task_id)
        ),
        "product-update": lambda: _to_json(
            _api().product_update(_load_json(args.items_json))
        ),
        "product-prices-update": lambda: _to_json(
            _api().product_prices_update(_load_json(args.prices_json))
        ),
        "product-stocks-update": lambda: _to_json(
            _api().product_stocks_update(_load_json(args.stocks_json))
        ),
        "product-stocks-info": lambda: _to_json(
            _api().product_stocks_info(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "product-prices-info": lambda: _to_json(
            _api().product_prices_info(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "product-description": lambda: _to_json(
            _api().product_description(
                offer_id=args.offer_id,
                product_id=args.product_id,
            )
        ),
        "product-attributes": lambda: _to_json(
            _api().product_attributes(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "product-archive": lambda: _to_json(
            _api().product_archive([int(x) for x in args.product_ids.split(",") if x.strip()])
        ),
        "product-unarchive": lambda: _to_json(
            _api().product_unarchive([int(x) for x in args.product_ids.split(",") if x.strip()])
        ),
        "product-delete": lambda: _to_json(
            _api().product_delete([int(x) for x in args.product_ids.split(",") if x.strip()])
        ),
        "product-pictures-import": lambda: _to_json(
            _api().product_pictures_import(_load_json(args.images_json))
        ),
        "product-pictures-info": lambda: _to_json(
            _api().product_pictures_info([int(x) for x in args.product_ids.split(",") if x.strip()])
        ),
        "product-geo-restrictions": lambda: _to_json(
            _api().product_geo_restrictions(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "product-rating": lambda: _to_json(
            _api().product_rating([int(x) for x in args.skus.split(",") if x.strip()])
        ),
        "product-related-sku": lambda: _to_json(
            _api().product_related_sku(_load_json(args.items_json))
        ),
        "product-digital-codes": lambda: _to_json(
            _api().product_upload_digital_codes(
                digital_codes=_load_json(args.codes_json),
                product_id=args.product_id,
            )
        ),
        # FBS
        "fbs-list": lambda: _to_json(
            _api().fbs_postings_list(
                filter_dict=_filt(args.filter_json),
                dir=args.dir,
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "fbs-get": lambda: _to_json(
            _api().fbs_posting_get(args.posting_number)
        ),
        "fbs-cancel": lambda: _to_json(
            _api().fbs_posting_cancel(
                args.posting_number,
                args.cancel_reason_id,
                args.message,
            )
        ),
        "fbs-cancel-reasons": lambda: _to_json(
            _api().fbs_cancel_reasons()
        ),
        "fbs-tracking": lambda: _to_json(
            _api().fbs_posting_tracking(args.posting_number, args.tracking_number)
        ),
        "fbs-label": lambda: (
            lambda pdf: _download(
                pdf,
                os.path.join(args.output_dir, f"{args.posting_number}.pdf"),
            )
        )(_api().get_label_pdf(args.posting_number)),
        "fbs-act-create": lambda: _to_json(
            _api().fbs_act_create(args.delivery_method_id, args.departure_date)
        ),
        "fbs-act-status": lambda: _to_json(
            _api().fbs_act_status(args.id)
        ),
        "fbs-act-pdf": lambda: (
            lambda data: _download(
                data,
                args.output_path or os.path.join(DEFAULT_DOCS_DIR, f"act_{args.id}.pdf"),
            )
        )(_api().fbs_act_pdf(args.id)),
        "fbs-digital-act-pdf": lambda: (
            lambda data: _download(
                data,
                args.output_path or os.path.join(DEFAULT_DOCS_DIR, f"digital_act_{args.id}.pdf"),
            )
        )(_api().fbs_digital_act_pdf(args.id, doc_type=args.doc_type)),
        "fbs-container-labels": lambda: (
            lambda data: _download(
                data,
                args.output_path or os.path.join(DEFAULT_DOCS_DIR, f"container_{args.id}.pdf"),
            )
        )(_api().fbs_container_labels(args.id)),
        "fbs-delivered": lambda: _to_json(
            _api().fbs_posting_delivered(args.posting_number)
        ),
        "fbs-last-mile": lambda: _to_json(
            _api().fbs_posting_last_mile(args.posting_number, _load_json(args.items_json))
        ),
        "fbs-timeslot-restrictions": lambda: _to_json(
            _api().fbs_timeslot_restrictions(args.delivery_method_id)
        ),
        "fbs-restrictions": lambda: _to_json(
            _api().fbs_restrictions(args.posting_number)
        ),
        "fbs-country-set": lambda: _to_json(
            _api().fbs_product_country_set(
                args.posting_number, args.product_id, args.country_iso_code,
            )
        ),
        "fbs-country-list": lambda: _to_json(
            _api().fbs_product_country_list()
        ),
        # FBO
        "fbo-list": lambda: _to_json(
            _api().fbo_postings_list(
                filter_dict=_filt(args.filter_json),
                dir=args.dir,
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "fbo-get": lambda: _to_json(
            _api().fbo_posting_get(args.posting_number)
        ),
        "fbo-supply-create": lambda: _to_json(
            _api().fbo_supply_create(_load_json(args.items_json), args.warehouse_id)
        ),
        "fbo-supply-get": lambda: _to_json(
            _api().fbo_supply_get(args.supply_order_id)
        ),
        "fbo-supply-list": lambda: _to_json(
            _api().fbo_supply_list(
                filter_dict=_filt(args.filter_json),
                page=args.page,
                page_size=args.page_size,
            )
        ),
        "fbo-supply-cancel": lambda: _to_json(
            _api().fbo_supply_cancel(args.supply_order_id)
        ),
        "fbo-supply-items": lambda: _to_json(
            _api().fbo_supply_items(args.supply_order_id)
        ),
        "fbo-supply-shipments": lambda: _to_json(
            _api().fbo_supply_shipments(args.supply_order_id)
        ),
        "fbo-warehouse-workload": lambda: _to_json(
            _api().fbo_warehouse_workload(args.warehouse_id)
        ),
        # Categories
        "categories": lambda: _to_json(
            _api().category_tree(language=args.language)
        ),
        "category-attributes": lambda: _to_json(
            _api().category_attributes(
                args.description_category_id,
                language=args.language,
                type_id=args.type_id,
            )
        ),
        "category-values": lambda: _to_json(
            _api().category_attribute_values(
                args.attribute_id,
                args.description_category_id,
                limit=args.limit,
                last_value_id=args.last_value_id,
            )
        ),
        "category-values-search": lambda: _to_json(
            _api().category_attribute_values_search(
                args.attribute_id,
                args.description_category_id,
                args.value,
                limit=args.limit,
            )
        ),
        # Finance
        "finance-transactions": lambda: _to_json(
            _api().finance_transactions(
                _load_json(args.filter_json),
                page=args.page,
                page_size=args.page_size,
            )
        ),
        "finance-totals": lambda: _to_json(
            _api().finance_totals(_load_json(args.filter_json))
        ),
        "finance-cash-flow": lambda: _to_json(
            _api().finance_cash_flow(
                _load_json(args.filter_json),
                page=args.page,
                page_size=args.page_size,
            )
        ),
        "finance-realization": lambda: _to_json(
            _api().finance_realization(args.date)
        ),
        # Analytics
        "analytics": lambda: _to_json(
            _api().analytics_data(
                args.date_from,
                args.date_to,
                _load_json(args.metrics_json),
                _load_json(args.dimensions_json),
                filters=_load_json(args.filters_json) if args.filters_json else None,
                sort=_load_json(args.sort_json) if args.sort_json else None,
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "analytics-stock": lambda: _to_json(
            _api().analytics_stock_on_warehouses(
                limit=args.limit,
                offset=args.offset,
                warehouse_type=args.warehouse_type,
            )
        ),
        "analytics-turnover": lambda: _to_json(
            _api().analytics_item_turnover(
                args.date_from,
                args.date_to,
                sku=[int(s) for s in args.skus.split(",") if s.strip()] or None,
            )
        ),
        # Warehouses
        "warehouses": lambda: _to_json(
            _api().warehouse_list()
        ),
        "delivery-methods": lambda: _to_json(
            _api().delivery_methods(
                filter_dict=_filt(args.filter_json),
                limit=args.limit,
                offset=args.offset,
            )
        ),
        # Returns
        "returns-fbo": lambda: _to_json(
            _api().returns_fbo(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "returns-fbs": lambda: _to_json(
            _api().returns_fbs(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "return-get": lambda: _to_json(
            _api().return_get(args.posting_number)
        ),
        "returns-rfbs": lambda: _to_json(
            _api().return_rfbs_list(
                filter_dict=_filt(args.filter_json),
                last_id=args.last_id,
                limit=args.limit,
            )
        ),
        "return-rfbs-get": lambda: _to_json(
            _api().return_rfbs_get(args.return_id)
        ),
        "return-rfbs-approve": lambda: _to_json(
            _api().return_rfbs_approve(args.return_id, comment=args.comment)
        ),
        "return-rfbs-reject": lambda: _to_json(
            _api().return_rfbs_reject(
                args.return_id,
                comment=args.comment,
                reject_reason_id=args.reject_reason_id,
            )
        ),
        "return-rfbs-compensate": lambda: _to_json(
            _api().return_rfbs_compensate(args.return_id, args.compensation_amount)
        ),
        # Chats
        "chats": lambda: _to_json(
            _api().chat_list(
                chat_id_list=[s.strip() for s in args.chat_ids.split(",") if s.strip()] or None,
                page=args.page,
                page_size=args.page_size,
            )
        ),
        "chat-history": lambda: _to_json(
            _api().chat_history(
                args.chat_id,
                from_message_id=args.from_message_id,
                limit=args.limit,
                direction=args.direction,
            )
        ),
        "chat-start": lambda: _to_json(
            _api().chat_start(args.posting_number)
        ),
        "chat-send": lambda: _to_json(
            _api().chat_send_message(args.chat_id, args.message)
        ),
        "chat-send-file": lambda: _to_json(
            _api().chat_send_file(args.chat_id, args.base64_content, name=args.name)
        ),
        "chat-read": lambda: _to_json(
            _api().chat_read(args.chat_id, args.from_message_id)
        ),
        # Promotions
        "promos": lambda: _to_json(
            _api().promo_available()
        ),
        "promo-candidates": lambda: _to_json(
            _api().promo_candidates(args.action_id, limit=args.limit, offset=args.offset)
        ),
        "promo-products": lambda: _to_json(
            _api().promo_products(args.action_id, limit=args.limit, offset=args.offset)
        ),
        "promo-products-add": lambda: _to_json(
            _api().promo_products_add(args.action_id, _load_json(args.products_json))
        ),
        "promo-products-remove": lambda: _to_json(
            _api().promo_products_remove(
                args.action_id,
                [int(x) for x in args.product_ids.split(",") if x.strip()],
            )
        ),
        "promo-hotsale": lambda: _to_json(
            _api().promo_hotsale_list()
        ),
        # Strategies
        "strategies": lambda: _to_json(
            _api().strategy_list()
        ),
        "strategy-create": lambda: _to_json(
            _api().strategy_create(args.type, args.update_type, name=args.name)
        ),
        "strategy-update": lambda: _to_json(
            _api().strategy_update(args.strategy_id, **_load_json(args.payload_json))
        ),
        "strategy-delete": lambda: _to_json(
            _api().strategy_delete(args.strategy_id)
        ),
        # Rating
        "rating": lambda: _to_json(
            _api().rating_summary()
        ),
        "rating-history": lambda: _to_json(
            _api().rating_history(
                args.date_from,
                args.date_to,
                ratings=[s.strip() for s in args.ratings.split(",") if s.strip()] or None,
            )
        ),
        "quality-rating": lambda: _to_json(
            _api().quality_rating(
                args.date_from,
                args.date_to,
                warehouse_id=args.warehouse_id,
            )
        ),
        # Reports
        "report-create": lambda: _to_json(
            _api().report_create(
                args.report_type,
                params=_filt(args.params_json),
            )
        ),
        "report-info": lambda: _to_json(
            _api().report_info(args.code)
        ),
        "report-list": lambda: _to_json(
            _api().report_list(
                page=args.page,
                page_size=args.page_size,
                report_type=args.report_type,
            )
        ),
        "report-download": lambda: (
            lambda data: _download(
                data,
                args.output_path or os.path.join(DEFAULT_DOCS_DIR, f"report_{args.code}"),
            )
        )(_api().report_download(args.code)),
        # Reviews
        "reviews": lambda: _to_json(
            _api().reviews_list(
                filter_dict=_filt(args.filter_json),
                sort_dir=args.sort_dir,
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "review-info": lambda: _to_json(
            _api().review_info(args.review_id)
        ),
        "review-count": lambda: _to_json(
            _api().review_count(filter_dict=_filt(args.filter_json))
        ),
        "review-comment": lambda: _to_json(
            _api().review_comment(args.review_id, args.text)
        ),
        # Questions
        "questions": lambda: _to_json(
            _api().questions_list(
                filter_dict=_filt(args.filter_json),
                sort_dir=args.sort_dir,
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "question-answer": lambda: _to_json(
            _api().question_answer(args.question_id, args.answer)
        ),
        "question-update": lambda: _to_json(
            _api().question_update(args.question_id, args.answer)
        ),
        # Cancellations
        "cancellations": lambda: _to_json(
            _api().cancellation_list(
                filter_dict=_filt(args.filter_json),
                limit=args.limit,
                offset=args.offset,
            )
        ),
        "cancellation-info": lambda: _to_json(
            _api().cancellation_info(args.cancellation_id)
        ),
        "cancellation-approve": lambda: _to_json(
            _api().cancellation_approve(args.cancellation_id, comment=args.comment)
        ),
        "cancellation-reject": lambda: _to_json(
            _api().cancellation_reject(args.cancellation_id, comment=args.comment)
        ),
        # Certificates
        "certificates": lambda: _to_json(
            _api().certificate_list(
                filter_dict=_filt(args.filter_json),
                page=args.page,
                page_size=args.page_size,
            )
        ),
        "certificate-info": lambda: _to_json(
            _api().certificate_info(args.certificate_id)
        ),
        "certificate-create": lambda: _to_json(
            _api().certificate_create(
                _load_json(args.files_json),
                args.name,
                args.type_code,
            )
        ),
        "certificate-delete": lambda: _to_json(
            _api().certificate_delete(args.certificate_id)
        ),
        "certificate-bind": lambda: _to_json(
            _api().certificate_bind(
                args.certificate_id,
                [int(x) for x in args.product_ids.split(",") if x.strip()],
            )
        ),
        "certificate-unbind": lambda: _to_json(
            _api().certificate_unbind(
                args.certificate_id,
                [int(x) for x in args.product_ids.split(",") if x.strip()],
            )
        ),
        # Barcodes
        "barcode-generate": lambda: _to_json(
            _api().barcode_generate([int(x) for x in args.product_ids.split(",") if x.strip()])
        ),
        "barcode-add": lambda: _to_json(
            _api().barcode_add(_load_json(args.barcodes_json))
        ),
        # Brands
        "brands": lambda: _to_json(
            _api().brand_list(page=args.page, page_size=args.page_size)
        ),
    }

    print(handlers[args.command]())


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        log.error(str(err))
        sys.exit(1)
