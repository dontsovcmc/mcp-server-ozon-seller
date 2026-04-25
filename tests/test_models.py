"""Тест: валидация pydantic-моделей."""

import pytest
from mcp_server_ozon_seller.models import (
    ProductItem, Posting, PostingProduct, FboPosting,
    Category, Transaction, Warehouse, Chat, Promotion,
    Strategy, Review, Question, Cancellation, Certificate,
    RatingSummary, ReportInfo, Brand, ReturnItem,
)


def test_product_item_defaults():
    item = ProductItem()
    assert item.product_id == 0
    assert item.offer_id == ""


def test_posting_with_products():
    p = Posting(
        posting_number="TEST-001",
        status="awaiting_packaging",
        products=[PostingProduct(name="Товар", sku=100, quantity=2)],
    )
    assert len(p.products) == 1
    assert p.products[0].sku == 100


def test_extra_fields_allowed():
    item = ProductItem.model_validate({"product_id": 1, "unknown_field": "value"})
    assert item.product_id == 1


def test_all_models_instantiate():
    models = [
        ProductItem, Posting, FboPosting, Category, Transaction,
        Warehouse, Chat, Promotion, Strategy, Review, Question,
        Cancellation, Certificate, RatingSummary, ReportInfo,
        Brand, ReturnItem,
    ]
    for model_cls in models:
        obj = model_cls()
        assert obj is not None


def test_category_recursive():
    cat = Category(
        category_id=1,
        title="Родитель",
        children=[Category(category_id=2, title="Потомок")],
    )
    assert len(cat.children) == 1
    assert cat.children[0].title == "Потомок"
