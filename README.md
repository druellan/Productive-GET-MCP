# Productive.io MCP Server

A Model Context Protocol (MCP) server for accessing Productive.io API endpoints (projects, tasks, comments, todos, pages, attachments) via GET operations. Built with [FastMCP](https://gofastmcp.com/).

This implementation is tailored for read-only operations, providing streamlined access to essential data while minimizing token consumption. It is optimized for efficiency and simplicity, exposing only the necessary information. For a more comprehensive solution, consider BerwickGeek's implementation: [Productive MCP by BerwickGeek](https://github.com/berwickgeek/productive-mcp).

## Features

- **Get Projects**: Retrieve all projects
- **Get Tasks**: Retrieve tasks with filtering and pagination
- **Get Task**: Retrieve a specific task by internal ID
- **Get Project Tasks**: Retrieve all tasks for a specific project (lightweight)
- **Get Project Task**: Retrieve a task by its number (e.g., #960)
- **Get Recent Updates**: Summarized activity feed for status updates
- **Get Comments**: Retrieve comments with filtering
- **Get Pages**: Retrieve pages/documents with filtering
- **Get Page**: Retrieve a specific page/document by ID
- **Get Attachments**: Retrieve attachments/files with filtering
- **Get Todos**: Retrieve todo items with filtering
- **Get Todo**: Retrieve a specific todo by ID
- **LLM-Optimized Responses**: Filtered output removes noise, strips HTML, and reduces token consumption

## Requirements

- Python 3.8+
- Productive API token
- FastMCP 2.0+

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
Retrieve all active projects. Returns paginated results with project details, attributes, and relationships.

**Properties:**
- No parameters (returns all projects)

### `get_tasks`
Retrieve tasks with optional filtering and pagination.

**Properties:**
- `project_id` (int, optional): Filter tasks by Productive project ID
- `page_number` (int, optional): Page number for pagination
- `page_size` (int, optional): Page size for pagination (default: 20)
- `sort` (str, optional): Sort parameter (e.g., 'last_activity_at', '-last_activity_at', 'created_at', 'due_date')
- `extra_filters` (dict, optional): Additional Productive API filters (e.g., `{'filter[status][eq]': 'open'}`)

### `get_task`
Retrieve a specific task by its internal ID. Returns task details including title, description, status, dates, time tracking metrics, and todo counts.

**Properties:**
- `task_id` (int): The unique Productive task identifier (internal ID, e.g., 14677418)

### `get_project_tasks`
Get all tasks for a specific project. Optimized for browsing with lightweight output (no descriptions or relationships).

**Properties:**
- `project_id` (int): The project ID to get tasks for
- `status` (str, optional): Filter by task status ('open' or 'closed')

### `get_project_task`
Get a task by its  number within a project (e.g., task #960). Returns full task details.

**Properties:**
- `task_number` (str): The task number (e.g., "960")
- `project_id` (int): The project ID containing the task

### `get_comments`
Retrieve comments with optional filtering and pagination.

**Properties:**
- `project_id` (int, optional): Filter comments by Productive project ID
- `task_id` (int, optional): Filter comments by Productive task ID
- `page_number` (int, optional): Page number for pagination
- `page_size` (int, optional): Page size for pagination
- `extra_filters` (dict, optional): Additional Productive API filters (e.g., `{'filter[discussion_id]': '123'}`)

### `get_pages`
Retrieve pages/documents with optional filtering and pagination.

**Properties:**
- `project_id` (int, optional): Filter pages by Productive project ID
- `creator_id` (int, optional): Filter pages by creator ID
- `page_number` (int, optional): Page number for pagination
- `page_size` (int, optional): Page size for pagination

### `get_page`
Retrieve a specific page/document by ID.

**Properties:**
- `page_id` (int): The unique Productive page identifier

### `get_attachments`
Retrieve attachments/files with optional filtering and pagination.

**Properties:**
- `page_number` (int, optional): Page number for pagination
- `page_size` (int, optional): Page size for pagination
- `extra_filters` (dict, optional): Additional Productive API filters

### `get_recent_updates`
Get a summarized feed of recent activities and updates. Perfect for status updates.

**Properties:**
- `hours` (int, optional): Number of hours to look back (default: 24, use 168 for a week)
- `user_id` (int, optional): Filter by specific user/person ID
- `project_id` (int, optional): Filter by specific project ID
- `activity_type` (int, optional): Filter by activity type (1: Comment, 2: Changeset, 3: Email)
- `item_type` (str, optional): Filter by item type (e.g., 'Task', 'Page', 'Deal', 'Workspace')
- `event_type` (str, optional): Filter by event type (e.g., 'create', 'copy', 'update', 'delete')
- `task_id` (int, optional): Filter by specific task ID
- `max_results` (int, optional): Maximum number of activities to return (default: 100, max: 200)


### `get_todos`
Retrieve todo checklist items with optional filtering and pagination.

**Properties:**
- `task_id` (int, optional): Filter todos by Productive task ID
- `page_number` (int, optional): Page number for pagination
- `page_size` (int, optional): Page size for pagination
- `extra_filters` (dict, optional): Additional Productive API filters

### `get_todo`
Retrieve a specific todo checklist item by ID.

**Properties:**
- `todo_id` (int): The unique Productive todo checklist item identifier

## Output Format

All tools return filtered JSON optimized for LLM processing:

**LLM Optimizations:**
- Unwanted fields removed (e.g., `creation_method_id`, `email_key`, `placement` from tasks)
- HTML stripped from descriptions and comments
- Empty/null values removed
- Pagination links removed
- List views use lightweight output (e.g., `get_project_tasks` excludes descriptions and relationships)
- **Web app URLs included**: Each resource includes a `webapp_url` field linking directly to the Productive web interface

**Response Structure:**
- `data`: Main resource data (array for collections, object for single items)
- `meta`: Pagination and metadata
- `included`: Related resource data (when applicable)
- `webapp_url`: Direct link to view the resource in Productive (e.g., `https://app.productive.io/12345/tasks/67890`)

Example JSON output for projects:
```json
{
  "data": [
    {
      "id": "628",
      "type": "projects",
      "attributes": {
        "name": "test project",
        "number": "1",
        "project_type_id": 2,
        "created_at": "2025-10-12T06:07:57.592+02:00",
        "archived_at": null
      },
      "relationships": {
        "organization": {
          "data": {
            "type": "organizations",
            "id": "3003"
          }
        }
      }
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 1,
    "total_count": 3,
    "page_size": 30,
    "max_page_size": 200
  }
}
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

MIT License.