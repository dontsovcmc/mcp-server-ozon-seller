# Категории

4 действия в домене `categories`.

| Команда | Описание | Параметры |
|---------|----------|-----------|
| `category-tree` | Дерево категорий | `language` (string, "DEFAULT") |
| `category-attributes` | Атрибуты категории | `description_category_id` (int) *, `language` (string, "DEFAULT"), `type_id` (int, 0) |
| `category-attribute-values` | Значения словаря атрибута | `attribute_id` (int) *, `description_category_id` (int) *, `last_value_id` (int, 0), `limit` (int, 100), `language` (string, "DEFAULT") |
| `category-attribute-values-search` | Поиск по словарю атрибутов | `attribute_id` (int) *, `description_category_id` (int) *, `value` (string) *, `limit` (int, 100), `language` (string, "DEFAULT") |

\* — обязательный параметр
