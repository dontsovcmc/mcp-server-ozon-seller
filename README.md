<!-- mcp-name: io.github.dontsovcmc/ozon-seller -->

# mcp-server-ozon-seller

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/dontsovcmc/mcp-server-ozon-seller)

MCP-сервер для Ozon Seller API. Полное покрытие API: товары, заказы FBS/FBO, финансы, аналитика, возвраты, чаты, акции, отзывы и многое другое.

## Возможности

### Товары (Products)
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_product_list` | `product-list` | Список товаров |
| `ozon_product_info` | `product-info` | Информация о товаре |
| `ozon_product_info_list` | `product-info-list` | Информация о нескольких товарах |
| `ozon_product_import` | `product-import` | Импорт/создание товаров |
| `ozon_product_import_info` | `product-import-info` | Статус импорта |
| `ozon_product_update` | `product-update` | Обновить товары |
| `ozon_product_prices_update` | `product-prices-update` | Обновить цены |
| `ozon_product_stocks_update` | `product-stocks-update` | Обновить остатки FBS |
| `ozon_product_stocks_info` | `product-stocks-info` | Информация об остатках |
| `ozon_product_prices_info` | `product-prices-info` | Информация о ценах |
| `ozon_product_description` | `product-description` | Описание товара |
| `ozon_product_attributes` | `product-attributes` | Атрибуты товаров |
| `ozon_product_archive` | `product-archive` | Архивировать товары |
| `ozon_product_unarchive` | `product-unarchive` | Разархивировать товары |
| `ozon_product_delete` | `product-delete` | Удалить товары |
| `ozon_product_pictures_import` | — | Импорт изображений |
| `ozon_product_pictures_info` | — | Статус загрузки изображений |
| `ozon_product_geo_restrictions` | — | Гео-ограничения |
| `ozon_product_rating` | `product-rating` | Контент-рейтинг по SKU |
| `ozon_product_related_sku` | `product-related-sku` | Связанные SKU (FBO/FBS) |
| `ozon_product_upload_digital_codes` | — | Загрузить коды активации |

### FBS-отправления
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_unfulfilled_orders` | `list` | Несобранные FBS-заказы |
| `ozon_labels_pdf` | `labels` | Скачать PDF-этикетки |
| `ozon_ship_orders` | `ship` | Собрать заказы |
| `ozon_fbs_postings_list` | `fbs-list` | Список FBS-отправлений с фильтрами |
| `ozon_fbs_posting_get` | `fbs-get` | Детали отправления |
| `ozon_fbs_posting_ship` | `fbs-ship` | Собрать конкретное отправление |
| `ozon_fbs_posting_cancel` | `fbs-cancel` | Отменить отправление |
| `ozon_fbs_cancel_reasons` | `fbs-cancel-reasons` | Причины отмены |
| `ozon_fbs_posting_tracking` | `fbs-tracking` | Установить трек-номер |
| `ozon_fbs_posting_label` | `fbs-label` | Скачать этикетку |
| `ozon_fbs_act_create` | `fbs-act-create` | Создать акт |
| `ozon_fbs_act_status` | `fbs-act-status` | Статус акта |
| `ozon_fbs_act_pdf` | `fbs-act-pdf` | Скачать PDF акта |
| `ozon_fbs_digital_act_pdf` | — | Электронный акт |
| `ozon_fbs_container_labels` | — | Этикетки контейнера |
| `ozon_fbs_posting_delivered` | — | Подтвердить доставку (rFBS) |
| `ozon_fbs_posting_last_mile` | — | Отгрузить последняя миля |
| `ozon_fbs_timeslot_restrictions` | — | Ограничения таймслота |
| `ozon_fbs_restrictions` | `fbs-restrictions` | Ограничения отправления |
| `ozon_fbs_product_country_set` | — | Установить страну |
| `ozon_fbs_product_country_list` | `fbs-country-list` | Список стран |

