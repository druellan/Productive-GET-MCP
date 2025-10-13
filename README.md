# Productive MCP Server

A Model Context Protocol (MCP) server for accessing Productive API endpoints (projects, tasks, comments, todos) via GET operations. Built with [FastMCP](https://gofastmcp.com/).

This MCP implementation is designed for read-only operations, exposing minimal information to ensure quick access to essential data while optimizing token usage. 

For full API access and extended functionality, check BerwickGeek's implementation: [Productive MCP by BerwickGeek](https://github.com/berwickgeek/productive-mcp).

## Features

- **Get Projects**: Retrieve all projects
- **Get Tasks**: Retrieve all tasks
- **Get Task by ID**: Retrieve a specific task
- **Get Comments**: Retrieve all comments
- **Get Comment by ID**: Retrieve a specific comment
- **Get Todos**: Retrieve all todos
- **Get Todo by ID**: Retrieve a specific todo
- **YAML Output**: All responses are converted from JSON API format to YAML for better LLM readability and less token usage

## Requirements

- Python 3.8+
- Productive API token
- FastMCP 2.0+
- PyYAML 6.0+

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
or
```bash
uv venv && uv sync
```

## Configuration

The server uses environment variables for configuration:

- `PRODUCTIVE_API_KEY`: Your Productive API token (required)
- `PRODUCTIVE_ORGANIZATION`: Your Productive organization ID (required)
- `PRODUCTIVE_BASE_URL`: Base URL for Productive API (default: https://api.productive.io/api/v2)
- `PRODUCTIVE_TIMEOUT`: Request timeout in seconds (default: 30)

## Usage

### Direct Python Execution (Recommended)
```json
    "productive": {
      "command": "python",
      "args": [
        "server.py"
      ],
      "env": {
        "PRODUCTIVE_API_KEY": "<api-key>",
        "PRODUCTIVE_ORGANIZATION": "<organization-id>"
      }
    }
```

### Using UV
```json
    "productive": {
      "command": "uv",
      "args": [
        "--directory", "<path-to-productive-mcp>",
        "run", "server.py"
      ],
      "env": {
        "PRODUCTIVE_API_KEY": "<api-key>",
        "PRODUCTIVE_ORGANIZATION": "<organization-id"
      }
    },
```

## Available Tools

### `get_projects`
Retrieve all projects. Returns paginated results with project details, attributes, and relationships.

### `get_tasks`
Retrieve all tasks. Returns paginated results with task details, attributes, and relationships.

### `get_task`
Retrieve a specific task by ID. Returns detailed task information including attributes and relationships.

### `get_comments`
Retrieve all comments. Returns paginated results with comment details, attributes, and relationships.

### `get_comment`
Retrieve a specific comment by ID. Returns detailed comment information including attributes and relationships.

### `get_todos`
Retrieve all todos. Returns paginated results with todo details, attributes, and relationships.

### `get_todo`
Retrieve a specific todo by ID. Returns detailed todo information including attributes and relationships.

## Output Format

All tools return data in YAML format for improved readability and LLM processing.

- `data`: Contains the main resource data (array for collections, object for single items)
- `meta`: Contains pagination and metadata information
- `links`: Contains pagination links (for collection endpoints)
- `included`: Contains related resource data (when relationships are included)

Example YAML output for projects:
```yaml
data:
- id: '628'
  type: projects
  attributes:
    name: test project
    number: '1'
    project_type_id: 2
    created_at: '2025-10-12T06:07:57.592+02:00'
    archived_at: null
  relationships:
    organization:
      data:
        type: organizations
        id: '1003'
    company:
      meta:
        included: false
meta:
  current_page: 1
  total_pages: 1
  total_count: 3
  page_size: 30
  max_page_size: 200
links:
  first: 'http://api.productive.io/api/v2/projects?page%5Bnumber%5D=1&page%5Bsize%5D=30'
  last: 'http://api.productive.io/api/v2/projects?page%5Bnumber%5D=1&page%5Bsize%5D=30'
```

## Error Handling

The server provides comprehensive error handling:

- **401 Unauthorized**: Invalid API token
- **404 Not Found**: Resource not found
- **429 Rate Limited**: Too many requests
- **500 Server Error**: Productive API issues

All errors are logged via MCP context with appropriate severity levels.

## Security

- API tokens are loaded from environment variables
- No sensitive data is logged
- HTTPS is used for all API requests
- Error messages don't expose internal details

## License

This project is provided as-is for educational and integration purposes.