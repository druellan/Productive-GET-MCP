from fastmcp import Context
from fastmcp.tools.tool import ToolResult

from productive_client import client, ProductiveAPIError
from utils import filter_response, filter_task_list_response


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

        return filtered

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "projects")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching projects: {str(e)}")
        raise e


async def get_tasks(
    ctx: Context,
    project_id: int = None,
    page_number: int = None,
    page_size: int = 20,
    sort: str = "-last_activity_at",
    extra_filters: dict = None
) -> ToolResult:
    """Get tasks with optional filtering and pagination.

    Args:
        ctx: MCP context for logging and error handling
        project_id: Optional Productive project ID to filter tasks by
        page_number: Optional page number for pagination
        page_size: Page size for pagination (default 20, max 200)
        sort: Sort parameter (e.g., 'last_activity_at', '-last_activity_at', 'created_at', 'due_date')
              Defaults to '-last_activity_at' (most recent activity first). Use '-' prefix for descending order.
        extra_filters: Optional dict of additional filter query params using Productive syntax
                       (e.g. {'filter[status][eq]': 1} for open tasks, or 2 for closed tasks)

    Returns:
        Dictionary containing tasks with assignments, time tracking, and project context
    """
    try:
        await ctx.info("Fetching tasks")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        # Always apply default page_size to ensure consistent pagination
        if page_size is not None:
            params["page[size]"] = page_size
        else:
            params["page[size]"] = 20
        if project_id is not None:
            params["filter[project_id][eq]"] = project_id
        if sort:
            params["sort"] = sort
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_tasks(params=params if params else None)
        await ctx.info("Successfully retrieved tasks")

        filtered = filter_response(result)

        return filtered

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "tasks")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching tasks: {str(e)}")
        raise e


async def get_task(task_id: int, ctx: Context) -> ToolResult:
    """Get detailed task information by ID including all related data.
    
    Args:
        task_id: The unique Productive task identifier (internal ID)
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary with complete task details and project context
    """
    try:
        await ctx.info(f"Fetching task with ID: {task_id}")
        result = await client.get_task(task_id)
        await ctx.info("Successfully retrieved task")
        
        filtered = filter_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"task {task_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching task: {str(e)}")
        raise e


async def get_project_tasks(
    ctx: Context,
    project_id: int,
    status: int = None
) -> ToolResult:
    """Get all tasks for a specific project.
    
    This is optimized for getting a comprehensive view of all tasks in a project.
    
    Args:
        ctx: MCP context for logging and error handling
        project_id: The project ID to get tasks for
        status: Optional filter by task status (1 = open, 2 = closed)
        
    Returns:
        Dictionary containing all tasks for the project with full details
        
    Example:
        get_project_tasks(project_id=343136, status=1)  # Get open tasks
    """
    try:
        await ctx.info(f"Fetching all tasks for project {project_id}")
        
        # Get all tasks for the project with a high limit
        params = {
            "filter[project_id][eq]": project_id,
            "page[size]": 200  # Maximum to get comprehensive view
        }
        
        # Status filter: 1 = open, 2 = closed (per Productive API docs)
        if status is not None:
            params["filter[status][eq]"] = status
        
        result = await client.get_tasks(params=params)
        
        if not result.get("data") or len(result["data"]) == 0:
            await ctx.info(f"No tasks found for project {project_id}")
            return {"data": [], "meta": {"message": f"No tasks found for project {project_id}"}}
        
        # Use lighter filtering for task lists - removes descriptions and relationships
        filtered = filter_task_list_response(result)
        await ctx.info(f"Successfully retrieved {len(result['data'])} tasks for project {project_id}")
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"tasks for project {project_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching tasks: {str(e)}")
        raise e


async def get_project_task(
    ctx: Context,
    task_number: str,
    project_id: int
) -> ToolResult:
    """Get a task by its task number within a specific project.
    
    This is the preferred way to fetch tasks when you know the task number (e.g., #960)
    rather than the internal ID. Task numbers are project-specific.
    
    Args:
        ctx: MCP context for logging and error handling
        task_number: The task number (e.g., "960")
        project_id: The project ID containing the task
        
    Returns:
        Dictionary with complete task details and project context
        
    Example:
        get_project_task(task_number="960", project_id=343136)
    """
    try:
        await ctx.info(f"Fetching task #{task_number} from project {project_id}")
        
        # Get tasks for the project filtered by task_number
        params = {
            "filter[project_id][eq]": project_id,
            "filter[task_number][eq]": task_number,
            "page[size]": 1
        }
        
        result = await client.get_tasks(params=params)
        
        if not result.get("data") or len(result["data"]) == 0:
            raise ProductiveAPIError(
                message=f"Task #{task_number} not found in project {project_id}",
                status_code=404
            )
        
        # Return the first (and should be only) task
        task_data = result["data"][0]
        filtered = filter_response({"data": task_data})
        await ctx.info(f"Successfully retrieved task #{task_number}")
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"task #{task_number}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching task: {str(e)}")
        raise e


