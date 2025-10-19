from fastmcp import FastMCP, Context
from typing import Any, Dict, Annotated
from pydantic import Field
from config import config
from productive_client import client
import tools
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(server):
    """Server lifespan context manager"""
    # Startup
    if not config.validate():
        raise ValueError("Invalid configuration: API token and base URL are required")
    
    yield
    
    # Shutdown
    await client.close()

mcp = FastMCP(
    name="Productive MCP Server",
    instructions="Use this tool to access Productive projects, tasks, comments, and todo-lists. Focus on providing accurate and concise information based on the data available in Productive. If a project name or ID is provided, focus on that project. If a task ID is provided, focus on that task.",
    lifespan=lifespan,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn",
    on_duplicate_prompts="warn"
)

@mcp.tool
async def get_projects(ctx: Context) -> Dict[str, Any]:
    """Get all active projects with budgets, deadlines, and team assignments.

    Returns comprehensive project data including:
    - Project budgets, hourly rates, and cost tracking
    - Team members with roles and hourly rates
    - Deadlines, start/end dates, and project status
    - Client information and contact details
    """
    return await tools.get_projects(ctx)

@mcp.tool
async def get_tasks(
    ctx: Context,
    project_id: Annotated[
        int, Field(description="Productive project ID to filter tasks by")
    ] = None,
    page_number: Annotated[
        int, Field(description="Page number for pagination")
    ] = None,
    page_size: Annotated[
        int, Field(description="Number of tasks per page (default 20, max 200)")
    ] = 20,
    sort: Annotated[
        str,
        Field(
            description="Sort parameter (e.g., 'last_activity_at', '-last_activity_at', 'created_at', 'due_date'). Use '-' prefix for descending order. Defaults to '-last_activity_at' (most recent first)."
        ),
    ] = "-last_activity_at",
    extra_filters: Annotated[
        dict,
        Field(
            description="Additional Productive query filters using API syntax. Common filters: filter[status][eq] ('open'), filter[project_id][eq] (ID), filter[assignee_id][eq] (ID), filter[due_date][gte] (date)."
        ),
    ] = None,
) -> Dict[str, Any]:
    """Get tasks with optional filtering and pagination.

    Supports Productive's native query-language:
      - Pagination: page_number, page_size (default 15)
      - Filtering: project_id, or any extra_filters dict
      - Sorting: sort parameter (defaults to most recent activity first)
      - All params are optional; omit to fetch all tasks.

    Returns:
        Dictionary of tasks matching the provided filters (passed through to the Productive API)
    """
    return await tools.get_tasks(
        ctx,
        project_id=project_id,
        page_number=page_number,
        page_size=page_size,
        sort=sort,
        extra_filters=extra_filters
    )

@mcp.tool
async def get_task(
    task_id: Annotated[int, Field(description="Productive task ID")],
    ctx: Context,
) -> Dict[str, Any]:
    """Get detailed task information by ID including all related data.

    Returns comprehensive task details including:
    - Task description, priority, and current status
    - Assigned team member with role and hourly rate
    - Parent project with budget and client details
    - Time tracking: estimated vs actual hours
    - All comments and discussion history
    - Attached files and checklist items (todos)
    - Due dates, start dates, and completion timeline

    Args:
        task_id: Productive task ID
    """
    return await tools.get_task(task_id, ctx)

@mcp.tool
async def get_comments(
    ctx: Context,
    project_id: Annotated[
        int, Field(description="Productive project ID to filter comments by")
    ] = None,
    task_id: Annotated[
        int, Field(description="Productive task ID to filter comments by")
    ] = None,
    page_number: Annotated[int, Field(description="Page number for pagination")] = None,
    page_size: Annotated[
        int, Field(description="Number of comments per page (default 20, max 200)")
    ] = 20,
    extra_filters: Annotated[
        dict,
        Field(
            description="Additional Productive query filters using API syntax. Common filters: filter[project_id][eq] (ID), filter[task_id][eq] (ID), filter[discussion_id][eq] (ID)."
        ),
    ] = None,
) -> Dict[str, Any]:
    """Get all comments across projects and tasks with full context.

    Returns comprehensive comment data including:
    - Comment text, author, and timestamp
    - Parent entity (project, task, or other) with details
    - Discussion threads and replies
    - Attachments and file references
    - Mentions of team members or clients
    """
    return await tools.get_comments(
        ctx,
        project_id=project_id,
        task_id=task_id,
        page_number=page_number,
        page_size=page_size,
        extra_filters=extra_filters
    )

@mcp.tool
async def get_comment(
    comment_id: Annotated[int, Field(description="Productive comment ID")],
    ctx: Context,
) -> Dict[str, Any]:
    """Get specific comment details with full context and discussion thread.

    Returns detailed comment information including:
    - Complete comment text and formatting
    - Author details and timestamp
    - Parent entity (project, task, etc.) with full context
    - Reply thread and conversation flow
    - Attached files, images, or documents
    - Mentions and references to team members

    Args:
        comment_id: Productive comment ID
    """
    return await tools.get_comment(comment_id, ctx)

@mcp.tool
async def get_todos(
    ctx: Context,
    task_id: Annotated[int, Field(description="Productive task ID to filter todos by")] = None,
    page_number: Annotated[int, Field(description="Page number for pagination")] = None,
    page_size: Annotated[int, Field(description="Number of todos per page (default 20, max 200)")] = 20,
    extra_filters: Annotated[dict, Field(description="Additional Productive query filters using API syntax. Common filters: filter[task_id][eq] (ID), filter[status][eq] (0/1), filter[assignee_id][eq] (ID).")] = None
) -> Dict[str, Any]:
    """Get all todo checklist items across all tasks and projects.

    Returns comprehensive todo data including:
    - Checkbox items within tasks for granular tracking
    - Completion status and assignee information
    - Parent task details with project context
    - Due dates and priority relative to parent task
    - Estimated vs actual time for checklist items
    """
    return await tools.get_todos(
        ctx,
        task_id=task_id,
        page_number=page_number,
        page_size=page_size,
        extra_filters=extra_filters
    )

@mcp.tool
async def get_todo(
    todo_id: Annotated[int, Field(description="Productive todo ID")],
    ctx: Context,
) -> Dict[str, Any]:
    """Get specific todo checklist item details with full task context.

    Returns detailed todo information including:
    - Checkbox item text and completion status
    - Parent task with project and client details
    - Assignee and team member information
    - Due date relative to parent task timeline
    - Time estimates vs actual completion time
    - Related comments and file attachments

    Args:
        todo_id: The Productive todo ID
    """
    return await tools.get_todo(todo_id, ctx)

if __name__ == "__main__":
    mcp.run()