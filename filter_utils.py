from typing import Any, Dict

def remove_null_and_empty(obj: Any) -> Any:
    """Recursively remove null, empty dicts/lists, and empty strings from a dict/list."""
    if isinstance(obj, dict):
        return {k: remove_null_and_empty(v) for k, v in obj.items() if v not in (None, {}, [], "")}
    elif isinstance(obj, list):
        return [remove_null_and_empty(v) for v in obj if v not in (None, {}, [], "")]
    else:
        return obj

PROJECT_FIELDS = [
    "id", "type",
    "attributes",
    "relationships"
]

PROJECT_ATTRIBUTE_WHITELIST = [
    "name", "number", "project_number", "project_type_id", "project_color_id",
    "last_activity_at", "time_on_tasks", "archived_at", "created_at", "template", "duplication_status"
]

PROJECT_RELATIONSHIP_WHITELIST = ["organization"]

META_FIELDS = ["current_page", "total_pages", "total_count", "page_size", "max_page_size"]
LINKS_FIELDS = ["first", "last"]

def filter_project_response(response: Dict[str, Any]) -> Dict[str, Any]:
    filtered = {}
    # Filter 'data'
    data = response.get("data")
    if isinstance(data, list):
        filtered["data"] = [filter_project_item(item) for item in data]
    elif isinstance(data, dict):
        filtered["data"] = filter_project_item(data)
    # Filter 'meta'
    meta = response.get("meta")
    if meta:
        filtered["meta"] = {k: v for k, v in meta.items() if k in META_FIELDS and v not in (None, "", [], {})}
    # Filter 'links'
    links = response.get("links")
    if links:
        filtered["links"] = {k: v for k, v in links.items() if k in LINKS_FIELDS and v not in (None, "", [], {})}
    # Remove null/empty recursively
    return remove_null_and_empty(filtered)

def filter_project_item(item: Dict[str, Any]) -> Dict[str, Any]:
    result = {k: item[k] for k in PROJECT_FIELDS if k in item}
    # Attributes
    attrs = result.get("attributes")
    if attrs:
        result["attributes"] = {k: v for k, v in attrs.items() if k in PROJECT_ATTRIBUTE_WHITELIST and v not in (None, "", [], {})}
    # Relationships
    rels = result.get("relationships")
    if rels:
        result["relationships"] = {k: rels[k] for k in PROJECT_RELATIONSHIP_WHITELIST if k in rels}
    return remove_null_and_empty(result)
