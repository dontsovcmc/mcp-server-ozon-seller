"""HTTP-клиент Ozon Seller API (https://docs.ozon.ru/api/seller/)."""

import time
import logging
from datetime import datetime, timedelta, timezone

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://api-seller.ozon.ru"


class OzonSellerAPI:
    """Синхронный клиент Ozon Seller API."""

    def __init__(self, client_id: str, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Client-Id": client_id,
            "Api-Key": api_key,
            "Content-Type": "application/json",
        })

    # ── Base HTTP ──────────────────────────────────────────────────

    def _post(self, path: str, payload: dict, **kwargs) -> dict:
        resp = self.session.post(f"{BASE_URL}{path}", json=payload, timeout=30, **kwargs)
        if not resp.ok:
            raise RuntimeError(f"POST {path} -> {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    def _post_binary(self, path: str, payload: dict, **kwargs) -> bytes:
        resp = self.session.post(f"{BASE_URL}{path}", json=payload, timeout=30, **kwargs)
        if not resp.ok:
            raise RuntimeError(f"POST {path} -> {resp.status_code}: {resp.text[:500]}")
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("application/pdf"):
            raise RuntimeError(f"POST {path} -> ожидался PDF, получен {content_type}: {resp.text[:300]}")
        return resp.content

    def _get(self, path: str, **kwargs) -> bytes:
        """GET-запрос, возвращает байты (для скачивания файлов)."""
        resp = self.session.get(f"{BASE_URL}{path}", timeout=30, **kwargs)
        if not resp.ok:
            raise RuntimeError(f"GET {path} -> {resp.status_code}: {resp.text[:500]}")
        return resp.content

    # ── Products ───────────────────────────────────────────────────

    def product_import(self, items: list[dict]) -> dict:
        """Импортировать/создать товары."""
        return self._post("/v3/product/import", {"items": items})

    def product_import_info(self, task_id: int) -> dict:
        """Статус импорта товаров."""
        return self._post("/v1/product/import/info", {"task_id": task_id})

    def product_info(self, offer_id: str = "", product_id: int = 0, sku: int = 0) -> dict:
        """Информация о товаре."""
        body: dict = {}
        if offer_id:
            body["offer_id"] = offer_id
        if product_id:
            body["product_id"] = product_id
        if sku:
            body["sku"] = sku
        return self._post("/v2/product/info", body)

    def product_info_list(self, offer_id: list[str] | None = None,
                          product_id: list[int] | None = None,
                          sku: list[int] | None = None) -> dict:
        """Информация о нескольких товарах."""
        body: dict = {}
        if offer_id:
            body["offer_id"] = offer_id
        if product_id:
            body["product_id"] = product_id
        if sku:
            body["sku"] = sku
        return self._post("/v2/product/info/list", body)

    def product_list(self, filter_dict: dict | None = None,
                     last_id: str = "", limit: int = 100) -> dict:
        """Список товаров с фильтрами."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v2/product/list", body)

    def product_update(self, items: list[dict]) -> dict:
        """Обновить поля товаров."""
        return self._post("/v2/product/update", {"items": items})

    def product_prices_update(self, prices: list[dict]) -> dict:
        """Обновить цены товаров."""
        return self._post("/v1/product/import/prices", {"prices": prices})

    def product_stocks_update(self, stocks: list[dict]) -> dict:
        """Обновить остатки FBS."""
        return self._post("/v2/products/stocks", {"stocks": stocks})

    def product_stocks_info(self, filter_dict: dict | None = None,
                            last_id: str = "", limit: int = 100) -> dict:
        """Информация об остатках."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v3/product/info/stocks", body)

    def product_prices_info(self, filter_dict: dict | None = None,
                            last_id: str = "", limit: int = 100) -> dict:
        """Информация о ценах."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v4/product/info/prices", body)

    def product_description(self, offer_id: str = "", product_id: int = 0) -> dict:
        """Описание товара."""
        body: dict = {}
        if offer_id:
            body["offer_id"] = offer_id
        if product_id:
            body["product_id"] = product_id
        return self._post("/v1/product/info/description", body)

    def product_attributes(self, filter_dict: dict | None = None,
                           last_id: str = "", limit: int = 100, sort_dir: str = "ASC") -> dict:
        """Атрибуты товаров."""
        body: dict = {"limit": limit, "sort_dir": sort_dir}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v3/products/info/attributes", body)

    def product_archive(self, product_id: list[int]) -> dict:
        """Архивировать товары."""
        return self._post("/v1/product/archive", {"product_id": product_id})

    def product_unarchive(self, product_id: list[int]) -> dict:
        """Разархивировать товары."""
        return self._post("/v1/product/unarchive", {"product_id": product_id})

    def product_delete(self, product_id: list[int]) -> dict:
        """Удалить товары."""
        return self._post("/v2/products/delete", {"products": [{"product_id": p} for p in product_id]})

    def product_pictures_import(self, images: list[dict]) -> dict:
        """Импортировать изображения товаров."""
        return self._post("/v1/product/pictures/import", {"images": images})

    def product_pictures_info(self, product_id: list[int]) -> dict:
        """Статус загрузки изображений."""
        return self._post("/v1/product/pictures/info", {"product_id": product_id})

    def product_geo_restrictions(self, filter_dict: dict | None = None,
                                 last_id: str = "", limit: int = 100) -> dict:
        """Гео-ограничения товаров."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/products/geo-restrictions-catalog-by-filter", body)

    def product_rating(self, skus: list[int]) -> dict:
        """Контент-рейтинг по SKU."""
        return self._post("/v1/product/rating-by-sku", {"skus": skus})

    def product_related_sku(self, items: list[dict]) -> dict:
        """Связанные SKU (FBO/FBS)."""
        return self._post("/v1/product/related-sku/get", {"items": items})

    def product_upload_digital_codes(self, digital_codes: list[str], product_id: int) -> dict:
        """Загрузить цифровые коды активации."""
        return self._post("/v1/product/upload_digital_codes", {
            "digital_codes": digital_codes, "product_id": product_id,
        })

    # ── FBS-отправления ────────────────────────────────────────────

    def get_unfulfilled_orders(self, days: int = 7) -> list[dict]:
        """Список FBS-отправлений со статусом awaiting_packaging.

        :param days: за сколько дней назад искать.
        :return: список posting dict'ов.
        """
        now = datetime.now(timezone.utc)
        date_from = (now - timedelta(days=days)).isoformat()
        date_to = now.isoformat()

        all_postings: list[dict] = []
        offset = 0
        limit = 50

        for _ in range(100):
            body = {
                "dir": "ASC",
                "filter": {
                    "since": date_from,
                    "to": date_to,
                    "status": "awaiting_packaging",
                },
                "limit": limit,
                "offset": offset,
                "with": {
                    "analytics_data": False,
                    "financial_data": False,
                },
            }
            data = self._post("/v3/posting/fbs/list", body)
            postings = data.get("result", {}).get("postings", [])
            if not postings:
                break

            all_postings.extend(postings)

            if len(postings) < limit:
                break
            offset += limit

        return all_postings

    def get_posting(self, posting_number: str) -> dict:
        """Детали одного FBS-отправления."""
        body = {
            "posting_number": posting_number,
            "with": {
                "analytics_data": False,
                "barcodes": True,
                "financial_data": False,
                "translit": False,
            },
        }
        data = self._post("/v3/posting/fbs/get", body)
        return data.get("result", {})

    def get_label_pdf(self, posting_number: str, retries: int = 3) -> bytes:
        """Скачивает PDF-этикетку для одного отправления."""
        body = {"posting_number": [posting_number]}

        for attempt in range(retries):
            try:
                return self._post_binary("/v2/posting/fbs/package-label", body)
            except RuntimeError as e:
                log.warning(f"{posting_number}: попытка {attempt + 1}/{retries} — {e}")
                if attempt < retries - 1:
                    time.sleep(2)

        raise RuntimeError(f"{posting_number}: не удалось скачать этикетку после {retries} попыток")

    def ship_posting(self, posting_number: str, items: list[dict]) -> dict:
        """Собирает отправление (awaiting_packaging -> awaiting_deliver)."""
        body = {
            "posting_number": posting_number,
            "packages": [{"items": items}],
        }
        return self._post("/v2/posting/fbs/ship", body)

    def fbs_postings_list(self, filter_dict: dict | None = None,
                          dir: str = "ASC", limit: int = 50, offset: int = 0,
                          with_dict: dict | None = None) -> dict:
        """Список FBS-отправлений с фильтрами."""
        body: dict = {"dir": dir, "limit": limit, "offset": offset}
        if filter_dict:
            body["filter"] = filter_dict
        body["with"] = with_dict or {"analytics_data": False, "financial_data": False}
        return self._post("/v3/posting/fbs/list", body)

    def fbs_posting_get(self, posting_number: str, with_dict: dict | None = None) -> dict:
        """Детали FBS-отправления."""
        body: dict = {"posting_number": posting_number}
        body["with"] = with_dict or {
            "analytics_data": False, "barcodes": True,
            "financial_data": False, "translit": False,
        }
        return self._post("/v3/posting/fbs/get", body)

    def fbs_posting_cancel(self, posting_number: str,
                           cancel_reason_id: int, cancel_reason_message: str = "") -> dict:
        """Отменить FBS-отправление."""
        body: dict = {
            "cancel_reason_id": cancel_reason_id,
            "cancel_reason_message": cancel_reason_message,
            "posting_number": posting_number,
        }
        return self._post("/v2/posting/fbs/cancel", body)

    def fbs_cancel_reasons(self) -> dict:
        """Список причин отмены FBS."""
        return self._post("/v1/posting/fbs/cancel-reason/list", {})

    def fbs_posting_tracking(self, posting_number: str, tracking_number: str) -> dict:
        """Установить трек-номер FBS."""
        return self._post("/v1/posting/fbs/set-tracking-number", {
            "posting_number": posting_number,
            "tracking_number": tracking_number,
        })

    def fbs_act_create(self, delivery_method_id: int, departure_date: str) -> dict:
        """Создать акт приёма-передачи."""
        return self._post("/v2/posting/fbs/act/create", {
            "delivery_method_id": delivery_method_id,
            "departure_date": departure_date,
        })

    def fbs_act_status(self, id: int) -> dict:
        """Статус формирования акта."""
        return self._post("/v2/posting/fbs/act/check-status", {"id": id})

    def fbs_act_pdf(self, id: int) -> bytes:
        """Скачать PDF акта."""
        resp = self.session.post(f"{BASE_URL}/v2/posting/fbs/act/get-pdf", json={"id": id}, timeout=30)
        if not resp.ok:
            raise RuntimeError(f"POST /v2/posting/fbs/act/get-pdf -> {resp.status_code}: {resp.text[:500]}")
        return resp.content

    def fbs_digital_act_pdf(self, id: int, doc_type: str = "act_of_acceptance") -> bytes:
        """Скачать PDF электронного акта."""
        resp = self.session.post(
            f"{BASE_URL}/v2/posting/fbs/digital/act/get-pdf",
            json={"id": id, "doc_type": doc_type}, timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(f"POST fbs/digital/act/get-pdf -> {resp.status_code}: {resp.text[:500]}")
        return resp.content

    def fbs_container_labels(self, id: int) -> bytes:
        """Этикетки для контейнера."""
        resp = self.session.post(
            f"{BASE_URL}/v2/posting/fbs/act/get-container-labels",
            json={"id": id}, timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(f"POST fbs/act/get-container-labels -> {resp.status_code}: {resp.text[:500]}")
        return resp.content

    def fbs_posting_delivered(self, posting_number: str) -> dict:
        """Подтвердить доставку (rFBS)."""
        return self._post("/v2/posting/fbs/deliver", {"posting_number": posting_number})

    def fbs_posting_last_mile(self, posting_number: str, items: list[dict]) -> dict:
        """Отгрузить последняя миля."""
        return self._post("/v2/posting/fbs/ship/last-mile", {
            "posting_number": posting_number,
            "packages": [{"items": items}],
        })

    def fbs_timeslot_restrictions(self, delivery_method_id: int) -> dict:
        """Ограничения на смену таймслота."""
        return self._post("/v1/posting/fbs/timeslot/change-restrictions", {
            "delivery_method_id": delivery_method_id,
        })

    def fbs_restrictions(self, posting_number: str) -> dict:
        """Ограничения отправления."""
        return self._post("/v1/posting/fbs/restrictions", {
            "posting_number": posting_number,
        })

    def fbs_product_country_set(self, posting_number: str, product_id: int, country_iso_code: str) -> dict:
        """Установить страну-производитель."""
        return self._post("/v1/posting/fbs/product/country/set", {
            "posting_number": posting_number,
            "product_id": product_id,
            "country_iso_code": country_iso_code,
        })

    def fbs_product_country_list(self) -> dict:
        """Список стран-производителей."""
        return self._post("/v1/posting/fbs/product/country/list", {})

    # ── FBO ────────────────────────────────────────────────────────

    def fbo_postings_list(self, filter_dict: dict | None = None,
                          dir: str = "ASC", limit: int = 50, offset: int = 0,
                          with_dict: dict | None = None) -> dict:
        """Список FBO-отправлений."""
        body: dict = {"dir": dir, "limit": limit, "offset": offset}
        if filter_dict:
            body["filter"] = filter_dict
        body["with"] = with_dict or {"analytics_data": False, "financial_data": False}
        return self._post("/v2/posting/fbo/list", body)

    def fbo_posting_get(self, posting_number: str, with_dict: dict | None = None) -> dict:
        """Детали FBO-отправления."""
        body: dict = {"posting_number": posting_number}
        body["with"] = with_dict or {"analytics_data": False, "financial_data": False}
        return self._post("/v2/posting/fbo/get", body)

    def fbo_supply_create(self, items: list[dict], warehouse_id: int) -> dict:
        """Создать заявку на поставку."""
        return self._post("/v1/supply-order/create", {
            "items": items, "warehouse_id": warehouse_id,
        })

    def fbo_supply_get(self, supply_order_id: int) -> dict:
        """Информация о поставке."""
        return self._post("/v1/supply-order/get", {"supply_order_id": supply_order_id})

    def fbo_supply_list(self, filter_dict: dict | None = None,
                        page: int = 1, page_size: int = 50) -> dict:
        """Список поставок."""
        body: dict = {"page": page, "page_size": page_size}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/supply-order/list", body)

    def fbo_supply_cancel(self, supply_order_id: int) -> dict:
        """Отменить поставку."""
        return self._post("/v1/supply-order/cancel", {"supply_order_id": supply_order_id})

    def fbo_supply_items(self, supply_order_id: int) -> dict:
        """Товары в поставке."""
        return self._post("/v1/supply-order/items", {"supply_order_id": supply_order_id})

    def fbo_supply_shipments(self, supply_order_id: int) -> dict:
        """Отгрузки поставки."""
        return self._post("/v1/supply-order/shipment/list", {"supply_order_id": supply_order_id})

    def fbo_warehouse_workload(self, warehouse_id: int) -> dict:
        """Загруженность склада FBO."""
        return self._post("/v1/fbo/warehouse/workload", {"warehouse_id": warehouse_id})

    # ── Categories ─────────────────────────────────────────────────

    def category_tree(self, language: str = "DEFAULT") -> dict:
        """Дерево категорий."""
        return self._post("/v1/description-category/tree", {"language": language})

    def category_attributes(self, description_category_id: int, language: str = "DEFAULT",
                            type_id: int = 0) -> dict:
        """Атрибуты категории."""
        body: dict = {"description_category_id": description_category_id, "language": language}
        if type_id:
            body["type_id"] = type_id
        return self._post("/v1/description-category/attribute", body)

    def category_attribute_values(self, attribute_id: int, description_category_id: int,
                                  last_value_id: int = 0, limit: int = 100,
                                  language: str = "DEFAULT") -> dict:
        """Значения словаря атрибута."""
        return self._post("/v1/description-category/attribute/values", {
            "attribute_id": attribute_id,
            "description_category_id": description_category_id,
            "language": language,
            "last_value_id": last_value_id,
            "limit": limit,
        })

    def category_attribute_values_search(self, attribute_id: int, description_category_id: int,
                                         value: str, limit: int = 100,
                                         language: str = "DEFAULT") -> dict:
        """Поиск по словарю атрибутов."""
        return self._post("/v1/description-category/attribute/values/search", {
            "attribute_id": attribute_id,
            "description_category_id": description_category_id,
            "language": language,
            "limit": limit,
            "value": value,
        })

    # ── Finance ────────────────────────────────────────────────────

    def finance_transactions(self, filter_dict: dict, page: int = 1, page_size: int = 50) -> dict:
        """Список финансовых транзакций."""
        return self._post("/v3/finance/transaction/list", {
            "filter": filter_dict, "page": page, "page_size": page_size,
        })

    def finance_totals(self, filter_dict: dict) -> dict:
        """Итоги по транзакциям."""
        return self._post("/v1/finance/transaction/totals", {"filter": filter_dict})

    def finance_cash_flow(self, filter_dict: dict, page: int = 1, page_size: int = 50) -> dict:
        """Движение денежных средств."""
        return self._post("/v1/finance/cash-flow-statement/list", {
            "filter": filter_dict, "page": page, "page_size": page_size,
        })

    def finance_realization(self, date: str) -> dict:
        """Отчёт о реализации."""
        return self._post("/v2/finance/realization", {"date": date})

    # ── Analytics ──────────────────────────────────────────────────

    def analytics_data(self, date_from: str, date_to: str,
                       metrics: list[str], dimensions: list[str],
                       filters: list[dict] | None = None,
                       sort: list[dict] | None = None,
                       limit: int = 1000, offset: int = 0) -> dict:
        """Аналитические данные (продажи, просмотры и т.д.)."""
        body: dict = {
            "date_from": date_from,
            "date_to": date_to,
            "metrics": metrics,
            "dimensions": dimensions,
            "limit": limit,
            "offset": offset,
        }
        if filters:
            body["filters"] = filters
        if sort:
            body["sort"] = sort
        return self._post("/v1/analytics/data", body)

    def analytics_stock_on_warehouses(self, limit: int = 100, offset: int = 0,
                                      warehouse_type: str = "") -> dict:
        """Остатки на складах."""
        body: dict = {"limit": limit, "offset": offset}
        if warehouse_type:
            body["warehouse_type"] = warehouse_type
        return self._post("/v2/analytics/stock_on_warehouses", body)

    def analytics_item_turnover(self, date_from: str, date_to: str,
                                sku: list[int] | None = None) -> dict:
        """Оборачиваемость товаров."""
        body: dict = {"date_from": date_from, "date_to": date_to}
        if sku:
            body["sku"] = sku
        return self._post("/v1/analytics/item_turnover", body)

    # ── Warehouses ─────────────────────────────────────────────────

    def warehouse_list(self) -> dict:
        """Список складов продавца."""
        return self._post("/v1/warehouse/list", {})

    def delivery_methods(self, filter_dict: dict | None = None,
                         limit: int = 50, offset: int = 0) -> dict:
        """Способы доставки."""
        body: dict = {"limit": limit, "offset": offset}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/delivery-method/list", body)

    # ── Returns ────────────────────────────────────────────────────

    def returns_fbo(self, filter_dict: dict | None = None,
                    last_id: int = 0, limit: int = 50) -> dict:
        """Возвраты FBO."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v3/returns/company/fbo", body)

    def returns_fbs(self, filter_dict: dict | None = None,
                    last_id: int = 0, limit: int = 50) -> dict:
        """Возвраты FBS."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v3/returns/company/fbs", body)

    def return_get(self, posting_number: str) -> dict:
        """Детали возврата."""
        return self._post("/v3/returns/company/get", {"posting_number": posting_number})

    def return_rfbs_list(self, filter_dict: dict | None = None,
                         last_id: int = 0, limit: int = 50) -> dict:
        """Список возвратов rFBS."""
        body: dict = {"limit": limit}
        if last_id:
            body["last_id"] = last_id
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/returns/list", body)

    def return_rfbs_get(self, return_id: int) -> dict:
        """Детали возврата rFBS."""
        return self._post("/v1/returns/get", {"return_id": return_id})

    def return_rfbs_approve(self, return_id: int, comment: str = "") -> dict:
        """Одобрить возврат rFBS."""
        body: dict = {"return_id": return_id}
        if comment:
            body["comment"] = comment
        return self._post("/v1/returns/approve", body)

    def return_rfbs_reject(self, return_id: int, comment: str = "",
                           reject_reason_id: int = 0) -> dict:
        """Отклонить возврат rFBS."""
        body: dict = {"return_id": return_id}
        if comment:
            body["comment"] = comment
        if reject_reason_id:
            body["reject_reason_id"] = reject_reason_id
        return self._post("/v1/returns/reject", body)

    def return_rfbs_compensate(self, return_id: int, compensation_amount: float) -> dict:
        """Компенсация возврата rFBS."""
        return self._post("/v1/returns/compensate", {
            "return_id": return_id,
            "compensation_amount": compensation_amount,
        })

    # ── Chats ──────────────────────────────────────────────────────

    def chat_list(self, chat_id_list: list[str] | None = None,
                  page: int = 1, page_size: int = 30) -> dict:
        """Список чатов."""
        body: dict = {"page": page, "page_size": page_size}
        if chat_id_list:
            body["chat_id_list"] = chat_id_list
        return self._post("/v2/chat/list", body)

    def chat_history(self, chat_id: str, from_message_id: str = "",
                     limit: int = 50, direction: str = "Forward") -> dict:
        """История сообщений чата."""
        body: dict = {"chat_id": chat_id, "limit": limit, "direction": direction}
        if from_message_id:
            body["from_message_id"] = from_message_id
        return self._post("/v2/chat/history", body)

    def chat_start(self, posting_number: str) -> dict:
        """Начать чат по отправлению."""
        return self._post("/v1/chat/start", {"posting_number": posting_number})

    def chat_send_message(self, chat_id: str, message: str) -> dict:
        """Отправить сообщение в чат."""
        return self._post("/v1/chat/send/message", {
            "chat_id": chat_id, "message": message,
        })

    def chat_send_file(self, chat_id: str, base64_content: str,
                       name: str = "file") -> dict:
        """Отправить файл в чат."""
        return self._post("/v1/chat/send/file", {
            "chat_id": chat_id,
            "base64_content": base64_content,
            "name": name,
        })

    def chat_read(self, chat_id: str, from_message_id: str) -> dict:
        """Пометить чат прочитанным."""
        return self._post("/v2/chat/mark-as-read", {
            "chat_id": chat_id, "from_message_id": from_message_id,
        })

    # ── Promotions & Strategies ────────────────────────────────────

    def promo_available(self) -> dict:
        """Доступные акции."""
        return self._post("/v1/actions", {})

    def promo_candidates(self, action_id: int, limit: int = 100, offset: int = 0) -> dict:
        """Товары-кандидаты в акцию."""
        return self._post("/v1/actions/candidates", {
            "action_id": action_id, "limit": limit, "offset": offset,
        })

    def promo_products(self, action_id: int, limit: int = 100, offset: int = 0) -> dict:
        """Товары в акции."""
        return self._post("/v1/actions/products", {
            "action_id": action_id, "limit": limit, "offset": offset,
        })

    def promo_products_add(self, action_id: int, products: list[dict]) -> dict:
        """Добавить товары в акцию."""
        return self._post("/v1/actions/products/activate", {
            "action_id": action_id, "products": products,
        })

    def promo_products_remove(self, action_id: int, product_ids: list[int]) -> dict:
        """Убрать товары из акции."""
        return self._post("/v1/actions/products/deactivate", {
            "action_id": action_id, "product_ids": product_ids,
        })

    def promo_hotsale_list(self) -> dict:
        """Список Hot Sale акций."""
        return self._post("/v1/actions/hotsales/list", {})

    def strategy_list(self) -> dict:
        """Список ценовых стратегий."""
        return self._post("/v1/pricing/strategy/list", {})

    def strategy_create(self, type: str, update_type: str,
                        name: str = "", competitors: list[dict] | None = None) -> dict:
        """Создать ценовую стратегию."""
        body: dict = {"type": type, "update_type": update_type}
        if name:
            body["name"] = name
        if competitors:
            body["competitors"] = competitors
        return self._post("/v1/pricing/strategy/create", body)

    def strategy_update(self, strategy_id: int, **kwargs) -> dict:
        """Обновить ценовую стратегию."""
        body: dict = {"strategy_id": strategy_id}
        body.update(kwargs)
        return self._post("/v1/pricing/strategy/update", body)

    def strategy_delete(self, strategy_id: int) -> dict:
        """Удалить ценовую стратегию."""
        return self._post("/v1/pricing/strategy/remove", {"strategy_id": strategy_id})

    # ── Rating & Quality ───────────────────────────────────────────

    def rating_summary(self) -> dict:
        """Сводка рейтинга продавца."""
        return self._post("/v1/rating/summary", {})

    def rating_history(self, date_from: str, date_to: str, ratings: list[str] | None = None) -> dict:
        """История рейтинга."""
        body: dict = {"date_from": date_from, "date_to": date_to}
        if ratings:
            body["ratings"] = ratings
        return self._post("/v1/rating/history", body)

    def quality_rating(self, date_from: str, date_to: str,
                       warehouse_id: int = 0) -> dict:
        """Рейтинг качества."""
        body: dict = {"date_from": date_from, "date_to": date_to}
        if warehouse_id:
            body["warehouse_id"] = warehouse_id
        return self._post("/v1/quality/rating", body)

    # ── Reports ────────────────────────────────────────────────────

    def report_create(self, report_type: str, params: dict | None = None) -> dict:
        """Создать отчёт."""
        body: dict = {"report_type": report_type}
        if params:
            body.update(params)
        return self._post("/v1/report/info/create", body)

    def report_info(self, code: str) -> dict:
        """Статус отчёта."""
        return self._post("/v1/report/info", {"code": code})

    def report_list(self, page: int = 1, page_size: int = 50,
                    report_type: str = "") -> dict:
        """Список отчётов."""
        body: dict = {"page": page, "page_size": page_size}
        if report_type:
            body["report_type"] = report_type
        return self._post("/v1/report/list", body)

    def report_download(self, code: str) -> bytes:
        """Скачать файл отчёта."""
        return self._get(f"/v1/report/download?code={code}")

    # ── Reviews ────────────────────────────────────────────────────

    def reviews_list(self, filter_dict: dict | None = None,
                     sort_dir: str = "DESC", limit: int = 50, offset: int = 0) -> dict:
        """Список отзывов."""
        body: dict = {"limit": limit, "offset": offset, "sort_dir": sort_dir}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/review/list", body)

    def review_info(self, review_id: int) -> dict:
        """Детали отзыва."""
        return self._post("/v1/review/info", {"review_id": review_id})

    def review_count(self, filter_dict: dict | None = None) -> dict:
        """Количество отзывов."""
        body: dict = {}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/review/count", body)

    def review_comment(self, review_id: int, text: str) -> dict:
        """Ответить на отзыв."""
        return self._post("/v1/review/comment/create", {
            "review_id": review_id, "text": text,
        })

    # ── Questions ──────────────────────────────────────────────────

    def questions_list(self, filter_dict: dict | None = None,
                       sort_dir: str = "DESC", limit: int = 50, offset: int = 0) -> dict:
        """Список вопросов."""
        body: dict = {"limit": limit, "offset": offset, "sort_dir": sort_dir}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/question/list", body)

    def question_answer(self, question_id: int, answer: str) -> dict:
        """Ответить на вопрос."""
        return self._post("/v1/question/answer", {
            "question_id": question_id, "answer": answer,
        })

    def question_update(self, question_id: int, answer: str) -> dict:
        """Обновить ответ на вопрос."""
        return self._post("/v1/question/update", {
            "question_id": question_id, "answer": answer,
        })

    # ── Cancellations ──────────────────────────────────────────────

    def cancellation_list(self, filter_dict: dict | None = None,
                          limit: int = 50, offset: int = 0) -> dict:
        """Список заявок на отмену."""
        body: dict = {"limit": limit, "offset": offset}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/conditional-cancellation/list", body)

    def cancellation_info(self, cancellation_id: int) -> dict:
        """Детали заявки на отмену."""
        return self._post("/v1/conditional-cancellation/get", {"cancellation_id": cancellation_id})

    def cancellation_approve(self, cancellation_id: int, comment: str = "") -> dict:
        """Одобрить заявку на отмену."""
        body: dict = {"cancellation_id": cancellation_id}
        if comment:
            body["comment"] = comment
        return self._post("/v1/conditional-cancellation/approve", body)

    def cancellation_reject(self, cancellation_id: int, comment: str = "") -> dict:
        """Отклонить заявку на отмену."""
        body: dict = {"cancellation_id": cancellation_id}
        if comment:
            body["comment"] = comment
        return self._post("/v1/conditional-cancellation/reject", body)

    # ── Certificates ───────────────────────────────────────────────

    def certificate_list(self, filter_dict: dict | None = None,
                         page: int = 1, page_size: int = 50) -> dict:
        """Список сертификатов."""
        body: dict = {"page": page, "page_size": page_size}
        if filter_dict:
            body["filter"] = filter_dict
        return self._post("/v1/product/certificate/list", body)

    def certificate_info(self, certificate_id: int) -> dict:
        """Детали сертификата."""
        return self._post("/v1/product/certificate/info", {"certificate_id": certificate_id})

    def certificate_create(self, files: list[dict], name: str,
                           type_code: str, **kwargs) -> dict:
        """Добавить сертификат."""
        body: dict = {"files": files, "name": name, "type_code": type_code}
        body.update(kwargs)
        return self._post("/v1/product/certificate/create", body)

    def certificate_delete(self, certificate_id: int) -> dict:
        """Удалить сертификат."""
        return self._post("/v1/product/certificate/delete", {"certificate_id": certificate_id})

    def certificate_bind(self, certificate_id: int, product_id: list[int]) -> dict:
        """Привязать сертификат к товарам."""
        return self._post("/v1/product/certificate/bind", {
            "certificate_id": certificate_id, "product_id": product_id,
        })

    def certificate_unbind(self, certificate_id: int, product_id: list[int]) -> dict:
        """Отвязать сертификат от товаров."""
        return self._post("/v1/product/certificate/unbind", {
            "certificate_id": certificate_id, "product_id": product_id,
        })

    # ── Barcodes ───────────────────────────────────────────────────

    def barcode_generate(self, product_ids: list[int]) -> dict:
        """Сгенерировать штрихкоды."""
        return self._post("/v1/barcode/generate", {"product_ids": product_ids})

    def barcode_add(self, barcodes: list[dict]) -> dict:
        """Привязать штрихкод к товару."""
        return self._post("/v1/barcode/add", {"barcodes": barcodes})

    # ── Brands ─────────────────────────────────────────────────────

    def brand_list(self, page: int = 1, page_size: int = 100) -> dict:
        """Список брендов."""
        return self._post("/v1/brand/company-certification/list", {
            "page": page, "page_size": page_size,
        })
