import yaml
from typing import Dict, Any

def convert_json_to_yaml(json_data: Dict[str, Any]) -> str:
    """Convert JSON data to YAML format string
    
    Args:
        json_data: Dictionary containing JSON data from Productive API
        
    Returns:
        YAML formatted string representation of the data
    """
    try:
        # Configure YAML dump options for better readability
        yaml_output = yaml.dump(
            json_data,
            default_flow_style=False,
            allow_unicode=True,
            indent=2,
            width=120,
            sort_keys=False
        )
        return yaml_output
    except Exception as e:
        # Fallback: return original data as string if YAML conversion fails
        return f"Error converting to YAML: {str(e)}\nOriginal data: {str(json_data)}"