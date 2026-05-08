"""MCP server for Ozon Seller API — search + execute pattern."""

from ._shared import mcp, _get_api, _to_json, _parse_json, _save_bytes


def _search_actions(query: str, domain: str = "", limit: int = 10) -> list[dict]:
    from .actions import ACTIONS

    tokens = query.lower().split()
    if not tokens:
        return []

    scored: list[tuple[int, dict]] = []
    for action in ACTIONS.values():
        if domain and action.domain != domain:
            continue

        score = 0
        action_id_lower = action.id.lower()
        desc_lower = action.description.lower()
        kw_lower = [k.lower() for k in action.keywords]
        domain_lower = action.domain.lower()

        for t in tokens:
            if t == action_id_lower:
                score += 1000
            if t in action_id_lower:
                score += 10
            if t in desc_lower:
                score += 5
            if any(t in kw for kw in kw_lower):
                score += 8
            if t in domain_lower:
                score += 3

        if score > 0:
            params_schema = None
            if action.params_model is not None:
                params_schema = action.params_model.model_json_schema()

            scored.append((score, {
                "id": action.id,
                "domain": action.domain,
                "description": action.description,
                "is_destructive": action.is_destructive,
                "is_file": action.is_file,
                "params_schema": params_schema,
            }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]


def _dispatch(action, api, params: dict):
    """Call the API method with validated params."""
    import inspect

    method = getattr(api, action.api_method)

    if action.params_model is None:
        return method()

    validated = action.params_model.model_validate(params)
    data = validated.model_dump(exclude_none=True, by_alias=True)

    sig = inspect.signature(method)
    method_params = list(sig.parameters.keys())
    if len(method_params) == 1 and method_params[0] == "params":
        return method(data)

    return method(**data)


@mcp.tool(annotations={"readOnlyHint": True})
def ozon_search(query: str, domain: str = "", limit: int = 10) -> str:
    """Find available Ozon Seller API actions by intent.

    Args:
        query: natural language description of what you want to do
        domain: optional filter (products, fbs, fbo, categories, finance,
                analytics, warehouses, returns, chats, promos, strategies,
                rating, reports, reviews, questions, cancellations,
                certificates, barcodes, brands)
        limit: max results (default 10)
    """
    return _to_json(_search_actions(query, domain, limit))


@mcp.tool(annotations={"readOnlyHint": False})
def ozon_execute(action: str, params_json: str = "{}") -> str:
    """Execute an Ozon Seller API action by ID.

    Use ozon_search first to find the action ID and its parameter schema.

    Args:
        action: action ID from ozon_search results (e.g. "product-list")
        params_json: JSON object with action parameters matching the schema
    """
    from .actions import ACTIONS

    if action not in ACTIONS:
        return _to_json({"error": f"Unknown action: {action}. Use ozon_search to find valid actions."})

    act = ACTIONS[action]

    if act.is_file:
        return _to_json({"error": f"Action {action} returns a file. Use ozon_execute_file instead."})

    params = _parse_json(params_json, "params_json")
    api = _get_api()

    result = _dispatch(act, api, params)
    return _to_json(result)


@mcp.tool(annotations={"readOnlyHint": False})
def ozon_execute_file(action: str, file_path: str, params_json: str = "{}") -> str:
    """Execute an Ozon Seller API action that downloads a file.

    Args:
        action: action ID for download actions
        file_path: local file path to save the downloaded file
        params_json: JSON object with action parameters
    """
    from .actions import ACTIONS

    if action not in ACTIONS:
        return _to_json({"error": f"Unknown action: {action}. Use ozon_search to find valid actions."})

    act = ACTIONS[action]

    if not act.is_file:
        return _to_json({"error": f"Action {action} does not return a file. Use ozon_execute instead."})

    params = _parse_json(params_json, "params_json")
    api = _get_api()

    result = _dispatch(act, api, params)
    return _save_bytes(result, file_path)
