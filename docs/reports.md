# Отчёты

4 действия в домене `reports`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `report-create` | Создать отчёт | `report_type` (string) *, `params` (dict) |
| `report-info` | Статус отчёта | `code` (string) * |
| `report-list` | Список отчётов | `page` (int, 1), `page_size` (int, 50), `report_type` (string, "") |
| `report-download` :floppy_disk: | Скачать файл отчёта | `code` (string) * |

\* — обязательный параметр

:floppy_disk: — скачивание файла
