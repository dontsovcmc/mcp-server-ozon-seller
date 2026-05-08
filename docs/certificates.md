# Сертификаты

6 действий в домене `certificates`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `certificate-list` | Список сертификатов | `filter_dict` (dict), `page` (int, 1), `page_size` (int, 50) |
| `certificate-info` | Детали сертификата | `certificate_id` (int) * |
| `certificate-create` | Добавить сертификат | `files` (list[dict]) *, `name` (string) *, `type_code` (string) *, + доп. поля |
| `certificate-delete` :warning: | Удалить сертификат | `certificate_id` (int) * |
| `certificate-bind` | Привязать сертификат к товарам | `certificate_id` (int) *, `product_id` (list[int]) * |
| `certificate-unbind` | Отвязать сертификат от товаров | `certificate_id` (int) *, `product_id` (list[int]) * |

\* — обязательный параметр

:warning: — деструктивное действие
