<!-- mcp-name: io.github.dontsovcmc/ozon-seller -->

# mcp-server-ozon-seller

[![Version](https://img.shields.io/badge/version-0.3.1-blue)](https://github.com/dontsovcmc/mcp-server-ozon-seller)

MCP-сервер, CLI-утилита и библиотека Pydantic-моделей для [Ozon Seller API](https://docs.ozon.ru/api/seller/).

- **MCP-сервер** — интеграция с Claude Code, Claude Desktop и другими MCP-клиентами
- **CLI-утилита** — работа с API из терминала, скрипты и автоматизация
- **Pydantic-модели** — типизированные модели API для использования в своих Python-программах

Все данные остаются на вашем компьютере — ключи API никуда не передаются.

## Оглавление

- [Архитектура](#архитектура)
- [Доступные действия](#доступные-действия-111)
- [MCP-сервер](#mcp-сервер)
  - [Установка](#установка)
  - [Подключение к Claude Code](#подключение-к-claude-code)
  - [Подключение к Claude Desktop](#подключение-к-claude-desktop)
  - [Подключение через --mcp-config](#подключение-через---mcp-config)
  - [Примеры](#примеры-mcp)
- [CLI-утилита](#cli-утилита)
  - [Установка](#установка-cli)
  - [Использование](#использование-cli)
  - [Примеры команд](#примеры-команд)
- [Pydantic-модели](#pydantic-модели)
  - [Установка](#установка-библиотеки)
  - [Использование в своих программах](#использование-в-своих-программах)
- [Переменные окружения](#переменные-окружения)
- [Разработка](#разработка)
- [Лицензия](#лицензия)

## Архитектура

Сервер использует паттерн **search + execute** — вместо 111 отдельных инструментов предоставляет 3:

| Инструмент | Описание |
|------------|----------|
| `ozon_search` | Поиск действий по описанию на естественном языке |
| `ozon_execute` | Выполнение действия по ID |
| `ozon_execute_file` | Выполнение действия со скачиванием файла |

### Как это работает

```
LLM: ozon_search("отменить отправление fbs")
→ [{"id": "fbs-posting-cancel", "params_schema": {"posting_number": "str", ...}, ...}]

LLM: ozon_execute("fbs-posting-cancel", '{"posting_number": "12345678-0001-1", "cancel_reason_id": 352}')
→ {"result": true}
```

## Доступные действия (111)

| Домен | Кол-во | Описание |
|-------|--------|----------|
| [`products`](docs/products.md) | 21 | Товары: создание, обновление, цены, остатки, атрибуты |
| [`fbs`](docs/fbs.md) | 17 | FBS-отправления: списки, отмены, этикетки, акты |
| [`fbo`](docs/fbo.md) | 9 | FBO: отправления, поставки, склады |
| [`categories`](docs/categories.md) | 4 | Категории и атрибуты товаров |
| [`finance`](docs/finance.md) | 4 | Финансы: транзакции, итоги, движение средств |
| [`analytics`](docs/analytics.md) | 3 | Аналитика: данные, остатки, оборачиваемость |
| [`warehouses`](docs/warehouses.md) | 2 | Склады и способы доставки |
| [`returns`](docs/returns.md) | 8 | Возвраты FBO/FBS/rFBS |
| [`chats`](docs/chats.md) | 6 | Чаты с покупателями |
| [`promos`](docs/promos.md) | 6 | Акции и промо |
| [`strategies`](docs/strategies.md) | 4 | Ценовые стратегии |
| [`rating`](docs/rating.md) | 3 | Рейтинг и качество продавца |
| [`reports`](docs/reports.md) | 4 | Отчёты |
| [`reviews`](docs/reviews.md) | 4 | Отзывы покупателей |
| [`questions`](docs/questions.md) | 3 | Вопросы покупателей |
| [`cancellations`](docs/cancellations.md) | 4 | Заявки на отмену |
| [`certificates`](docs/certificates.md) | 6 | Сертификаты |
| [`barcodes`](docs/barcodes.md) | 2 | Штрихкоды |
| [`brands`](docs/brands.md) | 1 | Бренды |

---

## MCP-сервер

### Установка

#### Шаг 1. Получить API-ключи

1. Войдите в [Ozon Seller](https://seller.ozon.ru/)
2. Перейдите в **Настройки** → **API-ключи**
3. Создайте ключ (Admin)
4. Скопируйте `Client-Id` и `Api-Key`

#### Шаг 2. Подключить MCP-сервер

### Подключение к Claude Code

**Способ 1: через uvx** (не требует установки пакета)

> Требуется [uv](https://docs.astral.sh/uv/) — если не установлен:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

```bash
claude mcp add ozon-seller \
  -e OZON_CLIENT_ID=ваш_client_id \
  -e OZON_API_KEY=ваш_api_key \
  -- uvx mcp-server-ozon-seller
```

**Способ 2: через pip**

```bash
pip install mcp-server-ozon-seller

claude mcp add ozon-seller \
  -e OZON_CLIENT_ID=ваш_client_id \
  -e OZON_API_KEY=ваш_api_key \
  -- mcp-server-ozon-seller
```

Для удаления:
```bash
claude mcp remove ozon-seller
```

### Подключение к Claude Desktop

Добавьте в конфигурационный файл:

| Клиент | ОС | Путь к файлу |
|--------|----|-------------|
| Claude Code | все | `~/.claude/settings.json` (секция `mcpServers`) |
| Claude Desktop | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop | Linux | `~/.config/Claude/claude_desktop_config.json` |

**Через uvx:**
```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "uvx",
      "args": ["mcp-server-ozon-seller"],
      "env": {
        "OZON_CLIENT_ID": "ваш_client_id",
        "OZON_API_KEY": "ваш_api_key"
      }
    }
  }
}
```

**Через pip** (после `pip install mcp-server-ozon-seller`):
```json
{
  "mcpServers": {
    "ozon-seller": {
      "command": "mcp-server-ozon-seller",
      "env": {
        "OZON_CLIENT_ID": "ваш_client_id",
        "OZON_API_KEY": "ваш_api_key"
      }
    }
  }
}
```

### Подключение через --mcp-config

Подключает сервер только на время одной сессии Claude, не сохраняя в настройки. Токен хранится в отдельном `.env.mcp` файле, а не в конфиге Claude.

Из JSON-строки:
```bash
claude --mcp-config '{"ozon-seller":{"command":"bash","args":["-c","source ~/.env.mcp && exec uvx mcp-server-ozon-seller"]}}'
```

Из файла:
```bash
claude --mcp-config ~/mcp-servers.json
```

Пример `~/mcp-servers.json`:
```json
{
  "ozon-seller": {
    "command": "bash",
    "args": ["-c", "source ~/.env.mcp && exec uvx mcp-server-ozon-seller"]
  }
}
```

Пример `~/.env.mcp`:
```
OZON_CLIENT_ID=ваш_client_id
OZON_API_KEY=ваш_api_key
```

#### Шаг 3. Проверить

Попросите Claude: *«покажи мои товары на Ozon»* — он вызовет `ozon_search`, затем `ozon_execute`.

### Примеры (MCP)

- «покажи мои товары на Ozon» → `ozon_search("products list")` → `ozon_execute("product-list")`
- «отмени FBS отправление 12345678-0001-1» → `ozon_execute("fbs-posting-cancel", ...)`
- «скачай акт приёмки №42» → `ozon_execute_file("fbs-act-pdf", ...)`
- «какие FBS заказы ещё не собраны?» → `ozon_execute("fbs-postings-list", ...)`
- «покажи финансовые транзакции за апрель» → `ozon_execute("finance-transactions", ...)`

---

## CLI-утилита

### Установка (CLI)

```bash
pip install mcp-server-ozon-seller
```

Переменные окружения `OZON_CLIENT_ID` и `OZON_API_KEY` должны быть установлены:

```bash
export OZON_CLIENT_ID=ваш_client_id
export OZON_API_KEY=ваш_api_key
```

Или через файл:

```bash
ozon-seller-cli --env /path/to/.env <command>
```

Формат файла — `KEY=VALUE`, по одной переменной на строку, `#`-комментарии.

### Использование (CLI)

Без аргументов запускается MCP-сервер, с командой — CLI. Все команды выводят JSON.

```bash
# Версия
ozon-seller-cli --version

# Справка
ozon-seller-cli --help
ozon-seller-cli <command> --help
```

### Примеры команд

```bash
# Товары
ozon-seller-cli product-list --limit 10
ozon-seller-cli product-info --offer-id SKU-001
ozon-seller-cli product-stocks-info

# FBS-отправления
ozon-seller-cli fbs-list
ozon-seller-cli fbs-cancel-reasons
ozon-seller-cli fbs-label 12345678-0001-1

# FBO
ozon-seller-cli fbo-list
ozon-seller-cli fbo-supply-list

# Финансы и аналитика
ozon-seller-cli finance-transactions '{"date": {"from": "2026-04-01", "to": "2026-04-25"}}'
ozon-seller-cli analytics-stock

# Возвраты
ozon-seller-cli returns-fbs
ozon-seller-cli returns-fbo

# Другое
ozon-seller-cli warehouses
ozon-seller-cli categories
ozon-seller-cli rating
ozon-seller-cli reviews
ozon-seller-cli brands
```

---

## Pydantic-модели

Пакет содержит типизированные Pydantic-модели всех объектов API. Модели можно использовать в своих Python-программах для валидации данных и автодополнения в IDE.

### Установка (библиотеки)

```bash
pip install mcp-server-ozon-seller
```

### Использование в своих программах

```python
from mcp_server_ozon_seller.models import FbsPostingsListParams

# Валидация данных
params = FbsPostingsListParams.model_validate({
    "filter_dict": {"status": "awaiting_packaging"},
    "limit": 50,
})
print(params.model_dump_json())

# Создание объекта
params = FbsPostingsListParams(limit=10)
print(params.limit)  # type-safe доступ к полям
```

Все модели используют `extra="allow"` для forward compatibility — неизвестные поля API не вызывают ошибок.

Полный список моделей: [`models.py`](src/mcp_server_ozon_seller/models.py)

---

## Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|------------|:------------:|:------------:|----------|
| `OZON_CLIENT_ID` | да | — | Client-Id из личного кабинета Ozon Seller |
| `OZON_API_KEY` | да | — | Api-Key из личного кабинета Ozon Seller |
| `OZON_TIMEOUT` | нет | `30` | Таймаут HTTP-запросов к API (секунды) |
| `OZON_FILE_TIMEOUT` | нет | `60` | Таймаут скачивания файлов (секунды) |

Получить ключи: [Ozon Seller](https://seller.ozon.ru/) → Настройки → API-ключи.

## Разработка

```bash
pip install -e ".[test]"
ruff check src/ tests/
pytest tests/ -v
```

## Лицензия

MIT
