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
├── server.py       # FastMCP, все tools (~120 tools)
├── ozon_api.py     # HTTP-клиент Ozon Seller API (~120 методов)
├── models.py       # Pydantic-модели для валидации в тестах
└── cli.py          # CLI entry point (argparse, ~80 subcommands)
```

### Ozon Seller API

- Документация: https://docs.ozon.ru/api/seller/
- Base URL: `https://api-seller.ozon.ru`
- Авторизация: `Client-Id` + `Api-Key` в заголовках

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
