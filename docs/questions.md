# Вопросы

3 действия в домене `questions`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `questions-list` | Список вопросов | `filter_dict` (dict), `sort_dir` (string, "DESC"), `limit` (int, 50), `offset` (int, 0) |
| `question-answer` | Ответить на вопрос | `question_id` (int) *, `answer` (string) * |
| `question-update` | Обновить ответ на вопрос | `question_id` (int) *, `answer` (string) * |

\* — обязательный параметр
