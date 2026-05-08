# Финансы

4 действия в домене `finance`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `finance-transactions` | Список финансовых транзакций | `filter_dict` (dict) *, `page` (int, 1), `page_size` (int, 50) |
| `finance-totals` | Итоги по транзакциям | `filter_dict` (dict) * |
| `finance-cash-flow` | Движение денежных средств | `filter_dict` (dict) *, `page` (int, 1), `page_size` (int, 50) |
| `finance-realization` | Отчёт о реализации | `date` (string) * |

\* — обязательный параметр
