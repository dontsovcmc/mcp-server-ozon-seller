"""HTTP-клиент Ozon Seller API (https://docs.ozon.ru/api/seller/)."""

import time
import logging
from datetime import datetime, timedelta, timezone

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://api-seller.ozon.ru"


class OzonSellerAPI:
    """Синхронный клиент Ozon Seller API для работы с FBS-отправлениями."""

    def __init__(self, client_id: str, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Client-Id": client_id,
            "Api-Key": api_key,
            "Content-Type": "application/json",
        })

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

    # --- FBS-отправления ---

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

        for _ in range(100):  # защита от бесконечного цикла
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
        """Детали одного FBS-отправления.

        :param posting_number: номер отправления.
        :return: posting dict.
        """
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
        """Скачивает PDF-этикетку для одного отправления.

        :param posting_number: номер отправления.
        :param retries: количество попыток.
        :return: PDF в байтах.
        """
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
        """Собирает отправление (awaiting_packaging -> awaiting_deliver).

        :param posting_number: номер отправления.
        :param items: список [{sku: int, quantity: int}].
        :return: ответ API.
        """
        body = {
            "posting_number": posting_number,
            "packages": [{"items": items}],
        }
        return self._post("/v2/posting/fbs/ship", body)
