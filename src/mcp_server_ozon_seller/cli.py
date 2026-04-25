"""CLI для Ozon Seller API.

Usage: ozon-seller-cli <command> [options]
"""

import argparse
import json
import os
import sys
import logging

from . import __version__
from . import server

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger(__name__)

DEFAULT_LABELS_DIR = os.path.expanduser("~/.config/mcp-server-ozon-seller/labels")


def _load_env(path: str) -> None:
    """Простая загрузка .env без внешних зависимостей."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл окружения не найден: {path}")
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
    log.info(f"Загружены переменные из {path}")


# ── Entry point ─────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ozon-seller-cli",
        description="Ozon Seller: MCP-сервер и CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--env", help="Путь к .env файлу")

    sub = parser.add_subparsers(dest="command")

    # ── Legacy commands ────────────────────────────────────────────

    p = sub.add_parser("list", help="Список несобранных FBS-заказов")
    p.add_argument("--days", type=int, default=7)

    p = sub.add_parser("labels", help="Скачать PDF-этикетки")
    p.add_argument("--posting", nargs="*", help="Номера отправлений")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--output-dir", dest="output_dir", default=DEFAULT_LABELS_DIR)

    p = sub.add_parser("ship", help="Собрать заказы")
    p.add_argument("--posting", nargs="*", help="Номера отправлений")
    p.add_argument("--all", action="store_true")
    p.add_argument("--days", type=int, default=7)

    # ── Products ───────────────────────────────────────────────────

    p = sub.add_parser("product-list", help="Список товаров")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("product-info", help="Информация о товаре")
    p.add_argument("--offer-id", default="")
    p.add_argument("--product-id", type=int, default=0)
    p.add_argument("--sku", type=int, default=0)

    p = sub.add_parser("product-info-list", help="Информация о нескольких товарах")
    p.add_argument("--offer-ids", default="")
    p.add_argument("--product-ids", default="")
    p.add_argument("--skus", default="")

    p = sub.add_parser("product-import", help="Импорт товаров")
    p.add_argument("items_json")

    p = sub.add_parser("product-import-info", help="Статус импорта")
    p.add_argument("task_id", type=int)

    p = sub.add_parser("product-update", help="Обновить товары")
    p.add_argument("items_json")

    p = sub.add_parser("product-prices-update", help="Обновить цены")
    p.add_argument("prices_json")

    p = sub.add_parser("product-stocks-update", help="Обновить остатки")
    p.add_argument("stocks_json")

    p = sub.add_parser("product-stocks-info", help="Информация об остатках")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("product-prices-info", help="Информация о ценах")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("product-description", help="Описание товара")
    p.add_argument("--offer-id", default="")
    p.add_argument("--product-id", type=int, default=0)

    p = sub.add_parser("product-attributes", help="Атрибуты товаров")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("product-archive", help="Архивировать товары")
    p.add_argument("product_ids")

    p = sub.add_parser("product-unarchive", help="Разархивировать товары")
    p.add_argument("product_ids")

    p = sub.add_parser("product-delete", help="Удалить товары")
    p.add_argument("product_ids")

    p = sub.add_parser("product-rating", help="Контент-рейтинг по SKU")
    p.add_argument("skus")

    p = sub.add_parser("product-related-sku", help="Связанные SKU")
    p.add_argument("items_json")

    # ── FBS Postings ───────────────────────────────────────────────

    p = sub.add_parser("fbs-list", help="Список FBS-отправлений")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--offset", type=int, default=0)

    p = sub.add_parser("fbs-get", help="Детали FBS-отправления")
    p.add_argument("posting_number")

    p = sub.add_parser("fbs-ship", help="Собрать FBS-отправление")
    p.add_argument("posting_number")
    p.add_argument("items_json")

    p = sub.add_parser("fbs-cancel", help="Отменить FBS-отправление")
    p.add_argument("posting_number")
    p.add_argument("cancel_reason_id", type=int)
    p.add_argument("--message", default="")

    p = sub.add_parser("fbs-cancel-reasons", help="Причины отмены FBS")

    p = sub.add_parser("fbs-tracking", help="Установить трек-номер")
    p.add_argument("posting_number")
    p.add_argument("tracking_number")

    p = sub.add_parser("fbs-label", help="Скачать этикетку")
    p.add_argument("posting_number")
    p.add_argument("--output-dir", default=DEFAULT_LABELS_DIR)

    p = sub.add_parser("fbs-act-create", help="Создать акт")
    p.add_argument("delivery_method_id", type=int)
    p.add_argument("departure_date")

    p = sub.add_parser("fbs-act-status", help="Статус акта")
    p.add_argument("id", type=int)

    p = sub.add_parser("fbs-act-pdf", help="Скачать PDF акта")
    p.add_argument("id", type=int)
    p.add_argument("--output-path", default="")

    p = sub.add_parser("fbs-restrictions", help="Ограничения отправления")
    p.add_argument("posting_number")

    p = sub.add_parser("fbs-country-list", help="Список стран-производителей")

    # ── FBO ────────────────────────────────────────────────────────

    p = sub.add_parser("fbo-list", help="Список FBO-отправлений")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--offset", type=int, default=0)

    p = sub.add_parser("fbo-get", help="Детали FBO-отправления")
    p.add_argument("posting_number")

    p = sub.add_parser("fbo-supply-list", help="Список поставок")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("fbo-supply-get", help="Детали поставки")
    p.add_argument("supply_order_id", type=int)

    p = sub.add_parser("fbo-supply-cancel", help="Отменить поставку")
    p.add_argument("supply_order_id", type=int)

    p = sub.add_parser("fbo-supply-items", help="Товары поставки")
    p.add_argument("supply_order_id", type=int)

    # ── Categories ─────────────────────────────────────────────────

    sub.add_parser("categories", help="Дерево категорий")

    p = sub.add_parser("category-attributes", help="Атрибуты категории")
    p.add_argument("description_category_id", type=int)

    p = sub.add_parser("category-values", help="Значения словаря атрибута")
    p.add_argument("attribute_id", type=int)
    p.add_argument("description_category_id", type=int)
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("category-values-search", help="Поиск по словарю")
    p.add_argument("attribute_id", type=int)
    p.add_argument("description_category_id", type=int)
    p.add_argument("value")

    # ── Finance ────────────────────────────────────────────────────

    p = sub.add_parser("finance-transactions", help="Финансовые транзакции")
    p.add_argument("filter_json")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=50)

    p = sub.add_parser("finance-totals", help="Итоги по транзакциям")
    p.add_argument("filter_json")

    p = sub.add_parser("finance-cash-flow", help="Движение денежных средств")
    p.add_argument("filter_json")

    p = sub.add_parser("finance-realization", help="Отчёт о реализации")
    p.add_argument("date")

    # ── Analytics ──────────────────────────────────────────────────

    p = sub.add_parser("analytics", help="Аналитические данные")
    p.add_argument("date_from")
    p.add_argument("date_to")
    p.add_argument("metrics_json")
    p.add_argument("dimensions_json")

    p = sub.add_parser("analytics-stock", help="Остатки на складах")
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("analytics-turnover", help="Оборачиваемость товаров")
    p.add_argument("date_from")
    p.add_argument("date_to")
    p.add_argument("--skus", default="")

    # ── Warehouses ─────────────────────────────────────────────────

    sub.add_parser("warehouses", help="Склады продавца")

    p = sub.add_parser("delivery-methods", help="Способы доставки")
    p.add_argument("--filter-json", default="{}")

    # ── Returns ────────────────────────────────────────────────────

    p = sub.add_parser("returns-fbo", help="Возвраты FBO")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("returns-fbs", help="Возвраты FBS")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("return-get", help="Детали возврата")
    p.add_argument("posting_number")

    p = sub.add_parser("returns-rfbs", help="Возвраты rFBS")
    p.add_argument("--filter-json", default="{}")

    p = sub.add_parser("return-rfbs-get", help="Детали возврата rFBS")
    p.add_argument("return_id", type=int)

    p = sub.add_parser("return-rfbs-approve", help="Одобрить возврат rFBS")
    p.add_argument("return_id", type=int)
    p.add_argument("--comment", default="")

    p = sub.add_parser("return-rfbs-reject", help="Отклонить возврат rFBS")
    p.add_argument("return_id", type=int)
    p.add_argument("--comment", default="")

    # ── Chats ──────────────────────────────────────────────────────

    p = sub.add_parser("chats", help="Список чатов")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("chat-history", help="История чата")
    p.add_argument("chat_id")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("chat-start", help="Начать чат")
    p.add_argument("posting_number")

    p = sub.add_parser("chat-send", help="Отправить сообщение")
    p.add_argument("chat_id")
    p.add_argument("message")

    # ── Promotions ─────────────────────────────────────────────────

    sub.add_parser("promos", help="Доступные акции")

    p = sub.add_parser("promo-candidates", help="Кандидаты в акцию")
    p.add_argument("action_id", type=int)

    p = sub.add_parser("promo-products", help="Товары в акции")
    p.add_argument("action_id", type=int)

    sub.add_parser("promo-hotsale", help="Hot Sale акции")

    # ── Strategies ─────────────────────────────────────────────────

    sub.add_parser("strategies", help="Ценовые стратегии")

    p = sub.add_parser("strategy-create", help="Создать стратегию")
    p.add_argument("type")
    p.add_argument("update_type")
    p.add_argument("--name", default="")

    p = sub.add_parser("strategy-delete", help="Удалить стратегию")
    p.add_argument("strategy_id", type=int)

    # ── Rating ─────────────────────────────────────────────────────

    sub.add_parser("rating", help="Рейтинг продавца")

    p = sub.add_parser("rating-history", help="История рейтинга")
    p.add_argument("date_from")
    p.add_argument("date_to")

    p = sub.add_parser("quality-rating", help="Рейтинг качества")
    p.add_argument("date_from")
    p.add_argument("date_to")

    # ── Reports ────────────────────────────────────────────────────

    p = sub.add_parser("report-create", help="Создать отчёт")
    p.add_argument("report_type")
    p.add_argument("--params-json", default="{}")

    p = sub.add_parser("report-info", help="Статус отчёта")
    p.add_argument("code")

    p = sub.add_parser("report-list", help="Список отчётов")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("report-download", help="Скачать отчёт")
    p.add_argument("code")
    p.add_argument("--output-path", default="")

    # ── Reviews ────────────────────────────────────────────────────

    p = sub.add_parser("reviews", help="Список отзывов")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("review-info", help="Детали отзыва")
    p.add_argument("review_id", type=int)

    p = sub.add_parser("review-comment", help="Ответить на отзыв")
    p.add_argument("review_id", type=int)
    p.add_argument("text")

    # ── Questions ──────────────────────────────────────────────────

    p = sub.add_parser("questions", help="Список вопросов")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("question-answer", help="Ответить на вопрос")
    p.add_argument("question_id", type=int)
    p.add_argument("answer")

    # ── Cancellations ──────────────────────────────────────────────

    p = sub.add_parser("cancellations", help="Заявки на отмену")
    p.add_argument("--filter-json", default="{}")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("cancellation-info", help="Детали заявки на отмену")
    p.add_argument("cancellation_id", type=int)

    p = sub.add_parser("cancellation-approve", help="Одобрить отмену")
    p.add_argument("cancellation_id", type=int)
    p.add_argument("--comment", default="")

    p = sub.add_parser("cancellation-reject", help="Отклонить отмену")
    p.add_argument("cancellation_id", type=int)
    p.add_argument("--comment", default="")

    # ── Certificates ───────────────────────────────────────────────

    p = sub.add_parser("certificates", help="Список сертификатов")
    p.add_argument("--filter-json", default="{}")

    p = sub.add_parser("certificate-info", help="Детали сертификата")
    p.add_argument("certificate_id", type=int)

    p = sub.add_parser("certificate-delete", help="Удалить сертификат")
    p.add_argument("certificate_id", type=int)

    # ── Barcodes ───────────────────────────────────────────────────

    p = sub.add_parser("barcode-generate", help="Сгенерировать штрихкоды")
    p.add_argument("product_ids")

    p = sub.add_parser("barcode-add", help="Привязать штрихкоды")
    p.add_argument("barcodes_json")

    # ── Brands ─────────────────────────────────────────────────────

    sub.add_parser("brands", help="Список брендов")

    # ── Parse & dispatch ───────────────────────────────────────────

    args = parser.parse_args(argv)

    if args.env:
        _load_env(args.env)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handlers = {
        # Legacy
        "list": lambda: server.ozon_unfulfilled_orders(days=args.days),
        "labels": lambda: server.ozon_labels_pdf(
            posting_numbers=",".join(args.posting) if args.posting else "all",
            days=args.days, output_dir=args.output_dir,
        ),
        "ship": lambda: server.ozon_ship_orders(
            posting_numbers=",".join(args.posting) if args.posting else "all",
            days=args.days,
        ),
        # Products
        "product-list": lambda: server.ozon_product_list(filter_json=args.filter_json, limit=args.limit),
        "product-info": lambda: server.ozon_product_info(offer_id=args.offer_id, product_id=args.product_id, sku=args.sku),
        "product-info-list": lambda: server.ozon_product_info_list(offer_ids=args.offer_ids, product_ids=args.product_ids, skus=args.skus),
        "product-import": lambda: server.ozon_product_import(args.items_json),
        "product-import-info": lambda: server.ozon_product_import_info(args.task_id),
        "product-update": lambda: server.ozon_product_update(args.items_json),
        "product-prices-update": lambda: server.ozon_product_prices_update(args.prices_json),
        "product-stocks-update": lambda: server.ozon_product_stocks_update(args.stocks_json),
        "product-stocks-info": lambda: server.ozon_product_stocks_info(filter_json=args.filter_json, limit=args.limit),
        "product-prices-info": lambda: server.ozon_product_prices_info(filter_json=args.filter_json, limit=args.limit),
        "product-description": lambda: server.ozon_product_description(offer_id=args.offer_id, product_id=args.product_id),
        "product-attributes": lambda: server.ozon_product_attributes(filter_json=args.filter_json, limit=args.limit),
        "product-archive": lambda: server.ozon_product_archive(args.product_ids),
        "product-unarchive": lambda: server.ozon_product_unarchive(args.product_ids),
        "product-delete": lambda: server.ozon_product_delete(args.product_ids),
        "product-rating": lambda: server.ozon_product_rating(args.skus),
        "product-related-sku": lambda: server.ozon_product_related_sku(args.items_json),
        # FBS
        "fbs-list": lambda: server.ozon_fbs_postings_list(filter_json=args.filter_json, limit=args.limit, offset=args.offset),
        "fbs-get": lambda: server.ozon_fbs_posting_get(args.posting_number),
        "fbs-ship": lambda: server.ozon_fbs_posting_ship(args.posting_number, args.items_json),
        "fbs-cancel": lambda: server.ozon_fbs_posting_cancel(args.posting_number, args.cancel_reason_id, args.message),
        "fbs-cancel-reasons": lambda: server.ozon_fbs_cancel_reasons(),
        "fbs-tracking": lambda: server.ozon_fbs_posting_tracking(args.posting_number, args.tracking_number),
        "fbs-label": lambda: server.ozon_fbs_posting_label(args.posting_number, output_dir=args.output_dir),
        "fbs-act-create": lambda: server.ozon_fbs_act_create(args.delivery_method_id, args.departure_date),
        "fbs-act-status": lambda: server.ozon_fbs_act_status(args.id),
        "fbs-act-pdf": lambda: server.ozon_fbs_act_pdf(args.id, output_path=args.output_path),
        "fbs-restrictions": lambda: server.ozon_fbs_restrictions(args.posting_number),
        "fbs-country-list": lambda: server.ozon_fbs_product_country_list(),
        # FBO
        "fbo-list": lambda: server.ozon_fbo_postings_list(filter_json=args.filter_json, limit=args.limit, offset=args.offset),
        "fbo-get": lambda: server.ozon_fbo_posting_get(args.posting_number),
        "fbo-supply-list": lambda: server.ozon_fbo_supply_list(filter_json=args.filter_json, page=args.page),
        "fbo-supply-get": lambda: server.ozon_fbo_supply_get(args.supply_order_id),
        "fbo-supply-cancel": lambda: server.ozon_fbo_supply_cancel(args.supply_order_id),
        "fbo-supply-items": lambda: server.ozon_fbo_supply_items(args.supply_order_id),
        # Categories
        "categories": lambda: server.ozon_category_tree(),
        "category-attributes": lambda: server.ozon_category_attributes(args.description_category_id),
        "category-values": lambda: server.ozon_category_attribute_values(args.attribute_id, args.description_category_id, limit=args.limit),
        "category-values-search": lambda: server.ozon_category_attribute_values_search(args.attribute_id, args.description_category_id, args.value),
        # Finance
        "finance-transactions": lambda: server.ozon_finance_transactions(args.filter_json, page=args.page, page_size=args.page_size),
        "finance-totals": lambda: server.ozon_finance_totals(args.filter_json),
        "finance-cash-flow": lambda: server.ozon_finance_cash_flow(args.filter_json),
        "finance-realization": lambda: server.ozon_finance_realization(args.date),
        # Analytics
        "analytics": lambda: server.ozon_analytics_data(args.date_from, args.date_to, args.metrics_json, args.dimensions_json),
        "analytics-stock": lambda: server.ozon_analytics_stock_on_warehouses(limit=args.limit),
        "analytics-turnover": lambda: server.ozon_analytics_item_turnover(args.date_from, args.date_to, skus=args.skus),
        # Warehouses
        "warehouses": lambda: server.ozon_warehouse_list(),
        "delivery-methods": lambda: server.ozon_warehouse_delivery_methods(filter_json=args.filter_json),
        # Returns
        "returns-fbo": lambda: server.ozon_returns_fbo(filter_json=args.filter_json, limit=args.limit),
        "returns-fbs": lambda: server.ozon_returns_fbs(filter_json=args.filter_json, limit=args.limit),
        "return-get": lambda: server.ozon_return_get(args.posting_number),
        "returns-rfbs": lambda: server.ozon_return_rfbs_list(filter_json=args.filter_json),
        "return-rfbs-get": lambda: server.ozon_return_rfbs_get(args.return_id),
        "return-rfbs-approve": lambda: server.ozon_return_rfbs_approve(args.return_id, comment=args.comment),
        "return-rfbs-reject": lambda: server.ozon_return_rfbs_reject(args.return_id, comment=args.comment),
        # Chats
        "chats": lambda: server.ozon_chat_list(page=args.page),
        "chat-history": lambda: server.ozon_chat_history(args.chat_id, limit=args.limit),
        "chat-start": lambda: server.ozon_chat_start(args.posting_number),
        "chat-send": lambda: server.ozon_chat_send_message(args.chat_id, args.message),
        # Promotions
        "promos": lambda: server.ozon_promo_available(),
        "promo-candidates": lambda: server.ozon_promo_candidates(args.action_id),
        "promo-products": lambda: server.ozon_promo_products(args.action_id),
        "promo-hotsale": lambda: server.ozon_promo_hotsale_list(),
        # Strategies
        "strategies": lambda: server.ozon_strategy_list(),
        "strategy-create": lambda: server.ozon_strategy_create(args.type, args.update_type, name=args.name),
        "strategy-delete": lambda: server.ozon_strategy_delete(args.strategy_id),
        # Rating
        "rating": lambda: server.ozon_rating_summary(),
        "rating-history": lambda: server.ozon_rating_history(args.date_from, args.date_to),
        "quality-rating": lambda: server.ozon_quality_rating(args.date_from, args.date_to),
        # Reports
        "report-create": lambda: server.ozon_report_create(args.report_type, params_json=args.params_json),
        "report-info": lambda: server.ozon_report_info(args.code),
        "report-list": lambda: server.ozon_report_list(page=args.page),
        "report-download": lambda: server.ozon_report_download(args.code, output_path=args.output_path),
        # Reviews
        "reviews": lambda: server.ozon_reviews_list(filter_json=args.filter_json, limit=args.limit),
        "review-info": lambda: server.ozon_review_info(args.review_id),
        "review-comment": lambda: server.ozon_review_comment(args.review_id, args.text),
        # Questions
        "questions": lambda: server.ozon_questions_list(filter_json=args.filter_json, limit=args.limit),
        "question-answer": lambda: server.ozon_question_answer(args.question_id, args.answer),
        # Cancellations
        "cancellations": lambda: server.ozon_cancellation_list(filter_json=args.filter_json, limit=args.limit),
        "cancellation-info": lambda: server.ozon_cancellation_info(args.cancellation_id),
        "cancellation-approve": lambda: server.ozon_cancellation_approve(args.cancellation_id, comment=args.comment),
        "cancellation-reject": lambda: server.ozon_cancellation_reject(args.cancellation_id, comment=args.comment),
        # Certificates
        "certificates": lambda: server.ozon_certificate_list(filter_json=args.filter_json),
        "certificate-info": lambda: server.ozon_certificate_info(args.certificate_id),
        "certificate-delete": lambda: server.ozon_certificate_delete(args.certificate_id),
        # Barcodes
        "barcode-generate": lambda: server.ozon_barcode_generate(args.product_ids),
        "barcode-add": lambda: server.ozon_barcode_add(args.barcodes_json),
        # Brands
        "brands": lambda: server.ozon_brand_list(),
    }

    print(handlers[args.command]())


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        log.error(str(err))
        sys.exit(1)
