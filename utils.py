from typing import Any, Dict
import bleach
from config import config


def get_webapp_url(resource_type: str, resource_id: str) -> str:
    """Generate Productive web app URL for a resource.
    
    Args:
        resource_type: Type of resource ('projects', 'tasks', etc.)
        resource_id: The resource ID
        
    Returns:
        URL to view the resource in Productive web app
    """
    org_id = config.organization
    # Productive URLs follow pattern: https://app.productive.io/{org-id}/[resource-type]/{id}
    return f"https://app.productive.io/{org_id}/{resource_type}/{resource_id}"

def _filter_attributes(attributes: Dict[str, Any], obj_type: str) -> Dict[str, Any]:
    """Filter out unwanted attributes and strip HTML from specific fields based on object type."""
    filtered = dict(attributes)
    
    # Fields to remove per type
    remove_fields = {
        'tasks': ['creation_method_id', 'email_key', 'placement'],
        'comments': [],
        'todos': [],
        'pages': ['preferences', 'cover_image_meta', 'custom_fields'],
        'attachments': ['attachable_type', 'attachable_id'],
    }
    
    # Fields to strip HTML from per type
    html_fields = {
        'tasks': ['description'],
        'comments': ['body'],
        'todos': ['description'],
        'pages': ['body'],
    }
    
    # Remove unwanted fields
    for field in remove_fields.get(obj_type, []):
        filtered.pop(field, None)
    
    # Strip HTML from specified fields
    for field in html_fields.get(obj_type, []):
        if field in filtered and isinstance(filtered[field], str):
            filtered[field] = bleach.clean(filtered[field], tags=[], strip=True)
    
    return filtered


def _filter_task_list_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Filter task attributes for list views - keep only essential fields for browsing.
    
    When listing multiple tasks, we want just enough info to identify and select tasks,
    without overwhelming the LLM with descriptions and metadata.
    """
    # Keep only these essential fields
    essential_fields = [
        'title',
        'number',
        'task_number',
        'closed',
        'created_at',
        'updated_at',
        'last_activity_at',
        'initial_estimate',
        'remaining_time',
        'worked_time',
        'billable_time',
        'closed_at',
        'type_id',
        'private'
    ]
    
    filtered = {k: v for k, v in attributes.items() if k in essential_fields}
    return filtered

def remove_null_and_empty(obj: Any) -> Any:
    """Recursively remove null, empty dicts/lists, and empty strings from a dict/list.

    Additionally:
    - Remove meta.included when it's False
    - Remove meta.settings when present
    - Remove pagination links
    - Remove empty meta dicts and empty parent objects after cleanup
    - Filter out unwanted task attributes
    - Remove organization relationships (redundant)
    """
    if isinstance(obj, dict):
        result = {}
        
        for key, value in obj.items():
            # Skip pagination links - not useful for LLMs
            if key == "links":
                continue
            
            # Skip organization relationships - redundant
            if key == "relationships" and isinstance(value, dict):
                value = {k: v for k, v in value.items() if k != "organization"}
                
            cleaned_value = remove_null_and_empty(value)
            
            # Skip empty values
            if cleaned_value in (None, "", {}, []):
                continue
            
            # Filter out unwanted attributes based on object type
            if key == "attributes" and isinstance(cleaned_value, dict):
                obj_type = obj.get('type')
                cleaned_value = _filter_attributes(cleaned_value, obj_type)
            
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
    """Filter Productive API response: remove sensitive fields and clean empty values.
    
    Also adds webapp_url to resources for easy access to the Productive web interface.
    """
    filtered = remove_null_and_empty(response)
    
    # Add webapp URLs to single resource responses
    if isinstance(filtered, dict) and "data" in filtered:
        if isinstance(filtered["data"], dict):
            # Single resource
            _add_webapp_url(filtered["data"])
        elif isinstance(filtered["data"], list):
            # Multiple resources
            for item in filtered["data"]:
                _add_webapp_url(item)
    
    return filtered


def _add_webapp_url(item: Dict[str, Any]) -> None:
    """Add webapp_url to a resource item in-place.
    
    Modifies the item dict to include a webapp_url field for easy access.
    """
    if not isinstance(item, dict):
        return
    
    resource_type = item.get("type")
    resource_id = item.get("id")
    
    if resource_type and resource_id:
        item["webapp_url"] = get_webapp_url(resource_type, resource_id)


def filter_task_list_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Filter task list responses to show only essential fields for browsing.
    
    Removes:
    - descriptions (can be very long)
    - relationships (not needed for list view)
    - non-essential metadata
    
    Keeps only what's needed to identify and select tasks.
    Also adds webapp_url for easy access.
    """
    if not isinstance(response, dict):
        return response
    
    filtered = {}
    
    # Process data array
    if "data" in response and isinstance(response["data"], list):
        filtered_data = []
        for item in response["data"]:
            if isinstance(item, dict) and item.get("type") == "tasks":
                filtered_item = {
                    "id": item.get("id"),
                    "type": item.get("type"),
                }
                
                # Filter attributes to essential fields only
                if "attributes" in item:
                    filtered_item["attributes"] = _filter_task_list_attributes(item["attributes"])
                
                # Add webapp URL for easy access
                _add_webapp_url(filtered_item)

                filtered_data.append(filtered_item)
            else:
                filtered_data.append(item)
        
        filtered["data"] = filtered_data
    
    # Keep meta if present (has useful info like total_count)
    if "meta" in response:
        filtered["meta"] = _clean_meta_object(response["meta"])
    
    # Clean up empty values
    return remove_null_and_empty(filtered)
