# Чаты

6 действий в домене `chats`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `chat-list` | Список чатов | `chat_id_list` (list[str]), `page` (int, 1), `page_size` (int, 30) |
| `chat-history` | История сообщений чата | `chat_id` (string) *, `from_message_id` (string, ""), `limit` (int, 50), `direction` (string, "Forward") |
| `chat-start` | Начать чат по отправлению | `posting_number` (string) * |
| `chat-send-message` | Отправить сообщение в чат | `chat_id` (string) *, `message` (string) * |
| `chat-send-file` | Отправить файл в чат | `chat_id` (string) *, `base64_content` (string) *, `name` (string, "file") |
| `chat-read` | Пометить чат прочитанным | `chat_id` (string) *, `from_message_id` (string) * |

\* — обязательный параметр
