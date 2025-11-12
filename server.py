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
    try:
        config.validate()
    except ValueError as e:
        raise ValueError(f"Configuration error: {str(e)}")
    
    yield
    
    # Shutdown
    await client.close()

mcp = FastMCP(
    name="Productive MCP Server",
    instructions="Use this tool to access Productive projects, pages, tasks, comments, and todo-lists. Focus on providing accurate and concise information based on the data available in Productive. If a project name or ID is provided, focus on that project. If a task ID is provided, focus on that task.",
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
        int, Field(description="Optional number of tasks per page (max 200)")
    ] = None,
    sort: Annotated[
        str,
        Field(
            description="Sort parameter (e.g., 'last_activity_at', '-last_activity_at', 'created_at', 'due_date'). Use '-' prefix for descending order. Defaults to '-last_activity_at' (most recent first)."
        ),
    ] = "-last_activity_at",
    extra_filters: Annotated[
        dict,
        Field(
            description="Additional Productive query filters using API syntax. Common filters: filter[status][eq] (1: open, 2: closed), filter[project_id][eq] (ID), filter[assignee_id][eq] (ID), filter[due_date][gte] (date)."
        ),
    ] = None,
) -> Dict[str, Any]:
    """Get tasks with optional filtering and pagination.

    Supports Productive's native query-language:
      - Pagination: page_number, page_size (configurable default)
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
    ctx: Context,
    task_id: Annotated[
        int, Field(description="The unique Productive task identifier (internal ID)")
    ],
) -> Dict[str, Any]:
    """Get detailed task information by its internal ID.
    
    Use this when you have the internal task ID (e.g., 14677418).
    For looking up tasks by their project-specific number (e.g., #960), use get_project_task instead.

    Returns task details including:
    - Task title, description, and status (open/closed)
    - Due date, start date, and creation/update timestamps
    - Time tracking: initial estimate, remaining time, billable time, and worked time (in minutes)
    - Todo counts: total and open
    """
    return await tools.get_task(ctx=ctx, task_id=task_id)


@mcp.tool
async def get_project_tasks(
    ctx: Context,
    project_id: Annotated[
        int, Field(description="The project ID to get tasks for")
    ],
    status: Annotated[
        int, Field(description="Optional filter by task status: 1 = open, 2 = closed")
    ] = None,
) -> Dict[str, Any]:
    """Get all tasks for a specific project.
    
    This is optimized for getting a comprehensive view of all tasks in a project.

    Returns a list of all tasks in the project with details including:
    - Task title, number, and status
    - Assignee information
    - Due dates and priority
    - Task descriptions
    - Related project context
    
    Example:
        To get all open tasks in project 343136:
        get_project_tasks(project_id=343136, status=1)
    """
    return await tools.get_project_tasks(
        ctx=ctx,
        project_id=project_id,
        status=status
    )


@mcp.tool
async def get_project_task(
    ctx: Context,
    task_number: Annotated[
        str, Field(description="The task number without # (e.g., '960')")
    ],
    project_id: Annotated[
        int, Field(description="The project ID containing the task")
    ],
) -> Dict[str, Any]:
    """Get a task by its number within a specific project.
    
    This is the preferred way to fetch tasks when you know the task number (e.g., #960)
    that appears in the UI, rather than the internal database ID.

    Task numbers are project-specific, so you must provide both the task_number and project_id.
    For example, task #960 in project 343136.

    Returns comprehensive task details including:
    - Task description, priority, and current status
    - Assigned team member with role and hourly rate
    - Parent project with budget and client details
    - Time tracking: estimated vs actual hours
    - All comments and discussion history
    - Attached files and checklist items (todos)
    """
    return await tools.get_project_task(
        ctx=ctx,
        task_number=task_number,
        project_id=project_id
    )

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
        int, Field(description="Optional number of comments per page (max 200)")
    ] = None,
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

# @mcp.tool
# async def get_comment(
#     ctx: Context,
#     comment_id: Annotated[int, Field(description="Productive comment ID")],
# ) -> Dict[str, Any]:
#     """Get specific comment details with full context and discussion thread.

#     Returns detailed comment information including:
#     - Complete comment text and formatting
#     - Author details and timestamp
#     - Parent entity (project, task, etc.) with full context
#     - Reply thread and conversation flow
#     - Attached files, images, or documents
#     - Mentions and references to team members

#     Args:
#         ctx: MCP context for logging and error handling
#         comment_id: Productive comment ID
#     """
#     return await tools.get_comment(ctx, comment_id)

@mcp.tool
async def get_todos(
    ctx: Context,
    task_id: Annotated[int, Field(description="Productive task ID to filter todos by")] = None,
    page_number: Annotated[int, Field(description="Page number for pagination")] = None,
    page_size: Annotated[int, Field(description="Optional number of todos per page (max 200)")] = None,
    extra_filters: Annotated[dict, Field(description="Additional Productive query filters using API syntax. Common filters: filter[task_id][eq] (ID), filter[status][eq] (1: open, 2: closed), filter[assignee_id][eq] (ID).")] = None
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
    ctx: Context,
    todo_id: Annotated[int, Field(description="Productive todo ID")],
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
        ctx: MCP context for logging and error handling
        todo_id: The Productive todo ID
    """
    return await tools.get_todo(ctx, todo_id)

@mcp.tool
async def get_recent_updates(
    ctx: Context,
    hours: Annotated[
        int, Field(description="Number of hours to look back (default: 24, use 168 for a week)")
    ] = 24,
    user_id: Annotated[
        int, Field(description="Optional: Filter by specific user/person ID")
    ] = None,
    project_id: Annotated[
        int, Field(description="Optional: Filter by specific project ID")
    ] = None,
    activity_type: Annotated[
        int, Field(description="Optional: Filter by activity type (1: Comment, 2: Changeset, 3: Email)")
    ] = None,
    item_type: Annotated[
        str, Field(description="Optional: Filter by item type. Accepted values include: Workspace, Task, Page, Deal, Project, Person, Discussion, Invoice, TimeEntry, Section, TaskList, Pipeline, Dashboard, Team. Note: This list is not exhaustive; see Productive Activities docs for latest values.")
    ] = None,
    event_type: Annotated[
        str, Field(description="Optional: Filter by event type. Common values include: create, copy, edit, delete. Note: The full set isn't fixed and may evolve; see Productive Activities docs for current list.")
    ] = None,
    task_id: Annotated[
        int, Field(description="Optional: Filter by specific task ID")
    ] = None,
    max_results: Annotated[
        int, Field(description="Optional maximum number of activities to return (max: 200)")
    ] = None,
) -> Dict[str, Any]:
    """Get a summarized feed of recent activities and updates.

    Returns recent changes, task updates, comments, and activities in chronological order.

    Perfect for status updates and answering questions like:
    - "What happened today?"
    - "What did the team work on this week?"
    - "Show me recent updates on project X"
    - "What did John do yesterday?"

    Examples:
        get_recent_updates()  # Last 24 hours, all activity
        get_recent_updates(hours=168)  # Last week
        get_recent_updates(hours=48, project_id=343136)  # Last 2 days on specific project
        get_recent_updates(hours=24, user_id=12345)  # What a specific user did today
        get_recent_updates(hours=24, activity_type=1)  # Only comments from last day
        get_recent_updates(hours=168, item_type='Task')  # Task activities from last week
    """
    return await tools.get_recent_updates(
        ctx,
        hours=hours,
        user_id=user_id,
        project_id=project_id,
        activity_type=activity_type,
        item_type=item_type,
        event_type=event_type,
        task_id=task_id,
        max_results=max_results
    )


@mcp.tool
async def get_pages(
    ctx: Context,
    project_id: Annotated[
        int, Field(description="Optional project ID to filter pages by")
    ] = None,
    creator_id: Annotated[
        int, Field(description="Optional creator ID to filter pages by")
    ] = None,
    page_number: Annotated[int, Field(description="Page number for pagination")] = None,
    page_size: Annotated[
        int, Field(description="Optional number of pages per page (max 200)")
    ] = None,
) -> Dict[str, Any]:
    """Get all pages/documents with optional filtering.
    
    Pages in Productive are documents that can contain rich text content,
    attachments, and are organized within projects.
    
    Args:
        ctx: MCP context for logging and error handling
        project_id: Optional project ID to filter pages by
        creator_id: Optional creator ID to filter pages by
        page_number: Optional page number for pagination
        page_size: Page size for pagination (max 200)
        
    Returns:
        Dictionary containing pages with content, metadata, and relationships
        
    Example:
        get_pages(project_id=1234)  # Get all pages for a specific project
    """
    return await tools.get_pages(
        ctx,
        project_id=project_id,
        creator_id=creator_id,
        page_number=page_number,
        page_size=page_size
    )


@mcp.tool
async def get_page(
    page_id: Annotated[int, Field(description="The unique Productive page identifier")],
    ctx: Context,
) -> Dict[str, Any]:
    """Get specific page/document details with full content.
    
    Args:
        page_id: The unique Productive page identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary with complete page details including JSON-formatted content
    """
    return await tools.get_page(page_id, ctx)


@mcp.tool
async def get_attachments(
    ctx: Context,
    page_number: Annotated[int, Field(description="Page number for pagination")] = None,
    page_size: Annotated[
        int, Field(description="Optional number of attachments per page (max 200)")
    ] = None,
    extra_filters: Annotated[
        dict,
        Field(description="Additional Productive query filters using API syntax")
    ] = None,
) -> Dict[str, Any]:
    """Get all attachments/files with optional filtering.
    
    Attachments are files (PDFs, images, documents) that can be associated with
    various Productive entities like tasks, comments, expenses, etc.
    
    Args:
        ctx: MCP context for logging and error handling
        page_number: Optional page number for pagination
        page_size: Page size for pagination (max 200)
        extra_filters: Optional dict of additional filter query params
        
    Returns:
        Dictionary containing attachment metadata (name, type, size, relationships)
        Note: This provides metadata only, not actual file content
    """
    return await tools.get_attachments(
        ctx,
        page_number=page_number,
        page_size=page_size,
        extra_filters=extra_filters
    )


# @mcp.tool
# async def get_attachment(
#     attachment_id: Annotated[int, Field(description="The unique Productive attachment identifier")],
#     ctx: Context,
# ) -> Dict[str, Any]:
#     """Get specific attachment/file details.

#     Args:
#         attachment_id: The unique Productive attachment identifier
#         ctx: MCP context for logging and error handling
        
#     Returns:
#         Dictionary with complete attachment metadata including:
#         - File name, type, size
#         - Associated entity (task, comment, etc.)
#         - Upload metadata
        
#     Note:
#         This provides metadata only, not actual file content
#     """
#     return await tools.get_attachment(attachment_id, ctx)


if __name__ == "__main__":
    mcp.run()