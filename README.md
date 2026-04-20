# mcp-server-ozon-seller

MCP-сервер для управления FBS-отправлениями Ozon Seller API.

Позволяет просматривать несобранные заказы, скачивать PDF-этикетки и собирать отправления — через Claude (MCP) или из командной строки (CLI).

## Возможности

| MCP Tool | CLI команда | Описание |
|---|---|---|
| `ozon_unfulfilled_orders` | `list` | Список несобранных FBS-заказов |
| `ozon_labels_pdf` | `labels` | Скачать PDF-этикетки (штрихкоды) |
| `ozon_ship_orders` | `ship` | Собрать заказы (awaiting_packaging -> awaiting_deliver) |

## Установка

### Из PyPI

```bash
pip install mcp-server-ozon-seller
```

### Из исходников

```bash
git clone https://github.com/dontsovcmc/mcp-server-ozon-seller.git
cd mcp-server-ozon-seller
pip install -e ".[test]"
```

## Настройка Claude Code

```bash
claude mcp add ozon-seller \
  -e OZON_CLIENT_ID=your_client_id \
  -e OZON_API_KEY=your_api_key \
  -- mcp-server-ozon-seller
```

Или вручную в `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "mcp-server-ozon-seller",
      "env": {
        "OZON_CLIENT_ID": "your_client_id",
        "OZON_API_KEY": "your_api_key"
      }
    }
  }
}
```

## CLI

Вторая точка входа — команда `ozon-seller-cli` для использования как обычного скрипта.

### Переменные окружения

```bash
export OZON_CLIENT_ID=your_client_id
export OZON_API_KEY=your_api_key
```

Или через файл:

```bash
ozon-seller-cli --env .env COMMAND
```

### Список несобранных заказов

```bash
ozon-seller-cli list
ozon-seller-cli list --days 14
ozon-seller-cli list --json
```

Пример вывода:

```
Номер отправления          Товары                                   Кол-во  Дата отгрузки
──────────────────────────────────────────────────────────────────────────────────────────
89765432-0001-1            Ватериус WiFi                                 1  2026-04-21
89765432-0002-1            Ватериус WiFi, Адаптер 1/2                    3  2026-04-21
──────────────────────────────────────────────────────────────────────────────────────────
Итого: 2 отправлений
```

### Скачать этикетки

```bash
# Все несобранные
ozon-seller-cli labels

# Конкретные отправления
ozon-seller-cli labels --posting 89765432-0001-1 89765432-0002-1

# В указанную папку
ozon-seller-cli labels --output-dir /tmp/labels
```

### Собрать заказы

```bash
# Все несобранные
ozon-seller-cli ship --all

# Конкретные отправления
ozon-seller-cli ship --posting 89765432-0001-1 89765432-0002-1
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `OZON_CLIENT_ID` | Client-Id из личного кабинета Ozon Seller |
| `OZON_API_KEY` | Api-Key из личного кабинета Ozon Seller |

Получить ключи: Ozon Seller -> Настройки -> API-ключи.

## Лицензия

MIT
