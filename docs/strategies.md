# Ценовые стратегии

4 действия в домене `strategies`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `strategy-list` | Список ценовых стратегий | — |
| `strategy-create` | Создать ценовую стратегию | `type` (string) *, `update_type` (string) *, `name` (string, ""), `competitors` (list[dict]) |
| `strategy-update` | Обновить ценовую стратегию | `strategy_id` (int) *, + доп. поля |
| `strategy-delete` :warning: | Удалить ценовую стратегию | `strategy_id` (int) * |

\* — обязательный параметр

:warning: — деструктивное действие
