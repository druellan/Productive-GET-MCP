from fastmcp import FastMCP, Context
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
async def get_projects(ctx: Context) -> str:
    """Get all projects from Productive
    
    Returns:
        List of projects with their details in JSON format
    """
    return await tools.get_projects(ctx)

@mcp.tool
async def get_tasks(ctx: Context) -> str:
    """Get all tasks from Productive
    
    Returns:
        List of tasks with their details in JSON format
    """
    return await tools.get_tasks(ctx)

@mcp.tool
async def get_task(task_id: str, ctx: Context) -> str:
    """Get a specific task by ID from Productive
    
    Args:
        task_id: The Productive task ID
        
    Returns:
        Task details in JSON format
    """
    return await tools.get_task(task_id, ctx)

@mcp.tool
async def get_comments(ctx: Context) -> str:
    """Get all comments from Productive
    
    Returns:
        List of comments with their details in JSON format
    """
    return await tools.get_comments(ctx)

@mcp.tool
async def get_comment(comment_id: str, ctx: Context) -> str:
    """Get a specific comment by ID from Productive
    
    Args:
        comment_id: The Productive comment ID
        
    Returns:
        Comment details in JSON format
    """
    return await tools.get_comment(comment_id, ctx)

@mcp.tool
async def get_todos(ctx: Context) -> str:
    """Get all todos from Productive
    
    Returns:
        List of todos with their details in JSON format
    """
    return await tools.get_todos(ctx)

@mcp.tool
async def get_todo(todo_id: str, ctx: Context) -> str:
    """Get a specific todo by ID from Productive
    
    Args:
        todo_id: The Productive todo ID
        
    Returns:
        Todo details in JSON format
    """
    return await tools.get_todo(todo_id, ctx)

if __name__ == "__main__":
    mcp.run()