async def get_comments(
    ctx: Context,
    project_id: int = None,
    task_id: int = None,
    page_number: int = None,
    page_size: int = 20,
    extra_filters: dict = None
) -> ToolResult:
    """Get all comments across projects and tasks with full context.

    Args:
        ctx: MCP context for logging and error handling
        project_id: Optional Productive project ID to filter comments by
        task_id: Optional Productive task ID to filter comments by
        page_number: Optional page number for pagination
        page_size: Page size for pagination (default 20, max 200)
        extra_filters: Optional dict of additional filter query params using Productive syntax
                       (e.g. {'filter[discussion_id]': '123', 'filter[page_id][]': ['1', '2']})

    Returns:
        Dictionary of comments with full context and related entity details
    """
    try:
        await ctx.info("Fetching comments")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        # Always apply default page_size to ensure consistent pagination
        if page_size is not None:
            params["page[size]"] = page_size
        else:
            params["page[size]"] = 20
        if project_id is not None:
            params["filter[project_id][]"] = project_id
        if task_id is not None:
            params["filter[task_id]"] = task_id
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_comments(params=params if params else None)
        await ctx.info("Successfully retrieved comments")

        filtered = filter_response(result)

        return filtered

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "comments")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching comments: {str(e)}")
        raise e


async def get_comment(comment_id: int, ctx: Context) -> ToolResult:
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
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"comment {comment_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching comment: {str(e)}")
        raise e


async def get_todos(
    ctx: Context,
    task_id: int = None,
    page_number: int = None,
    page_size: int = 20,
    extra_filters: dict = None
) -> ToolResult:
    """Get all todo checklist items across all tasks and projects.
    
    Args:
        ctx: MCP context for logging and error handling
        task_id: Optional task ID (string) to filter todos by
        page_number: Optional page number for pagination
        page_size: Page size for pagination (default 15, max 200)
        extra_filters: Optional dict of additional Productive API filters
        
    Returns:
        Dictionary of todo checklist items with task context and completion tracking
    """
    try:
        await ctx.info("Fetching todos")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        # Always apply default page_size to ensure consistent pagination
        if page_size is not None:
            params["page[size]"] = page_size
        else:
            params["page[size]"] = 20
        if task_id is not None:
            params["filter[task_id]"] = [task_id]
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_todos(params=params if params else None)
        await ctx.info("Successfully retrieved todos")
        
        filtered = filter_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "todos")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching todos: {str(e)}")
        raise e


async def get_todo(todo_id: int, ctx: Context) -> ToolResult:
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
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"todo {todo_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching todo: {str(e)}")
        raise e


async def get_recent_updates(
    ctx: Context,
    hours: int = 24,
    user_id: int = None,
    project_id: int = None
) -> ToolResult:
    """Get a summarized feed of recent activities and updates.
    
    Perfect for answering questions like "What happened today?" or "What did the team work on?"
    Returns recent changes, updates, and activities in an easy-to-read format.
    
    Args:
        ctx: MCP context for logging and error handling
        hours: Number of hours to look back (default: 24, e.g., 168 for a week)
        user_id: Optional filter by specific user/person ID
        project_id: Optional filter by specific project ID
        
    Returns:
        Dictionary containing recent activities with timestamps and context
        
    Example:
        get_recent_updates(hours=48, project_id=343136)  # Last 2 days on specific project
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate the cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        after_date = cutoff_time.isoformat() + "Z"
        
        await ctx.info(f"Fetching activities from the last {hours} hours")
        
        # Build filter params
        params = {
            "filter[after]": after_date,
            "page[size]": 100  # Get more activities for summary
        }
        
        if user_id:
            params["filter[person_id]"] = user_id
            
        if project_id:
            params["filter[project_id]"] = project_id
        
        result = await client.get_activities(params=params)
        
        if not result.get("data") or len(result["data"]) == 0:
            await ctx.info("No recent activities found")
            return {
                "data": [],
                "meta": {
                    "message": f"No activities found in the last {hours} hours",
                    "hours": hours
                }
            }
        
        filtered = filter_response(result)
        await ctx.info(f"Successfully retrieved {len(result['data'])} recent activities")
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "activities")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching recent updates: {str(e)}")
        raise e