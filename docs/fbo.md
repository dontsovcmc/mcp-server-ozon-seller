# FBO-отправления

9 действий в домене `fbo`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `fbo-postings-list` | Список FBO-отправлений | `filter_dict` (dict), `dir` (string, "ASC"), `limit` (int, 50), `offset` (int, 0) |
| `fbo-posting-get` | Детали FBO-отправления | `posting_number` (string) * |
| `fbo-supply-create` | Создать заявку на поставку | `items` (list[dict]) *, `warehouse_id` (int) * |
| `fbo-supply-get` | Информация о поставке | `supply_order_id` (int) * |
| `fbo-supply-list` | Список поставок | `filter_dict` (dict), `page` (int, 1), `page_size` (int, 50) |
| `fbo-supply-cancel` :warning: | Отменить поставку | `supply_order_id` (int) * |
| `fbo-supply-items` | Товары в поставке | `supply_order_id` (int) * |
| `fbo-supply-shipments` | Отгрузки поставки | `supply_order_id` (int) * |
| `fbo-warehouse-workload` | Загруженность склада FBO | `warehouse_id` (int) * |

\* — обязательный параметр

:warning: — деструктивное действие
