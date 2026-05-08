"""Pydantic models for Ozon Seller API action parameters.

Each model validates parameters for one or more ozon_execute actions.
Models use Field(description=...) so JSON schema is auto-generated for the LLM.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


# ── Shared / Reusable ─────────────────────────────────────────────────


class TaskIdParams(BaseModel):
    """Async task identifier (product import, etc.)."""

    task_id: int = Field(..., description="Task ID returned by the import action")


class PostingNumberParams(BaseModel):
    """Single posting number (reused by FBS/FBO get, deliver, restrictions, chat_start, return_get)."""

    posting_number: str = Field(..., description="Posting number (e.g. '12345678-0001-1')")


class IdParams(BaseModel):
    """Generic integer ID (reused by act_status, act_pdf, container_labels)."""

    id: int = Field(..., description="Entity ID (act, document, etc.)")


class ProductIdsParams(BaseModel):
    """List of product IDs (reused by archive, unarchive, delete, pictures_info, barcode_generate)."""

    product_id: list[int] = Field(..., description="List of product IDs")


class FilterLastIdLimitParams(BaseModel):
    """Cursor-based pagination with optional filter dict.

    Reused by product_list, product_stocks_info, product_prices_info,
    product_geo_restrictions.
    """

    filter_dict: dict | None = Field(None, description="Filter object (schema depends on endpoint)")
    last_id: str = Field("", description="Cursor for pagination (last_id from previous response)")
    limit: int = Field(100, description="Number of items to return per page")


class SupplyOrderIdParams(BaseModel):
    """Supply order identifier (reused by fbo_supply_get, cancel, items, shipments)."""

    supply_order_id: int = Field(..., description="Supply order ID")


class DeliveryMethodIdParams(BaseModel):
    """Delivery method identifier."""

    delivery_method_id: int = Field(..., description="Delivery method ID")


class WarehouseIdParams(BaseModel):
    """Warehouse identifier."""

    warehouse_id: int = Field(..., description="Warehouse ID")


class FilterPageParams(BaseModel):
    """Page-based pagination with optional filter dict (reused by fbo_supply_list)."""

    filter_dict: dict | None = Field(None, description="Filter object (schema depends on endpoint)")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(50, description="Number of items per page")


# ── Products ──────────────────────────────────────────────────────────


class ProductImportParams(BaseModel):
    """Parameters for product_import and product_update.

    Each item dict follows the Ozon product import schema with fields like
    offer_id, name, price, attributes, images, dimensions, etc.
    """

    items: list[dict] = Field(..., description="List of product item objects (Ozon product import schema)")


class ProductInfoParams(BaseModel):
    """Parameters for getting single product info.

    At least one identifier must be provided.
    """

    offer_id: str = Field("", description="Seller's product identifier (article)")
    product_id: int = Field(0, description="Ozon product ID")
    sku: int = Field(0, description="Ozon SKU")


class ProductInfoListParams(BaseModel):
    """Parameters for getting info on multiple products.

    At least one list must be provided.
    """

    offer_id: list[str] | None = Field(None, description="List of seller article identifiers")
    product_id: list[int] | None = Field(None, description="List of Ozon product IDs")
    sku: list[int] | None = Field(None, description="List of Ozon SKUs")


class ProductPricesUpdateParams(BaseModel):
    """Parameters for updating product prices.

    Each dict must contain product_id or offer_id plus price fields
    (price, old_price, min_price, currency_code, etc.).
    """

    prices: list[dict] = Field(..., description="List of price update objects ({product_id, price, old_price, ...})")


class ProductStocksUpdateParams(BaseModel):
    """Parameters for updating FBS product stocks.

    Each dict must contain offer_id or product_id, warehouse_id, and stock.
    """

    stocks: list[dict] = Field(..., description="List of stock update objects ({offer_id, warehouse_id, stock})")


class ProductDescriptionParams(BaseModel):
    """Parameters for getting product description.

    At least one identifier must be provided.
    """

    offer_id: str = Field("", description="Seller's product identifier (article)")
    product_id: int = Field(0, description="Ozon product ID")


class ProductAttributesParams(BaseModel):
    """Parameters for getting product attributes (extends FilterLastIdLimitParams with sort_dir)."""

    filter_dict: dict | None = Field(None, description="Filter object (e.g. {offer_id: [...], product_id: [...], visibility: 'ALL'})")
    last_id: str = Field("", description="Cursor for pagination")
    limit: int = Field(100, description="Number of items to return per page")
    sort_dir: str = Field("ASC", description="Sort direction: 'ASC' or 'DESC'")


class ProductPicturesImportParams(BaseModel):
    """Parameters for importing product images.

    Each dict must contain file_name, default (bool), and either url or base64.
    """

    images: list[dict] = Field(..., description="List of image objects ({file_name, default, url})")


class ProductRatingParams(BaseModel):
    """Parameters for getting product content rating by SKU."""

    skus: list[int] = Field(..., description="List of Ozon SKUs to get content rating for")


class ProductRelatedSkuParams(BaseModel):
    """Parameters for getting related SKU (FBO/FBS pairs).

    Each item dict must contain 'sku' (int) and 'item_type' (str).
    """

    items: list[dict] = Field(..., description="List of SKU query objects ({sku: int, item_type: str})")


class ProductDigitalCodesParams(BaseModel):
    """Parameters for uploading digital activation codes."""

    digital_codes: list[str] = Field(..., description="List of digital activation codes")
    product_id: int = Field(..., description="Product ID to attach codes to")


# ── FBS Postings ──────────────────────────────────────────────────────


class FbsPostingsListParams(BaseModel):
    """Parameters for listing FBS/FBO postings.

    Also reused by fbo_postings_list (same parameter signature).
    """

    filter_dict: dict | None = Field(None, description="Filter object ({since, to, status, delivery_method_id, ...})")
    dir: str = Field("ASC", description="Sort direction: 'ASC' or 'DESC'")
    limit: int = Field(50, description="Number of postings to return (max 50)")
    offset: int = Field(0, description="Offset for pagination")


class FbsPostingCancelParams(BaseModel):
    """Parameters for cancelling an FBS posting."""

    posting_number: str = Field(..., description="Posting number to cancel")
    cancel_reason_id: int = Field(..., description="Cancellation reason ID (from fbs_cancel_reasons)")
    cancel_reason_message: str = Field("", description="Optional message explaining the cancellation")


class FbsPostingTrackingParams(BaseModel):
    """Parameters for setting a tracking number on an FBS posting."""

    posting_number: str = Field(..., description="Posting number")
    tracking_number: str = Field(..., description="Tracking number from the carrier")


class FbsLabelParams(BaseModel):
    """Parameters for downloading a posting label PDF."""

    posting_number: str = Field(..., description="Posting number to get label for")
    retries: int = Field(3, description="Number of retry attempts for PDF download")


class FbsActCreateParams(BaseModel):
    """Parameters for creating an acceptance act."""

    delivery_method_id: int = Field(..., description="Delivery method ID")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DDTHH:MM:SSZ)")


class FbsDigitalActParams(BaseModel):
    """Parameters for downloading a digital act PDF."""

    id: int = Field(..., description="Act ID")
    doc_type: str = Field("act_of_acceptance", description="Document type: 'act_of_acceptance' or 'act_of_mismatch'")


class FbsLastMileParams(BaseModel):
    """Parameters for shipping a last-mile posting.

    Each item dict must contain sku (int) and quantity (int).
    """

    posting_number: str = Field(..., description="Posting number")
    items: list[dict] = Field(..., description="List of item objects ({sku: int, quantity: int})")


class FbsProductCountrySetParams(BaseModel):
    """Parameters for setting product country of origin in a posting."""

    posting_number: str = Field(..., description="Posting number")
    product_id: int = Field(..., description="Product ID")
    country_iso_code: str = Field(..., description="ISO 3166-1 alpha-2 country code (e.g. 'CN', 'RU')")


# ── FBO ───────────────────────────────────────────────────────────────


class FboSupplyCreateParams(BaseModel):
    """Parameters for creating an FBO supply order.

    Each item dict must contain sku (int) and quantity (int).
    """

    items: list[dict] = Field(..., description="List of supply items ({sku: int, quantity: int})")
    warehouse_id: int = Field(..., description="Target FBO warehouse ID")


# ── Categories ────────────────────────────────────────────────────────


class CategoryTreeParams(BaseModel):
    """Parameters for getting the category tree."""

    language: str = Field("DEFAULT", description="Language code: 'DEFAULT', 'RU', 'EN', 'TR', 'ZH_HANS'")


class CategoryAttributesParams(BaseModel):
    """Parameters for getting category attributes."""

    description_category_id: int = Field(..., description="Description category ID from category tree")
    language: str = Field("DEFAULT", description="Language code: 'DEFAULT', 'RU', 'EN', 'TR', 'ZH_HANS'")
    type_id: int = Field(0, description="Type ID (0 for all types)")


class CategoryAttributeValuesParams(BaseModel):
    """Parameters for getting attribute dictionary values."""

    attribute_id: int = Field(..., description="Attribute ID")
    description_category_id: int = Field(..., description="Description category ID")
    last_value_id: int = Field(0, description="Cursor for pagination (last value ID from previous response)")
    limit: int = Field(100, description="Number of values to return (max 5000)")
    language: str = Field("DEFAULT", description="Language code: 'DEFAULT', 'RU', 'EN', 'TR', 'ZH_HANS'")


class CategoryAttributeValuesSearchParams(BaseModel):
    """Parameters for searching attribute dictionary values."""

    attribute_id: int = Field(..., description="Attribute ID")
    description_category_id: int = Field(..., description="Description category ID")
    value: str = Field(..., description="Search query string")
    limit: int = Field(100, description="Number of values to return (max 5000)")
    language: str = Field("DEFAULT", description="Language code: 'DEFAULT', 'RU', 'EN', 'TR', 'ZH_HANS'")


# ── Finance ───────────────────────────────────────────────────────────


class FinanceTransactionsParams(BaseModel):
    """Parameters for listing financial transactions.

    The filter dict must contain date.from and date.to fields.
    May also include operation_type, posting_number, transaction_type.
    """

    filter_dict: dict = Field(..., description="Filter object ({date: {from, to}, operation_type: [...], ...})")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(50, description="Number of transactions per page (max 1000)")


class FinanceTotalsParams(BaseModel):
    """Parameters for getting finance totals.

    The filter dict must contain date.from and date.to fields.
    """

    filter_dict: dict = Field(..., description="Filter object ({date: {from, to}, ...})")


class FinanceCashFlowParams(BaseModel):
    """Parameters for getting cash flow statement.

    The filter dict must contain date.from and date.to fields.
    """

    filter_dict: dict = Field(..., description="Filter object ({date: {from, to}, ...})")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(50, description="Number of items per page (max 1000)")


class FinanceRealizationParams(BaseModel):
    """Parameters for getting the realization report."""

    date: str = Field(..., description="Report month in YYYY-MM format")


# ── Analytics ─────────────────────────────────────────────────────────


class AnalyticsDataParams(BaseModel):
    """Parameters for getting analytics data (sales, views, etc.).

    Available metrics: revenue, ordered_units, hits_view_search, hits_view_pdp,
    hits_view, hits_tocart, session_view_search, session_view_pdp, conv_tocart_search,
    conv_tocart_pdp, returns, cancellations, delivered_units, position_category.
    """

    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    metrics: list[str] = Field(..., description="List of metric names (e.g. ['revenue', 'ordered_units'])")
    dimensions: list[str] = Field(..., description="List of dimension names (e.g. ['sku', 'day'])")
    filters: list[dict] | None = Field(None, description="List of filter objects ({key, op, value})")
    sort: list[dict] | None = Field(None, description="List of sort objects ({key, order: 'ASC'|'DESC'})")
    limit: int = Field(1000, description="Number of rows to return (max 1000)")
    offset: int = Field(0, description="Offset for pagination")


class AnalyticsStockParams(BaseModel):
    """Parameters for getting stock on warehouses."""

    limit: int = Field(100, description="Number of items to return")
    offset: int = Field(0, description="Offset for pagination")
    warehouse_type: str = Field("", description="Warehouse type filter (empty for all)")


class AnalyticsItemTurnoverParams(BaseModel):
    """Parameters for getting item turnover analytics."""

    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    sku: list[int] | None = Field(None, description="List of SKUs to filter (None for all)")


# ── Warehouses ────────────────────────────────────────────────────────


class DeliveryMethodsParams(BaseModel):
    """Parameters for listing delivery methods."""

    filter_dict: dict | None = Field(None, description="Filter object ({warehouse_id, provider_id, status})")
    limit: int = Field(50, description="Number of items to return")
    offset: int = Field(0, description="Offset for pagination")


# ── Returns ───────────────────────────────────────────────────────────


class ReturnsFilterParams(BaseModel):
    """Cursor-based pagination for returns (reused by returns_fbo, returns_fbs, return_rfbs_list)."""

    filter_dict: dict | None = Field(None, description="Filter object ({posting_number, status, ...})")
    last_id: int = Field(0, description="Cursor for pagination (last return ID from previous response)")
    limit: int = Field(50, description="Number of returns to return")


class ReturnIdParams(BaseModel):
    """Single return identifier."""

    return_id: int = Field(..., description="Return ID")


class ReturnApproveParams(BaseModel):
    """Parameters for approving an rFBS return."""

    return_id: int = Field(..., description="Return ID to approve")
    comment: str = Field("", description="Optional approval comment")


class ReturnRejectParams(BaseModel):
    """Parameters for rejecting an rFBS return."""

    return_id: int = Field(..., description="Return ID to reject")
    comment: str = Field("", description="Optional rejection comment")
    reject_reason_id: int = Field(0, description="Rejection reason ID (0 if not specified)")


class ReturnCompensateParams(BaseModel):
    """Parameters for compensating an rFBS return."""

    return_id: int = Field(..., description="Return ID to compensate")
    compensation_amount: float = Field(..., description="Compensation amount in rubles")


# ── Chats ─────────────────────────────────────────────────────────────


class ChatListParams(BaseModel):
    """Parameters for listing chats."""

    chat_id_list: list[str] | None = Field(None, description="Filter by specific chat IDs (None for all)")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(30, description="Number of chats per page")


class ChatHistoryParams(BaseModel):
    """Parameters for getting chat message history."""

    chat_id: str = Field(..., description="Chat ID")
    from_message_id: str = Field("", description="Start from this message ID (empty for latest)")
    limit: int = Field(50, description="Number of messages to return")
    direction: str = Field("Forward", description="Direction: 'Forward' or 'Backward'")


class ChatSendMessageParams(BaseModel):
    """Parameters for sending a text message in a chat."""

    chat_id: str = Field(..., description="Chat ID")
    message: str = Field(..., description="Message text")


class ChatSendFileParams(BaseModel):
    """Parameters for sending a file in a chat."""

    chat_id: str = Field(..., description="Chat ID")
    base64_content: str = Field(..., description="File content encoded as base64 string")
    name: str = Field("file", description="File name")


class ChatReadParams(BaseModel):
    """Parameters for marking a chat as read."""

    chat_id: str = Field(..., description="Chat ID")
    from_message_id: str = Field(..., description="Mark all messages up to this ID as read")


# ── Promotions ────────────────────────────────────────────────────────


class PromoActionParams(BaseModel):
    """Parameters for listing promo candidates or promo products (reused by both)."""

    action_id: int = Field(..., description="Promotion action ID")
    limit: int = Field(100, description="Number of items to return")
    offset: int = Field(0, description="Offset for pagination")


class PromoProductsAddParams(BaseModel):
    """Parameters for adding products to a promotion.

    Each product dict must contain product_id and action_price.
    """

    action_id: int = Field(..., description="Promotion action ID")
    products: list[dict] = Field(..., description="List of product objects ({product_id: int, action_price: float})")


class PromoProductsRemoveParams(BaseModel):
    """Parameters for removing products from a promotion."""

    action_id: int = Field(..., description="Promotion action ID")
    product_ids: list[int] = Field(..., description="List of product IDs to remove from the promotion")


# ── Strategies ────────────────────────────────────────────────────────


class StrategyCreateParams(BaseModel):
    """Parameters for creating a pricing strategy."""

    type: str = Field(..., description="Strategy type (e.g. 'MIN_EXT_PRICE', 'COMP_PRICE')")
    update_type: str = Field(..., description="Update type (e.g. 'MANUAL', 'AUTO')")
    name: str = Field("", description="Strategy name (optional)")
    competitors: list[dict] | None = Field(None, description="List of competitor objects for price comparison")


class StrategyUpdateParams(BaseModel):
    """Parameters for updating a pricing strategy.

    Accepts strategy_id plus any additional fields forwarded to the API.
    """

    model_config = ConfigDict(extra="allow")

    strategy_id: int = Field(..., description="Strategy ID to update")


class StrategyIdParams(BaseModel):
    """Single strategy identifier."""

    strategy_id: int = Field(..., description="Strategy ID")


# ── Rating & Quality ─────────────────────────────────────────────────


class RatingHistoryParams(BaseModel):
    """Parameters for getting seller rating history."""

    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    ratings: list[str] | None = Field(None, description="Filter by rating names (None for all)")


class QualityRatingParams(BaseModel):
    """Parameters for getting quality rating."""

    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    warehouse_id: int = Field(0, description="Warehouse ID (0 for all warehouses)")


# ── Reports ───────────────────────────────────────────────────────────


class ReportCreateParams(BaseModel):
    """Parameters for creating a report."""

    report_type: str = Field(..., description="Report type (e.g. 'ALL_RETURNS', 'SELLER_PRODUCTS', 'SELLER_POSTINGS')")
    params: dict | None = Field(None, description="Additional report parameters (schema depends on report_type)")


class ReportCodeParams(BaseModel):
    """Report code identifier (reused by report_info and report_download)."""

    code: str = Field(..., description="Report code returned by report_create")


class ReportListParams(BaseModel):
    """Parameters for listing reports."""

    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(50, description="Number of reports per page")
    report_type: str = Field("", description="Filter by report type (empty for all)")


# ── Reviews ───────────────────────────────────────────────────────────


class ReviewsListParams(BaseModel):
    """Parameters for listing product reviews."""

    filter_dict: dict | None = Field(None, description="Filter object ({interaction_status, published, rating, ...})")
    sort_dir: str = Field("DESC", description="Sort direction: 'ASC' or 'DESC'")
    limit: int = Field(50, description="Number of reviews to return")
    offset: int = Field(0, description="Offset for pagination")


class ReviewIdParams(BaseModel):
    """Single review identifier."""

    review_id: int = Field(..., description="Review ID")


class ReviewCountParams(BaseModel):
    """Parameters for getting review count."""

    filter_dict: dict | None = Field(None, description="Filter object ({interaction_status, published, rating, ...})")


class ReviewCommentParams(BaseModel):
    """Parameters for posting a comment on a review."""

    review_id: int = Field(..., description="Review ID to comment on")
    text: str = Field(..., description="Comment text")


# ── Questions ─────────────────────────────────────────────────────────


class QuestionsListParams(BaseModel):
    """Parameters for listing product questions."""

    filter_dict: dict | None = Field(None, description="Filter object ({interaction_status, product_id, ...})")
    sort_dir: str = Field("DESC", description="Sort direction: 'ASC' or 'DESC'")
    limit: int = Field(50, description="Number of questions to return")
    offset: int = Field(0, description="Offset for pagination")


class QuestionAnswerParams(BaseModel):
    """Parameters for answering or updating a question (reused by question_answer and question_update)."""

    question_id: int = Field(..., description="Question ID")
    answer: str = Field(..., description="Answer text")


# ── Cancellations ─────────────────────────────────────────────────────


class CancellationListParams(BaseModel):
    """Parameters for listing cancellation requests."""

    filter_dict: dict | None = Field(None, description="Filter object ({posting_number, state, ...})")
    limit: int = Field(50, description="Number of cancellations to return")
    offset: int = Field(0, description="Offset for pagination")


class CancellationIdParams(BaseModel):
    """Single cancellation identifier."""

    cancellation_id: int = Field(..., description="Cancellation request ID")


class CancellationApproveParams(BaseModel):
    """Parameters for approving or rejecting a cancellation request.

    Reused by both cancellation_approve and cancellation_reject.
    """

    cancellation_id: int = Field(..., description="Cancellation request ID")
    comment: str = Field("", description="Optional comment explaining the decision")


# ── Certificates ──────────────────────────────────────────────────────


class CertificateListParams(BaseModel):
    """Parameters for listing certificates."""

    filter_dict: dict | None = Field(None, description="Filter object ({status, type_code, ...})")
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(50, description="Number of certificates per page")


class CertificateIdParams(BaseModel):
    """Single certificate identifier (reused by certificate_info and certificate_delete)."""

    certificate_id: int = Field(..., description="Certificate ID")


class CertificateCreateParams(BaseModel):
    """Parameters for creating a certificate.

    Accepts required fields plus any additional fields forwarded to the API.
    Each file dict must contain {file_name, file_content_base64}.
    """

    model_config = ConfigDict(extra="allow")

    files: list[dict] = Field(..., description="List of file objects ({file_name, file_content_base64})")
    name: str = Field(..., description="Certificate name")
    type_code: str = Field(..., description="Certificate type code (e.g. 'DECLARATION', 'CERTIFICATE')")


class CertificateBindParams(BaseModel):
    """Parameters for binding or unbinding a certificate to products.

    Reused by both certificate_bind and certificate_unbind.
    """

    certificate_id: int = Field(..., description="Certificate ID")
    product_id: list[int] = Field(..., description="List of product IDs to bind/unbind")


# ── Barcodes ──────────────────────────────────────────────────────────


class BarcodeAddParams(BaseModel):
    """Parameters for adding barcodes to products.

    Each dict must contain product_id (int) and barcode (str).
    """

    barcodes: list[dict] = Field(..., description="List of barcode objects ({product_id: int, barcode: str})")


# ── Brands ────────────────────────────────────────────────────────────


class BrandListParams(BaseModel):
    """Parameters for listing seller brands."""

    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(100, description="Number of brands per page")