### FBO
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_fbo_postings_list` | `fbo-list` | Список FBO-отправлений |
| `ozon_fbo_posting_get` | `fbo-get` | Детали FBO-отправления |
| `ozon_fbo_supply_create` | — | Создать поставку |
| `ozon_fbo_supply_get` | `fbo-supply-get` | Детали поставки |
| `ozon_fbo_supply_list` | `fbo-supply-list` | Список поставок |
| `ozon_fbo_supply_cancel` | `fbo-supply-cancel` | Отменить поставку |
| `ozon_fbo_supply_items` | `fbo-supply-items` | Товары поставки |
| `ozon_fbo_supply_shipments` | — | Отгрузки поставки |
| `ozon_fbo_warehouse_workload` | — | Загруженность склада |

### Категории
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_category_tree` | `categories` | Дерево категорий |
| `ozon_category_attributes` | `category-attributes` | Атрибуты категории |
| `ozon_category_attribute_values` | `category-values` | Значения словаря |
| `ozon_category_attribute_values_search` | `category-values-search` | Поиск по словарю |

### Финансы
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_finance_transactions` | `finance-transactions` | Финансовые транзакции |
| `ozon_finance_totals` | `finance-totals` | Итоги по транзакциям |
| `ozon_finance_cash_flow` | `finance-cash-flow` | Движение денежных средств |
| `ozon_finance_realization` | `finance-realization` | Отчёт о реализации |

### Аналитика
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_analytics_data` | `analytics` | Аналитические данные |
| `ozon_analytics_stock_on_warehouses` | `analytics-stock` | Остатки на складах |
| `ozon_analytics_item_turnover` | `analytics-turnover` | Оборачиваемость |

### Склады
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_warehouse_list` | `warehouses` | Склады продавца |
| `ozon_warehouse_delivery_methods` | `delivery-methods` | Способы доставки |

### Возвраты
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_returns_fbo` | `returns-fbo` | Возвраты FBO |
| `ozon_returns_fbs` | `returns-fbs` | Возвраты FBS |
| `ozon_return_get` | `return-get` | Детали возврата |
| `ozon_return_rfbs_list` | `returns-rfbs` | Возвраты rFBS |
| `ozon_return_rfbs_get` | `return-rfbs-get` | Детали возврата rFBS |
| `ozon_return_rfbs_approve` | `return-rfbs-approve` | Одобрить возврат |
| `ozon_return_rfbs_reject` | `return-rfbs-reject` | Отклонить возврат |
| `ozon_return_rfbs_compensate` | — | Компенсация возврата |

### Чаты
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_chat_list` | `chats` | Список чатов |
| `ozon_chat_history` | `chat-history` | История чата |
| `ozon_chat_start` | `chat-start` | Начать чат |
| `ozon_chat_send_message` | `chat-send` | Отправить сообщение |
| `ozon_chat_send_file` | — | Отправить файл |
| `ozon_chat_read` | — | Отметить прочитанным |

### Акции и стратегии
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_promo_available` | `promos` | Доступные акции |
| `ozon_promo_candidates` | `promo-candidates` | Кандидаты в акцию |
| `ozon_promo_products` | `promo-products` | Товары в акции |
| `ozon_promo_products_add` | — | Добавить товары в акцию |
| `ozon_promo_products_remove` | — | Убрать товары из акции |
| `ozon_promo_hotsale_list` | `promo-hotsale` | Hot Sale акции |
| `ozon_strategy_list` | `strategies` | Ценовые стратегии |
| `ozon_strategy_create` | `strategy-create` | Создать стратегию |
| `ozon_strategy_update` | — | Обновить стратегию |
| `ozon_strategy_delete` | `strategy-delete` | Удалить стратегию |

### Рейтинг и качество
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_rating_summary` | `rating` | Рейтинг продавца |
| `ozon_rating_history` | `rating-history` | История рейтинга |
| `ozon_quality_rating` | `quality-rating` | Рейтинг качества |

### Отчёты
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_report_create` | `report-create` | Создать отчёт |
| `ozon_report_info` | `report-info` | Статус отчёта |
| `ozon_report_list` | `report-list` | Список отчётов |
| `ozon_report_download` | `report-download` | Скачать отчёт |

