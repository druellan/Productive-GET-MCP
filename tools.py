from fastmcp import Context
from typing import Dict, Any

from productive_client import client, ProductiveAPIError
from yaml_utils import convert_json_to_yaml


async def get_projects(ctx: Context) -> str:
    """Get all projects from Productive
     
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Projects data from Productive API in YAML format
    """
    try:
        await ctx.info("Fetching all projects")
        result = await client.get_projects()
        await ctx.info("Successfully retrieved projects")
        
        return convert_json_to_yaml(result)
        
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
    """Get all tasks from Productive
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Tasks data from Productive API in YAML format
    """
    try:
        await ctx.info("Fetching all tasks")
        result = await client.get_tasks()
        await ctx.info("Successfully retrieved tasks")
        
        return convert_json_to_yaml(result)
        
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
    """Get task by ID from Productive
    
    Args:
        task_id: The Productive task ID
        ctx: MCP context for logging and error handling
        
    Returns:
        Task data from Productive API in YAML format
    """
    try:
        await ctx.info(f"Fetching task with ID: {task_id}")
        result = await client.get_task(task_id)
        await ctx.info("Successfully retrieved task")
        
        return convert_json_to_yaml(result)
        
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
    """Get all comments from Productive

    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Comments data from Productive API in YAML format
    """
    try:
        await ctx.info("Fetching all comments")
        result = await client.get_comments()
        await ctx.info("Successfully retrieved comments")
        
        return convert_json_to_yaml(result)
        
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
    """Get comment by ID from Productive
    
    Args:
        comment_id: The Productive comment ID
        ctx: MCP context for logging and error handling
        
    Returns:
        Comment data from Productive API in YAML format
    """
    try:
        await ctx.info(f"Fetching comment with ID: {comment_id}")
        result = await client.get_comment(comment_id)
        await ctx.info("Successfully retrieved comment")
        
        return convert_json_to_yaml(result)
        
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
    """Get all todos from Productive
    
    Args:
        ctx: MCP context for logging and error handling
        
    Returns:
        Todos data from Productive API in YAML format
    """
    try:
        await ctx.info("Fetching all todos")
        result = await client.get_todos()
        await ctx.info("Successfully retrieved todos")
        
        return convert_json_to_yaml(result)
        
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
    """Get todo by ID from Productive
    
    Args:
        todo_id: The Productive todo ID
        ctx: MCP context for logging and error handling
        
    Returns:
        Todo data from Productive API in YAML format
    """
    try:
        await ctx.info(f"Fetching todo with ID: {todo_id}")
        result = await client.get_todo(todo_id)
        await ctx.info("Successfully retrieved todo")
        
        return convert_json_to_yaml(result)
        
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