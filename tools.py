from fastmcp import Context
from fastmcp.tools.tool import ToolResult

from productive_client import client, ProductiveAPIError
from utils import filter_response


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
        return ToolResult(structured_content=filtered)

    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning("No projects found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
    except Exception as e:
        await ctx.error(f"Unexpected error fetching projects: {str(e)}")
        
        raise e


async def get_tasks(ctx: Context) -> ToolResult:
    """Get all active tasks across all projects with full assignment details.
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Dictionary containing tasks with assignments, time tracking, and project context
    """
    try:
        await ctx.info("Fetching all tasks")
        result = await client.get_tasks()
        await ctx.info("Successfully retrieved tasks")
        
        filtered = filter_response(result)
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning("No tasks found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
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
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning(f"Task {task_id} not found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
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
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning("No comments found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
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
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning(f"Comment {comment_id} not found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
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
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning("No todos found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
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
        return ToolResult(structured_content=filtered)
        
    except ProductiveAPIError as e:
        await ctx.error(f"Productive API error: {e.message}")
        
        if e.status_code == 404:
            await ctx.warning(f"Todo {todo_id} not found")
        elif e.status_code == 401:
            await ctx.error("Invalid API token - check configuration")
            
        raise e
        
    except Exception as e:
        await ctx.error(f"Unexpected error fetching todo: {str(e)}")
        raise e