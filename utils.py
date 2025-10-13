from typing import Any, Dict

def remove_null_and_empty(obj: Any) -> Any:
    """Recursively remove null, empty dicts/lists, and empty strings from a dict/list.

    Additionally:
    - Remove meta.included when it's False
    - Remove meta.settings when present
    - Remove pagination links
    - Remove empty meta dicts and empty parent objects after cleanup
    """
    if isinstance(obj, dict):
        result = {}
        
        for key, value in obj.items():
            # Skip pagination links - not useful for LLMs
            if key == "links":
                continue
                
            cleaned_value = remove_null_and_empty(value)
            
            # Skip empty values
            if cleaned_value in (None, "", {}, []):
                continue
            
            # Handle meta objects specially
            if key == "meta" and isinstance(cleaned_value, dict):
                cleaned_meta = _clean_meta_object(cleaned_value)
                if cleaned_meta:
                    result[key] = cleaned_meta
            else:
                result[key] = cleaned_value
        
        return result
    
    elif isinstance(obj, list):
        result = []
        for item in obj:
            cleaned_item = remove_null_and_empty(item)
            if cleaned_item not in (None, "", {}, []):
                result.append(cleaned_item)
        return result
    
    else:
        return obj


def _clean_meta_object(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Clean meta object by removing unwanted fields."""
    cleaned = dict(meta)
    
    # Remove 'included' when it's explicitly False
    if cleaned.get("included") is False:
        cleaned.pop("included", None)
    
    # Remove 'settings' if present
    cleaned.pop("settings", None)
    
    return cleaned


def filter_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Filter Productive API response: remove sensitive fields and clean empty values."""
    return remove_null_and_empty(response)
