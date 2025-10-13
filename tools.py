from fastmcp import Context
from typing import Dict, Any

from productive_client import client, ProductiveAPIError
from utils import filter_response
from yaml_utils import convert_json_to_yaml


async def get_projects(ctx: Context) -> str:
    """Get all active projects with budgets, deadlines, and team assignments.
     
    Returns comprehensive project data including:
    - Project budgets, hourly rates, and cost tracking
    - Team members with roles and hourly rates
    - Deadlines, start/end dates, and project status
    - Client information and contact details
    - Related tasks, comments, and todo-lists
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        All projects with full project details, budgets, and team assignments in YAML format
    """
    try:
        await ctx.info("Fetching all projects")
        result = await client.get_projects()
        
        await ctx.info("Successfully retrieved projects")
        filtered = filter_response(result)
        
        return convert_json_to_yaml(filtered)
    
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


async def get_tasks(ctx: Context) -> str:
    """Get all active tasks across all projects with full assignment details.
    
    Returns comprehensive task data including:
    - Task priorities (low, normal, high, urgent) and statuses
    - Assigned team members with hourly rates and roles
    - Estimated hours vs actual hours tracked
    - Parent project details and client information
    - Due dates, start dates, and completion tracking
    - Related comments, attachments, and todo-lists
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        All tasks with assignments, time tracking, and project context in YAML format
    """
    try:
        await ctx.info("Fetching all tasks")
        result = await client.get_tasks()
        await ctx.info("Successfully retrieved tasks")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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


async def get_task(task_id: str, ctx: Context) -> str:
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
        task_id: The unique Productive task identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Complete task details with project context and all related data in YAML format
    """
    try:
        await ctx.info(f"Fetching task with ID: {task_id}")
        result = await client.get_task(task_id)
        await ctx.info("Successfully retrieved task")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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


async def get_comments(ctx: Context) -> str:
    """Get all comments across projects and tasks with full context.
    
    Returns comprehensive comment data including:
    - Comment text, author, and timestamp
    - Parent entity (project, task, or other) with details
    - Discussion threads and replies
    - Attachments and file references
    - Mentions of team members or clients
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        All comments with full context and related entity details in YAML format
    """
    try:
        await ctx.info("Fetching all comments")
        result = await client.get_comments()
        await ctx.info("Successfully retrieved comments")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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


async def get_comment(comment_id: str, ctx: Context) -> str:
    """Get specific comment details with full context and discussion thread.
    
    Returns detailed comment information including:
    - Complete comment text and formatting
    - Author details and timestamp
    - Parent entity (project, task, etc.) with full context
    - Reply thread and conversation flow
    - Attached files, images, or documents
    - Mentions and references to team members
    
    Args:
        comment_id: The unique Productive comment identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Complete comment details with full context and discussion thread in YAML format
    """
    try:
        await ctx.info(f"Fetching comment with ID: {comment_id}")
        result = await client.get_comment(comment_id)
        await ctx.info("Successfully retrieved comment")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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


async def get_todos(ctx: Context) -> str:
    """Get all todo checklist items across all tasks and projects.
    
    Returns comprehensive todo data including:
    - Checkbox items within tasks for granular tracking
    - Completion status and assignee information
    - Parent task details with project context
    - Due dates and priority relative to parent task
    - Estimated vs actual time for checklist items
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        All todo checklist items with task context and completion tracking in YAML format
    """
    try:
        await ctx.info("Fetching all todos")
        result = await client.get_todos()
        await ctx.info("Successfully retrieved todos")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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


async def get_todo(todo_id: str, ctx: Context) -> str:
    """Get specific todo checklist item details with full task context.
    
    Returns detailed todo information including:
    - Checkbox item text and completion status
    - Parent task with project and client details
    - Assignee and team member information
    - Due date relative to parent task timeline
    - Time estimates vs actual completion time
    - Related comments and file attachments
    
    Args:
        todo_id: The unique Productive todo checklist item identifier
        ctx: MCP context for logging and error handling
        
    Returns:
        Complete todo checklist item with full task context and tracking details in YAML format
    """
    try:
        await ctx.info(f"Fetching todo with ID: {todo_id}")
        result = await client.get_todo(todo_id)
        await ctx.info("Successfully retrieved todo")
        
        filtered = filter_response(result)
        return convert_json_to_yaml(filtered)
        
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