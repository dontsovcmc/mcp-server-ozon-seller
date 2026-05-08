# Аналитика

3 действия в домене `analytics`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `analytics-data` | Аналитические данные (продажи, просмотры и т.д.) | `date_from` (string) *, `date_to` (string) *, `metrics` (list[str]) *, `dimensions` (list[str]) *, `filters` (list[dict]), `sort` (list[dict]), `limit` (int, 1000), `offset` (int, 0) |
| `analytics-stock` | Остатки на складах | `limit` (int, 100), `offset` (int, 0), `warehouse_type` (string, "") |
| `analytics-turnover` | Оборачиваемость товаров | `date_from` (string) *, `date_to` (string) *, `sku` (list[int]) |

\* — обязательный параметр
