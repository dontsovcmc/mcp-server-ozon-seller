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

### Структура

```
src/mcp_server_ozon_seller/
├── __init__.py     # main(), версия
├── __main__.py     # python -m entry point
├── server.py       # FastMCP, все tools
├── ozon_api.py     # HTTP-клиент Ozon Seller API
└── cli.py          # CLI entry point (argparse, subcommands)
```

### Ozon Seller API

- Документация: https://docs.ozon.ru/api/seller/
- Base URL: `https://api-seller.ozon.ru`
- Авторизация: `Client-Id` + `Api-Key` в заголовках

### Правила

- **CRITICAL: НИКОГДА не коммить в master!** Все коммиты — только в рабочую ветку.
- **Все изменения — через Pull Request в master.**
- **MANDATORY BEFORE EVERY `git push`: rebase onto fresh master:**
  ```bash
  git checkout master && git remote update && git pull && git checkout - && git rebase master
  ```
- **NEVER use `git stash`.**
- **NEVER use merge commits. ALWAYS rebase.**
- Не хардкодить токены и секреты в коде.
- stdout в MCP сервере занят JSON-RPC — для логов использовать только stderr.
- **В КАЖДОМ PR** обновлять версию в `pyproject.toml` и `src/mcp_server_ozon_seller/__init__.py`.
