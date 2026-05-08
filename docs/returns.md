# Возвраты

8 действий в домене `returns`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `returns-fbo` | Возвраты FBO | `filter_dict` (dict), `last_id` (int, 0), `limit` (int, 50) |
| `returns-fbs` | Возвраты FBS | `filter_dict` (dict), `last_id` (int, 0), `limit` (int, 50) |
| `return-get` | Детали возврата | `posting_number` (string) * |
| `return-rfbs-list` | Список возвратов rFBS | `filter_dict` (dict), `last_id` (int, 0), `limit` (int, 50) |
| `return-rfbs-get` | Детали возврата rFBS | `return_id` (int) * |
| `return-rfbs-approve` | Одобрить возврат rFBS | `return_id` (int) *, `comment` (string, "") |
| `return-rfbs-reject` :warning: | Отклонить возврат rFBS | `return_id` (int) *, `comment` (string, ""), `reject_reason_id` (int, 0) |
| `return-rfbs-compensate` | Компенсация возврата rFBS | `return_id` (int) *, `compensation_amount` (float) * |

\* — обязательный параметр

:warning: — деструктивное действие
