"""Pydantic-модели Ozon Seller API.

Используются для валидации структуры данных в тестах.
Сервер и API-клиент работают с dict — модели не меняют интерфейс.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# ── Common ─────────────────────────────────────────────────────────


class Pagination(BaseModel):
    model_config = ConfigDict(extra="allow")
    offset: int = 0
    limit: int = 100
    total: int = 0


class DateRange(BaseModel):
    model_config = ConfigDict(extra="allow")
    date_from: str = ""
    date_to: str = ""


# ── Products ───────────────────────────────────────────────────────


class ProductItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    product_id: int = 0
    offer_id: str = ""
    name: str = ""
    sku: int = 0
    barcode: str = ""
    category_id: int = 0
    price: str = ""
    old_price: str = ""
    min_price: str = ""
    vat: str = ""
    visible: bool = True
    visibility_details: dict = {}
    stocks: dict = {}
    sources: list = []


class ProductListFilter(BaseModel):
    model_config = ConfigDict(extra="allow")
    offer_id: list[str] = []
    product_id: list[int] = []
    visibility: str = "ALL"


class ProductListRequest(BaseModel):
    filter: ProductListFilter = ProductListFilter()
    last_id: str = ""
    limit: int = 100


class ProductListResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    items: list[ProductItem] = []
    total: int = 0
    last_id: str = ""


class ProductImportItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    attributes: list[dict] = []
    barcode: str = ""
    category_id: int = 0
    color_image: str = ""
    complex_attributes: list[dict] = []
    currency_code: str = "RUB"
    depth: int = 0
    dimension_unit: str = "mm"
    height: int = 0
    images: list[str] = []
    images360: list[str] = []
    name: str = ""
    offer_id: str = ""
    old_price: str = ""
    pdf_list: list[dict] = []
    premium_price: str = ""
    price: str = ""
    primary_image: str = ""
    vat: str = "0"
    weight: int = 0
    weight_unit: str = "g"
    width: int = 0


class ProductImportRequest(BaseModel):
    items: list[ProductImportItem] = []


class ProductImportResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    task_id: int = 0


class ProductStockUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    offer_id: str = ""
    product_id: int = 0
    stock: int = 0
    warehouse_id: int = 0


class ProductStocksUpdateRequest(BaseModel):
    stocks: list[ProductStockUpdate] = []


class ProductPriceUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    auto_action_enabled: str = "UNKNOWN"
    currency_code: str = "RUB"
    min_price: str = ""
    offer_id: str = ""
    old_price: str = ""
    price: str = ""
    product_id: int = 0


class ProductPricesUpdateRequest(BaseModel):
    prices: list[ProductPriceUpdate] = []


class ProductStocksInfoItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    product_id: int = 0
    offer_id: str = ""
    stocks: list[dict] = []


class ProductPricesInfoItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    product_id: int = 0
    offer_id: str = ""
    price: dict = {}
    commissions: dict = {}


class ProductAttributeItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0
    offer_id: str = ""
    attributes: list[dict] = []


# ── FBS Postings ───────────────────────────────────────────────────


class PostingProduct(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = ""
    sku: int = 0
    quantity: int = 0
    offer_id: str = ""
    price: str = ""
    currency_code: str = "RUB"


class PostingAddress(BaseModel):
    model_config = ConfigDict(extra="allow")
    city: str = ""
    street: str = ""
    house: str = ""
    flat: str = ""
    zip_code: str = ""
    region: str = ""
    address_tail: str = ""
    comment: str = ""


class Posting(BaseModel):
    model_config = ConfigDict(extra="allow")
    posting_number: str = ""
    order_number: str = ""
    order_id: int = 0
    status: str = ""
    substatus: str = ""
    shipment_date: str = ""
    delivering_date: str = ""
    tracking_number: str = ""
    products: list[PostingProduct] = []
    delivery_method: dict = {}
    analytics_data: dict = {}
    financial_data: dict = {}


class PostingListFilter(BaseModel):
    model_config = ConfigDict(extra="allow")
    since: str = ""
    to: str = ""
    status: str = ""
    delivery_method_id: list[int] = []
    provider_id: list[int] = []
    warehouse_id: list[int] = []


class PostingListRequest(BaseModel):
    dir: str = "ASC"
    filter: PostingListFilter = PostingListFilter()
    limit: int = 50
    offset: int = 0


class PostingShipItem(BaseModel):
    sku: int = 0
    quantity: int = 0


class PostingShipRequest(BaseModel):
    posting_number: str = ""
    packages: list[dict] = []


class PostingCancelRequest(BaseModel):
    cancel_reason_id: int = 0
    cancel_reason_message: str = ""
    posting_number: str = ""


class CancelReason(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0
    title: str = ""
    type_id: int = 0
    is_available_for_cancellation: bool = False


class ActCreateRequest(BaseModel):
    delivery_method_id: int = 0
    departure_date: str = ""


class ActCreateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0


class ActStatusResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    added_to_act: list[str] = []
    removed_from_act: list[str] = []
    status: str = ""


# ── FBO ────────────────────────────────────────────────────────────


class FboPosting(BaseModel):
    model_config = ConfigDict(extra="allow")
    posting_number: str = ""
    order_number: str = ""
    status: str = ""
    created_at: str = ""
    in_process_at: str = ""
    products: list[PostingProduct] = []
    analytics_data: dict = {}
    financial_data: dict = {}


class FboPostingListFilter(BaseModel):
    model_config = ConfigDict(extra="allow")
    since: str = ""
    to: str = ""
    status: str = ""


class SupplyOrder(BaseModel):
    model_config = ConfigDict(extra="allow")
    supply_order_id: int = 0
    state: str = ""
    created_at: str = ""
    updated_at: str = ""
    local_timeslot: dict = {}
    total_items_count: int = 0
    warehouse: dict = {}


class SupplyOrderItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    sku: int = 0
    quantity: int = 0
    name: str = ""
    offer_id: str = ""


# ── Categories ─────────────────────────────────────────────────────


class Category(BaseModel):
    model_config = ConfigDict(extra="allow")
    category_id: int = 0
    title: str = ""
    description_category_id: int = 0
    children: list[Category] = []


class CategoryAttribute(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0
    name: str = ""
    description: str = ""
    type: str = ""
    is_collection: bool = False
    is_required: bool = False
    dictionary_id: int = 0
    group_id: int = 0
    group_name: str = ""


class AttributeValue(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0
    value: str = ""
    info: str = ""
    picture: str = ""


# ── Finance ────────────────────────────────────────────────────────


class Transaction(BaseModel):
    model_config = ConfigDict(extra="allow")
    operation_id: int = 0
    operation_type: str = ""
    operation_date: str = ""
    operation_type_name: str = ""
    delivery_charge: float = 0.0
    return_delivery_charge: float = 0.0
    commission_amount: float = 0.0
    commission_percent: float = 0.0
    payout: float = 0.0
    amount: float = 0.0
    accruals_for_sale: float = 0.0
    sale_commission: float = 0.0
    posting: dict = {}
    items: list[dict] = []
    services: list[dict] = []


class TransactionListRequest(BaseModel):
    filter: dict = {}
    page: int = 1
    page_size: int = 50


class TransactionListResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    operations: list[Transaction] = []
    page_count: int = 0
    row_count: int = 0


class FinanceTotals(BaseModel):
    model_config = ConfigDict(extra="allow")
    accruals_for_sale: float = 0.0
    sale_commission: float = 0.0
    processing_and_delivery: float = 0.0
    return_amount: float = 0.0
    compensation_amount: float = 0.0


class CashFlowItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    period: dict = {}
    orders_amount: float = 0.0
    returns_amount: float = 0.0
    commission_amount: float = 0.0
    services_amount: float = 0.0
    item_amount: float = 0.0


# ── Analytics ──────────────────────────────────────────────────────


class AnalyticsRequest(BaseModel):
    date_from: str = ""
    date_to: str = ""
    metrics: list[str] = []
    dimensions: list[str] = []
    filters: list[dict] = []
    sort: list[dict] = []
    limit: int = 1000
    offset: int = 0


class AnalyticsDataItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    dimensions: list[dict] = []
    metrics: list[float] = []


class AnalyticsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    data: list[AnalyticsDataItem] = []
    totals: list[float] = []


class StockOnWarehouseItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    sku: int = 0
    item_code: str = ""
    item_name: str = ""
    free_to_sell_amount: int = 0
    promised_amount: int = 0
    reserved_amount: int = 0
    warehouse_name: str = ""


# ── Warehouses ─────────────────────────────────────────────────────


class Warehouse(BaseModel):
    model_config = ConfigDict(extra="allow")
    warehouse_id: int = 0
    name: str = ""
    is_rfbs: bool = False
    has_entrusted_acceptance: bool = False
    first_mile_type: dict = {}
    status: str = ""


class DeliveryMethod(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int = 0
    name: str = ""
    warehouse_id: int = 0
    company_id: int = 0
    provider_id: int = 0
    status: str = ""
    cutoff: dict = {}


# ── Returns ────────────────────────────────────────────────────────


class ReturnItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    return_id: int = 0
    posting_number: str = ""
    status: str = ""
    return_reason_name: str = ""
    created_at: str = ""
    product_id: int = 0
    sku: int = 0
    product_name: str = ""
    quantity: int = 0


class ReturnFboItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    accepted_from_customer_moment: str = ""
    posting_number: str = ""
    return_reason_name: str = ""
    sku: int = 0
    product_id: int = 0
    product_name: str = ""
    quantity: int = 0
    status: str = ""


class RfbsReturn(BaseModel):
    model_config = ConfigDict(extra="allow")
    return_id: int = 0
    order_id: int = 0
    order_number: str = ""
    posting_number: str = ""
    status: str = ""
    return_reason: str = ""
    return_reason_name: str = ""
    created_at: str = ""
    items: list[dict] = []


# ── Chats ──────────────────────────────────────────────────────────


class Chat(BaseModel):
    model_config = ConfigDict(extra="allow")
    chat_id: str = ""
    chat_type: str = ""
    created_at: str = ""
    last_message_id: str = ""
    first_unread_message_id: str = ""


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    message_id: str = ""
    user: dict = {}
    message: str = ""
    created_at: str = ""
    is_read: bool = False
    data: dict = {}


class ChatListRequest(BaseModel):
    chat_id_list: list[str] = []
    page: int = 1
    page_size: int = 30


class ChatHistoryRequest(BaseModel):
    chat_id: str = ""
    from_message_id: str = ""
    limit: int = 50
    direction: str = "Forward"


# ── Promotions & Strategies ───────────────────────────────────────


class Promotion(BaseModel):
    model_config = ConfigDict(extra="allow")
    action_id: int = 0
    title: str = ""
    date_start: str = ""
    date_end: str = ""
    potential_products_count: int = 0
    participating_products_count: int = 0
    is_participating: bool = False
    action_type: str = ""
    banned_products_count: int = 0


class PromoCandidateProduct(BaseModel):
    model_config = ConfigDict(extra="allow")
    product_id: int = 0
    price: float = 0.0
    action_price: float = 0.0
    max_action_price: float = 0.0
    add_mode: str = ""
    min_stock: int = 0
    stock: int = 0


class Strategy(BaseModel):
    model_config = ConfigDict(extra="allow")
    strategy_id: int = 0
    type: str = ""
    name: str = ""
    enabled: bool = False
    created_at: str = ""
    updated_at: str = ""
    products_count: int = 0


# ── Rating & Quality ──────────────────────────────────────────────


class RatingItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    rating: float = 0.0
    rating_direction: str = ""
    status: dict = {}
    value: float = 0.0


class RatingGroup(BaseModel):
    model_config = ConfigDict(extra="allow")
    group_name: str = ""
    items: list[RatingItem] = []


class RatingSummary(BaseModel):
    model_config = ConfigDict(extra="allow")
    groups: list[RatingGroup] = []
    premium: bool = False


# ── Reviews ────────────────────────────────────────────────────────


class Review(BaseModel):
    model_config = ConfigDict(extra="allow")
    review_id: int = 0
    rating: int = 0
    text: str = ""
    created_at: str = ""
    product_id: int = 0
    sku: int = 0
    author: dict = {}
    photos: list[dict] = []
    comments: list[dict] = []


class ReviewComment(BaseModel):
    model_config = ConfigDict(extra="allow")
    comment_id: int = 0
    text: str = ""
    created_at: str = ""
    author_type: str = ""


# ── Questions ──────────────────────────────────────────────────────


class Question(BaseModel):
    model_config = ConfigDict(extra="allow")
    question_id: int = 0
    text: str = ""
    created_at: str = ""
    product_id: int = 0
    sku: int = 0
    answer: str = ""
    is_answered: bool = False


# ── Cancellations ─────────────────────────────────────────────────


class Cancellation(BaseModel):
    model_config = ConfigDict(extra="allow")
    cancellation_id: int = 0
    posting_number: str = ""
    state: str = ""
    cancel_reason: str = ""
    cancellation_initiator: str = ""
    approve_comment: str = ""
    reject_comment: str = ""
    created_at: str = ""


# ── Certificates ──────────────────────────────────────────────────


class Certificate(BaseModel):
    model_config = ConfigDict(extra="allow")
    certificate_id: int = 0
    name: str = ""
    type: str = ""
    status: str = ""
    rejection_reasons: list[str] = []
    created_at: str = ""
    expire_date: str = ""


# ── Reports ────────────────────────────────────────────────────────


class ReportCreateRequest(BaseModel):
    report_type: str = ""
    params: dict = {}


class ReportInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    code: str = ""
    status: str = ""
    error: str = ""
    file: str = ""
    report_type: str = ""
    created_at: str = ""
    params: dict = {}


# ── Brands ─────────────────────────────────────────────────────────


class Brand(BaseModel):
    model_config = ConfigDict(extra="allow")
    brand_id: int = 0
    name: str = ""
    has_certificate: bool = False
