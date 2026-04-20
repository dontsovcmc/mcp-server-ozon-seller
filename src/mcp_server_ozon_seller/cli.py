"""CLI для управления FBS-отправлениями Ozon Seller."""

import json
import os
import sys
import logging
from argparse import ArgumentParser

from .ozon_api import OzonSellerAPI

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger(__name__)

DEFAULT_LABELS_DIR = os.path.expanduser("~/.config/mcp-server-ozon-seller/labels")


def _load_env(path: str) -> None:
    """Простая загрузка .env без внешних зависимостей."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл окружения не найден: {path}")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)
    log.info(f"Загружены переменные из {path}")


def _get_api(args) -> OzonSellerAPI:
    client_id = args.client_id or os.getenv("OZON_CLIENT_ID")
    api_key = args.api_key or os.getenv("OZON_API_KEY")
    if not client_id:
        raise ValueError("Client-Id не указан (--client-id или OZON_CLIENT_ID)")
    if not api_key:
        raise ValueError("Api-Key не указан (--api-key или OZON_API_KEY)")
    return OzonSellerAPI(client_id, api_key)


# ── Subcommands ─────────────────────────────────────────────────────


def cmd_list(args) -> None:
    """Список несобранных FBS-заказов."""
    api = _get_api(args)
    postings = api.get_unfulfilled_orders(days=args.days)

    if not postings:
        print("Нет несобранных заказов")
        return

    if args.json:
        print(json.dumps(postings, ensure_ascii=False, indent=2))
        return

    print(f"\n{'Номер отправления':<26} {'Товары':<40} {'Кол-во':>6}  {'Дата отгрузки'}")
    print("─" * 90)
    for p in postings:
        pn = p.get("posting_number", "?")
        products = p.get("products", [])
        names = ", ".join(prod.get("name", "?")[:35] for prod in products)
        total_qty = sum(prod.get("quantity", 0) for prod in products)
        ship_date = p.get("shipment_date", "")[:10]
        print(f"{pn:<26} {names:<40} {total_qty:>6}  {ship_date}")
    print("─" * 90)
    print(f"Итого: {len(postings)} отправлений\n")


def cmd_labels(args) -> None:
    """Скачать PDF-этикетки."""
    api = _get_api(args)
    out = args.output_dir
    os.makedirs(out, exist_ok=True)

    if args.posting:
        numbers = args.posting
    else:
        postings = api.get_unfulfilled_orders(days=args.days)
        numbers = [p["posting_number"] for p in postings]

    if not numbers:
        print("Нет отправлений для скачивания")
        return

    downloaded = 0
    skipped = 0
    errors = 0
    saved_files: list[str] = []

    for pn in numbers:
        filepath = os.path.join(out, f"{pn}.pdf")
        if os.path.exists(filepath):
            log.info(f"Пропущен (уже существует): {filepath}")
            skipped += 1
            saved_files.append(filepath)
            continue
        try:
            pdf_bytes = api.get_label_pdf(pn)
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
            abs_path = os.path.abspath(filepath)
            log.info(f"Сохранён: {abs_path}")
            downloaded += 1
            saved_files.append(abs_path)
        except RuntimeError as e:
            log.error(str(e))
            errors += 1

    print(f"\n=== Итого ===")
    print(f"Найдено отправлений:  {len(numbers)}")
    print(f"Скачано этикеток:     {downloaded}")
    if skipped:
        print(f"Пропущено (уже есть): {skipped}")
    if errors:
        print(f"Ошибки:               {errors}")
    print(f"Папка: {os.path.abspath(out)}")

    if saved_files:
        print(f"\nФайлы:")
        for f in saved_files:
            print(f"  {f}")


def cmd_ship(args) -> None:
    """Собрать заказы."""
    api = _get_api(args)

    if args.all:
        postings = api.get_unfulfilled_orders(days=args.days)
    elif args.posting:
        postings = [api.get_posting(pn) for pn in args.posting]
    else:
        print("Укажите --posting или --all")
        sys.exit(1)

    if not postings:
        print("Нет отправлений для сборки")
        return

    shipped = 0
    errors = 0

    for p in postings:
        pn = p.get("posting_number", "")
        items = [
            {"sku": prod["sku"], "quantity": prod["quantity"]}
            for prod in p.get("products", [])
        ]
        try:
            api.ship_posting(pn, items)
            log.info(f"{pn}: собран")
            shipped += 1
        except RuntimeError as e:
            log.error(f"{pn}: {e}")
            errors += 1

    print(f"\n=== Итого ===")
    print(f"Всего отправлений: {len(postings)}")
    print(f"Собрано:           {shipped}")
    if errors:
        print(f"Ошибки:            {errors}")


# ── Entry point ─────────────────────────────────────────────────────


def main() -> None:
    parser = ArgumentParser(
        prog="ozon-seller-cli",
        description="CLI для управления FBS-отправлениями Ozon Seller",
    )
    parser.add_argument("--env", help="Путь к .env файлу")
    parser.add_argument("--client-id", dest="client_id", help="OZON Client-Id")
    parser.add_argument("--api-key", dest="api_key", help="OZON Api-Key")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_parser = subparsers.add_parser("list", help="Список несобранных FBS-заказов")
    list_parser.add_argument("--days", type=int, default=7, help="За сколько дней (по умолчанию 7)")
    list_parser.set_defaults(func=cmd_list)

    # labels
    labels_parser = subparsers.add_parser("labels", help="Скачать PDF-этикетки")
    labels_parser.add_argument("--posting", nargs="*", help="Номера отправлений (без указания — все несобранные)")
    labels_parser.add_argument("--days", type=int, default=7, help="За сколько дней (по умолчанию 7)")
    labels_parser.add_argument("--output-dir", dest="output_dir", default=DEFAULT_LABELS_DIR,
                               help="Папка для PDF")
    labels_parser.set_defaults(func=cmd_labels)

    # ship
    ship_parser = subparsers.add_parser("ship", help="Собрать заказы")
    ship_parser.add_argument("--posting", nargs="*", help="Номера отправлений")
    ship_parser.add_argument("--all", action="store_true", help="Собрать все несобранные заказы")
    ship_parser.add_argument("--days", type=int, default=7, help="За сколько дней (по умолчанию 7)")
    ship_parser.set_defaults(func=cmd_ship)

    args = parser.parse_args()

    if args.env:
        _load_env(args.env)

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        log.error(str(err))
        sys.exit(1)
