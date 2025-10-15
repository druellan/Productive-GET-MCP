from fastmcp import Context
from fastmcp.tools.tool import ToolResult

from productive_client import client, ProductiveAPIError
from utils import filter_response


async def _handle_productive_api_error(ctx: Context, e: ProductiveAPIError, resource_type: str = "data") -> None:
    """Handle ProductiveAPIError consistently across all tool functions.
    
    Args:
        ctx: MCP context for logging and error handling
        e: The ProductiveAPIError exception
        resource_type: Type of resource being fetched (e.g., "projects", "tasks", "comments")
    """
    await ctx.error(f"Productive API error: {e.message}")
    
    if e.status_code == 404:
        await ctx.warning(f"No {resource_type} found")
    elif e.status_code == 401:
        await ctx.error("Invalid API token - check configuration")
    
    raise e


async def get_projects(ctx: Context) -> ToolResult:
    """Get all active projects with budgets, deadlines, and team assignments.
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary containing projects with full project details, budgets, and team assignments
    """
    try:
        await ctx.info("Fetching all projects")
        result = await client.get_projects()
        await ctx.info("Successfully retrieved projects")
        filtered = filter_response(result)
        
        # Create human-readable summary
        project_count = len(filtered.get('data', []))
        summary = f"Retrieved {project_count} active projects with budgets, deadlines, and team assignments"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered
        )

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "projects")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching projects: {str(e)}")
        raise e


async def get_tasks(
    ctx: Context,
    project_id: str = None,
    page_number: int = None,
    page_size: int = None,
    sort: str = "-last_activity_at",
    extra_filters: dict = None
) -> ToolResult:
    """Get tasks with optional filtering and pagination.

    Args:
        ctx: MCP context for logging and error handling
        project_id: Optional Productive project ID to filter tasks by
        page_number: Optional page number for pagination
        page_size: Optional page size for pagination
        sort: Sort parameter (e.g., 'last_activity_at', '-last_activity_at', 'created_at', 'due_date')
              Defaults to '-last_activity_at' (most recent activity first). Use '-' prefix for descending order.
        extra_filters: Optional dict of additional filter query params using Productive syntax
                       (e.g. {'filter[status][eq]': 'open'})

    Returns:
        Dictionary containing tasks with assignments, time tracking, and project context
    """
    try:
        await ctx.info("Fetching tasks")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        if page_size is not None:
            params["page[size]"] = page_size
        if project_id is not None:
            params["filter[project_id][eq]"] = project_id
        if sort:
            params["sort"] = sort
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_tasks(params=params if params else None)
        await ctx.info("Successfully retrieved tasks")

        filtered = filter_response(result)

        # Create human-readable summary (minimal notification)
        task_count = len(filtered.get("data", []))
        summary = f"Notification: {task_count} tasks retrieved from productive.get_tasks"

        return ToolResult(
            content=[summary],
            structured_content=filtered
        )

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "tasks")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching tasks: {str(e)}")
        raise e


async def get_task(task_id: str, ctx: Context) -> ToolResult:
    """Get detailed task information by ID including all related data.
    
    Args:
        task_id: The unique Productive task identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary with complete task details and project context
    """
    try:
        await ctx.info(f"Fetching task with ID: {task_id}")
        result = await client.get_task(task_id)
        await ctx.info("Successfully retrieved task")
        
        filtered = filter_response(result)
        
        # Create human-readable summary
        task_data = filtered.get('data', {})
        task_title = task_data.get('attributes', {}).get('title', 'Unknown')
        summary = f"Retrieved task '{task_title}' (ID: {task_id}) with complete details and project context"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered,
        )
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"task {task_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching task: {str(e)}")
        raise e


async def get_comments(ctx: Context) -> ToolResult:
    """Get all comments across projects and tasks with full context.
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary of comments with full context and related entity details
    """
    try:
        await ctx.info("Fetching all comments")
        result = await client.get_comments()
        await ctx.info("Successfully retrieved comments")
        
        filtered = filter_response(result)
        
        # Create human-readable summary
        comment_count = len(filtered.get('data', []))
        summary = f"Retrieved {comment_count} comments with full context and related entity details"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered,
        )
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "comments")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching comments: {str(e)}")
        raise e


async def get_comment(comment_id: str, ctx: Context) -> ToolResult:
    """Get specific comment details with full context and discussion thread.
    
    Args:
        comment_id: The unique Productive comment identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary with complete comment details and discussion thread
    """
    try:
        await ctx.info(f"Fetching comment with ID: {comment_id}")
        result = await client.get_comment(comment_id)
        await ctx.info("Successfully retrieved comment")
        
        filtered = filter_response(result)
        
        # Create human-readable summary
        comment_data = filtered.get('data', {})
        body_preview = comment_data.get('attributes', {}).get('body', '')[:50]
        if len(body_preview) == 50:
            body_preview += "..."
        summary = f"Retrieved comment (ID: {comment_id}): {body_preview}"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered
        )
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"comment {comment_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching comment: {str(e)}")
        raise e


async def get_todos(ctx: Context) -> ToolResult:
    """Get all todo checklist items across all tasks and projects.
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary of todo checklist items with task context and completion tracking
    """
    try:
        await ctx.info("Fetching all todos")
        result = await client.get_todos()
        await ctx.info("Successfully retrieved todos")
        
        filtered = filter_response(result)
        
        # Create human-readable summary
        todo_count = len(filtered.get('data', []))
        summary = f"Retrieved {todo_count} todo checklist items with task context and completion tracking"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered
        )
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "todos")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching todos: {str(e)}")
        raise e


async def get_todo(todo_id: str, ctx: Context) -> ToolResult:
    """Get specific todo checklist item details with full task context.
    
    Args:
        todo_id: The unique Productive todo checklist item identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary of todo checklist item with full task context and tracking details
    """
    try:
        await ctx.info(f"Fetching todo with ID: {todo_id}")
        result = await client.get_todo(todo_id)
        await ctx.info("Successfully retrieved todo")
        
        filtered = filter_response(result)
        
        # Create human-readable summary
        todo_data = filtered.get('data', {})
        todo_title = todo_data.get('attributes', {}).get('name', 'Unknown')
        is_completed = todo_data.get('attributes', {}).get('completed', False)
        status = "completed" if is_completed else "pending"
        summary = f"Retrieved todo '{todo_title}' (ID: {todo_id}) - Status: {status}"
        
        return ToolResult(
            content=[summary],
            structured_content=filtered
        )
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"todo {todo_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching todo: {str(e)}")
        raise e