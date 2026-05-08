# Отзывы

4 действия в домене `reviews`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `reviews-list` | Список отзывов | `filter_dict` (dict), `sort_dir` (string, "DESC"), `limit` (int, 50), `offset` (int, 0) |
| `review-info` | Детали отзыва | `review_id` (int) * |
| `review-count` | Количество отзывов | `filter_dict` (dict) |
| `review-comment` | Ответить на отзыв | `review_id` (int) *, `text` (string) * |

\* — обязательный параметр
