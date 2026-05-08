# FBS-отправления

17 действий в домене `fbs`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `fbs-postings-list` | Список FBS-отправлений с фильтрами | `filter_dict` (dict), `dir` (string, "ASC"), `limit` (int, 50), `offset` (int, 0) |
| `fbs-posting-get` | Детали FBS-отправления | `posting_number` (string) * |
| `fbs-posting-cancel` :warning: | Отменить FBS-отправление | `posting_number` (string) *, `cancel_reason_id` (int) *, `cancel_reason_message` (string, "") |
| `fbs-cancel-reasons` | Список причин отмены FBS | — |
| `fbs-posting-tracking` | Установить трек-номер FBS | `posting_number` (string) *, `tracking_number` (string) * |
| `fbs-label-pdf` :floppy_disk: | Скачать PDF-этикетку отправления | `posting_number` (string) *, `retries` (int, 3) |
| `fbs-act-create` | Создать акт приёма-передачи | `delivery_method_id` (int) *, `departure_date` (string) * |
| `fbs-act-status` | Статус формирования акта | `id` (int) * |
| `fbs-act-pdf` :floppy_disk: | Скачать PDF акта | `id` (int) * |
| `fbs-digital-act-pdf` :floppy_disk: | Скачать PDF электронного акта | `id` (int) *, `doc_type` (string, "act_of_acceptance") |
| `fbs-container-labels` :floppy_disk: | Этикетки для контейнера | `id` (int) * |
| `fbs-posting-delivered` | Подтвердить доставку (rFBS) | `posting_number` (string) * |
| `fbs-posting-last-mile` | Отгрузить последняя миля | `posting_number` (string) *, `items` (list[dict]) * |
| `fbs-timeslot-restrictions` | Ограничения на смену таймслота | `delivery_method_id` (int) * |
| `fbs-restrictions` | Ограничения отправления | `posting_number` (string) * |
| `fbs-product-country-set` | Установить страну-производитель | `posting_number` (string) *, `product_id` (int) *, `country_iso_code` (string) * |
| `fbs-product-country-list` | Список стран-производителей | — |

\* — обязательный параметр

:warning: — деструктивное действие

:floppy_disk: — скачивание файла