### Отзывы
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_reviews_list` | `reviews` | Список отзывов |
| `ozon_review_info` | `review-info` | Детали отзыва |
| `ozon_review_count` | — | Количество отзывов |
| `ozon_review_comment` | `review-comment` | Ответить на отзыв |

### Вопросы
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_questions_list` | `questions` | Список вопросов |
| `ozon_question_answer` | `question-answer` | Ответить на вопрос |
| `ozon_question_update` | — | Обновить ответ |

### Отмены
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_cancellation_list` | `cancellations` | Заявки на отмену |
| `ozon_cancellation_info` | `cancellation-info` | Детали заявки |
| `ozon_cancellation_approve` | `cancellation-approve` | Одобрить отмену |
| `ozon_cancellation_reject` | `cancellation-reject` | Отклонить отмену |

### Сертификаты
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_certificate_list` | `certificates` | Список сертификатов |
| `ozon_certificate_info` | `certificate-info` | Детали сертификата |
| `ozon_certificate_create` | — | Добавить сертификат |
| `ozon_certificate_delete` | `certificate-delete` | Удалить сертификат |
| `ozon_certificate_bind` | — | Привязать к товарам |
| `ozon_certificate_unbind` | — | Отвязать от товаров |

### Штрихкоды
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_barcode_generate` | `barcode-generate` | Сгенерировать штрихкоды |
| `ozon_barcode_add` | `barcode-add` | Привязать штрихкод |

### Бренды
| MCP Tool | CLI | Описание |
|---|---|---|
| `ozon_brand_list` | `brands` | Список брендов |

## Установка

### Из PyPI

```bash
pip install mcp-server-ozon-seller
```

### Из исходников

```bash
git clone https://github.com/dontsovcmc/mcp-server-ozon-seller.git
cd mcp-server-ozon-seller
pip install -e ".[test]"
```

## Настройка Claude Code

```bash
claude mcp add ozon-seller \
  -e OZON_CLIENT_ID=your_client_id \
  -e OZON_API_KEY=your_api_key \
  -- mcp-server-ozon-seller
```

Или вручную в `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "mcp-server-ozon-seller",
      "env": {
        "OZON_CLIENT_ID": "your_client_id",
        "OZON_API_KEY": "your_api_key"
      }
    }
  }
}
```

## CLI

Вторая точка входа — команда `ozon-seller-cli`.

### Переменные окружения

```bash
export OZON_CLIENT_ID=your_client_id
export OZON_API_KEY=your_api_key
```

Или через файл:

```bash
ozon-seller-cli --env .env COMMAND
```

### Примеры

```bash
# Товары
ozon-seller-cli product-list --limit 10
ozon-seller-cli product-info --offer-id SKU-001
ozon-seller-cli product-stocks-info

# FBS-отправления
ozon-seller-cli list                    # несобранные заказы
ozon-seller-cli labels                  # скачать этикетки
ozon-seller-cli ship --all              # собрать все
ozon-seller-cli fbs-list                # с фильтрами
ozon-seller-cli fbs-cancel-reasons      # причины отмены

# FBO
ozon-seller-cli fbo-list
ozon-seller-cli fbo-supply-list

# Финансы и аналитика
ozon-seller-cli finance-transactions '{"date": {"from": "2026-04-01", "to": "2026-04-25"}}'
ozon-seller-cli analytics-stock

# Возвраты
ozon-seller-cli returns-fbs
ozon-seller-cli returns-fbo

# Другое
ozon-seller-cli warehouses
ozon-seller-cli categories
ozon-seller-cli rating
ozon-seller-cli reviews
ozon-seller-cli brands
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `OZON_CLIENT_ID` | Client-Id из личного кабинета Ozon Seller |
| `OZON_API_KEY` | Api-Key из личного кабинета Ozon Seller |

Получить ключи: Ozon Seller -> Настройки -> API-ключи.

## Лицензия

MIT
