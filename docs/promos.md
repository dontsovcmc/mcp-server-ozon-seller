# Акции

6 действий в домене `promos`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `promo-available` | Доступные акции | — |
| `promo-candidates` | Товары-кандидаты в акцию | `action_id` (int) *, `limit` (int, 100), `offset` (int, 0) |
| `promo-products` | Товары в акции | `action_id` (int) *, `limit` (int, 100), `offset` (int, 0) |
| `promo-products-add` | Добавить товары в акцию | `action_id` (int) *, `products` (list[dict]) * |
| `promo-products-remove` :warning: | Убрать товары из акции | `action_id` (int) *, `product_ids` (list[int]) * |
| `promo-hotsale-list` | Список Hot Sale акций | — |

\* — обязательный параметр

:warning: — деструктивное действие
