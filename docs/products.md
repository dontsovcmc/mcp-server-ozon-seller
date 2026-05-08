# Товары

21 действие в домене `products`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `product-import` | Импортировать/создать товары | `items` (list[dict]) * |
| `product-import-info` | Статус импорта товаров | `task_id` (int) * |
| `product-info` | Информация о товаре | `offer_id` (string, ""), `product_id` (int, 0), `sku` (int, 0) |
| `product-info-list` | Информация о нескольких товарах | `offer_id` (list[str]), `product_id` (list[int]), `sku` (list[int]) |
| `product-list` | Список товаров с фильтрами | `filter_dict` (dict), `last_id` (string, ""), `limit` (int, 100) |
| `product-update` | Обновить поля товаров | `items` (list[dict]) * |
| `product-prices-update` | Обновить цены товаров | `prices` (list[dict]) * |
| `product-stocks-update` | Обновить остатки FBS | `stocks` (list[dict]) * |
| `product-stocks-info` | Информация об остатках | `filter_dict` (dict), `last_id` (string, ""), `limit` (int, 100) |
| `product-prices-info` | Информация о ценах | `filter_dict` (dict), `last_id` (string, ""), `limit` (int, 100) |
| `product-description` | Описание товара | `offer_id` (string, ""), `product_id` (int, 0) |
| `product-attributes` | Атрибуты товаров | `filter_dict` (dict), `last_id` (string, ""), `limit` (int, 100), `sort_dir` (string, "ASC") |
| `product-archive` :warning: | Архивировать товары | `product_id` (list[int]) * |
| `product-unarchive` | Разархивировать товары | `product_id` (list[int]) * |
| `product-delete` :warning: | Удалить товары | `product_id` (list[int]) * |
| `product-pictures-import` | Импортировать изображения товаров | `images` (list[dict]) * |
| `product-pictures-info` | Статус загрузки изображений | `product_id` (list[int]) * |
| `product-geo-restrictions` | Гео-ограничения товаров | `filter_dict` (dict), `last_id` (string, ""), `limit` (int, 100) |
| `product-rating` | Контент-рейтинг по SKU | `skus` (list[int]) * |
| `product-related-sku` | Связанные SKU (FBO/FBS) | `items` (list[dict]) * |
| `product-digital-codes` | Загрузить цифровые коды активации | `digital_codes` (list[str]) *, `product_id` (int) * |

\* — обязательный параметр

:warning: — деструктивное действие
