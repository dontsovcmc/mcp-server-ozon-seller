# Заявки на отмену

4 действия в домене `cancellations`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `cancellation-list` | Список заявок на отмену | `filter_dict` (dict), `limit` (int, 50), `offset` (int, 0) |
| `cancellation-info` | Детали заявки на отмену | `cancellation_id` (int) * |
| `cancellation-approve` | Одобрить заявку на отмену | `cancellation_id` (int) *, `comment` (string, "") |
| `cancellation-reject` | Отклонить заявку на отмену | `cancellation_id` (int) *, `comment` (string, "") |

\* — обязательный параметр
