# CLAUDE.md

## Разработка

**CRITICAL: Все правила разработки описаны в [development.md](development.md). Всегда следовать им при любых изменениях кода, тестов и документации.**

### Запуск из исходников

```bash
pip install -e ".[test]"
```

### Запуск тестов

```bash
pytest tests/ -v
```

Тесты мокают Ozon API — `OZON_API_KEY` и `OZON_CLIENT_ID` не нужны.

### CI

GitHub Actions: `.github/workflows/test.yml`, `runs-on: self-hosted`. Токен не требуется.

### Структура

```
src/mcp_server_ozon_seller/
├── __init__.py     # main(), версия
├── __main__.py     # python -m entry point
├── _shared.py      # FastMCP instance, хелперы (_get_api, _to_json, _parse_json, _safe_output_path, _save_bytes)
├── server.py       # 3 MCP tools: ozon_search, ozon_execute, ozon_execute_file
├── actions.py      # Каталог 111 действий (Action dataclass, ACTIONS dict)
├── models.py       # Pydantic модели параметров (75 классов, Field(description=...))
├── ozon_api.py     # HTTP-клиент Ozon Seller API (~90 методов)
└── cli.py          # CLI-интерфейс (111 субкоманд)
docs/
├── products.md     # 21 действие
├── fbs.md          # 17 действий
├── fbo.md          # 9 действий
├── categories.md   # 4 действия
├── finance.md      # 4 действия
├── analytics.md    # 3 действия
├── warehouses.md   # 2 действия
├── returns.md      # 8 действий
├── chats.md        # 6 действий
├── promos.md       # 6 действий
├── strategies.md   # 4 действия
├── rating.md       # 3 действия
├── reports.md      # 4 действия
├── reviews.md      # 4 действия
├── questions.md    # 3 действия
├── cancellations.md# 4 действия
├── certificates.md # 6 действий
├── barcodes.md     # 2 действия
└── brands.md       # 1 действие
```

### Паттерн Search + Execute

Сервер предоставляет 3 MCP-инструмента вместо 111 отдельных. Все 111 действий доступны через каталог:

- `ozon_search(query, domain?, limit?)` — поиск действий по ключевым словам
- `ozon_execute(action, params_json)` — выполнение действия по ID
- `ozon_execute_file(action, file_path, params_json)` — скачивание файла

Каталог (`actions.py`) хранит для каждого действия: ID, домен, описание, Pydantic-модель параметров, имя метода API, флаги (destructive, file), ключевые слова для поиска.

### Добавление нового действия

1. Добавить метод в `ozon_api.py`
2. Если нужна новая модель параметров — добавить в `models.py` с `Field(description=...)`
3. Добавить `Action(...)` в `_ACTIONS_LIST` в `actions.py`
4. Добавить CLI-команду в `cli.py` (subparser + handler) с `help=` на каждом аргументе
5. Добавить строку в соответствующий файл `docs/<domain>.md`

### Ozon Seller API

- Документация: https://docs.ozon.ru/api/seller/
- Base URL: `https://api-seller.ozon.ru`
- Авторизация: `Client-Id` + `Api-Key` в заголовках

### Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|-----------|-------------|-------------|----------|
| `OZON_CLIENT_ID` | да | — | Client ID продавца |
| `OZON_API_KEY` | да | — | API Key продавца |
| `OZON_TIMEOUT` | нет | `30` | Таймаут обычных запросов (секунды) |
| `OZON_FILE_TIMEOUT` | нет | `60` | Таймаут файловых операций (секунды) |

### Обновление MCP-сервера

Когда пользователь просит "обнови mcp ozon-seller":

1. Определить способ установки:
   ```bash
   which mcp-server-ozon-seller && pip show mcp-server-ozon-seller
   ```
2. Обновить пакет:
   - **pip:** `pip install --upgrade mcp-server-ozon-seller`
   - **uvx:** `uvx --upgrade mcp-server-ozon-seller`
3. Проверить версию:
   ```bash
   mcp-server-ozon-seller --version 2>/dev/null || python -c "import mcp_server_ozon_seller; print(mcp_server_ozon_seller.__version__)"
   ```
4. Сообщить пользователю новую версию и попросить перезапустить Claude Code (MCP-серверы перезапускаются при рестарте).

### Правила

- **CRITICAL: НИКОГДА не читать содержимое `.env` файлов** — запрещено использовать `cat`, `Read`, `grep`, `head`, `tail` и любые другие способы чтения `.env`. Для загрузки переменных использовать **только** `source <path>/.env`. Для проверки наличия файла — только `test -f`. Для проверки наличия переменной — `source .env && test -n "$VAR_NAME"` (без вывода значения).
- **CRITICAL: НИКОГДА не коммить в master!** Все коммиты — только в рабочую ветку.
- **Все изменения — через Pull Request в master.** Создать ветку, закоммитить, сделать rebase на свежий master, запушить, создать PR.
- **ПЕРЕД КОММИТОМ проверить, не слита ли текущая ветка в master.** Если ветка уже слита (merged) — создать новую ветку от свежего master и делать новый PR. Никогда не пушить в уже слитую ветку.
- **MANDATORY BEFORE EVERY `git push`: rebase onto fresh master:**
  ```bash
  git checkout master && git remote update && git pull && git checkout - && git rebase master
  ```
- **NEVER use `git stash`.**
- **NEVER use merge commits. ALWAYS rebase.**
- Не хардкодить токены и секреты в коде.
- stdout в MCP сервере занят JSON-RPC — для логов использовать только stderr.
- **ПЕРЕД КАЖДЫМ КОММИТОМ** проверять все исходные файлы, тесты и документацию на наличие реальных персональных данных (ИНН, номера счетов, имена, адреса, телефоны, email). Заменять на вымышленные.
- **В КАЖДОМ PR** обновлять версию в `pyproject.toml` и `src/mcp_server_ozon_seller/__init__.py` (patch для фиксов, minor для новых фич).
- **ПЕРЕД публикацией в MCP-реестр** обязательно запускать `mcp-publisher validate` — проверяет `server.json` на соответствие схеме реестра (лимиты длины полей и т.д.).
- Пути для записи файлов — только через `_safe_output_path()` (home или temp). Dotfiles под home запрещены.
