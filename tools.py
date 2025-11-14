from fastmcp import Context
from fastmcp.tools.tool import ToolResult

from config import config
from productive_client import client, ProductiveAPIError
from utils import filter_response, filter_task_list_response, filter_page_list_response


async def _handle_productive_api_error(ctx: Context, e: ProductiveAPIError, resource_type: str = "data") -> None:
    """Handle ProductiveAPIError consistently across all tool functions.
    
    Developer notes:
    - ctx: MCP context for logging and error handling
    - e: The ProductiveAPIError exception
    - resource_type: Type of resource being fetched (e.g., "projects", "tasks", "comments")
    """
    await ctx.error(f"Productive API error: {e.message}")
    
    if e.status_code == 404:
        await ctx.warning(f"No {resource_type} found")
    elif e.status_code == 401:
        await ctx.error("Invalid API token - check configuration")
    
    raise e


async def get_projects(ctx: Context) -> ToolResult:
    """Fetch projects and post-process response for LLM safety.

    Developer notes:
    - Wraps client.get_projects(); sorts by most recent activity first.
    - Applies utils.filter_response to strip noise and add webapp_url.
    - Raises ProductiveAPIError on API failure; errors are logged via ctx.
    """
    try:
        await ctx.info("Fetching all projects")
        params = {"sort": "-last_activity_at"}
        result = await client.get_projects(params=params)
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
    page_size: int = config.items_per_page,
    sort: str = "-last_activity_at",
    extra_filters: dict = None
) -> ToolResult:
    """List tasks with optional filters and pagination.

    Developer notes:
    - extra_filters is passed through directly to the API (e.g., filter[status][eq]).
    - Enforces a configurable default page[size] for consistency when not provided.
    - Sort supports Productive's allowed fields (e.g., last_activity_at, created_at, due_date).
    - Response is cleaned with utils.filter_task_list_response (excludes descriptions for lean lists).
    """
    try:
        await ctx.info("Fetching tasks")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        params["page[size]"] = page_size
        if project_id is not None:
            params["filter[project_id][eq]"] = project_id
        if sort:
            params["sort"] = sort
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_tasks(params=params if params else None)
        await ctx.info("Successfully retrieved tasks")

        filtered = filter_task_list_response(result)

        return filtered

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "tasks")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching tasks: {str(e)}")
        raise e


async def get_task(ctx: Context, task_id: int) -> ToolResult:
    """Fetch a single task by internal ID.

    Developer notes:
    - Wraps client.get_task(task_id).
    - Applies utils.filter_response to sanitize output.
    - Raises ProductiveAPIError on failure.
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
    """List tasks for a project with an optional status filter.

    Developer notes:
    - status expects integers per Productive: 1=open, 2=closed (mapped to filter[status][eq]).
    - Sorts by most recent activity first.
    - Uses configurable page[size] for consistency.
    - Applies utils.filter_task_list_response (lighter payload than filter_response).
    - On 404/empty, returns an empty data array with an informational meta message.
    """
    try:
        await ctx.info(f"Fetching all tasks for project {project_id}")
        
        # Get all tasks for the project with a high limit
        params = {
            "filter[project_id][eq]": project_id,
            "page[size]": config.items_per_page  # Configurable limit for comprehensive view
        }
        
        # Status filter: 1 = open, 2 = closed (per Productive API docs)
        if status is not None:
            params["filter[status][eq]"] = status
        
        params["sort"] = "-last_activity_at"
        
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
    """Fetch a task by its project-scoped task_number.

    Developer notes:
    - Uses filter[project_id][eq] and filter[task_number][eq].
    - Returns the first matched record (API constrained to one).
    - Raises ProductiveAPIError(404) if not found.
    """
    try:
        await ctx.info(f"Fetching task #{task_number} from project {project_id}")
        
        # Get tasks for the project filtered by task_number
        params = {
            "filter[project_id][eq]": project_id,
            "filter[task_number][eq]": task_number
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
    page_size: int = config.items_per_page,
    extra_filters: dict = None
) -> ToolResult:
    """List comments with optional filters and pagination.

    Developer notes:
    - Pass-through for extra_filters (e.g., discussion_id, page_id, task_id).
    - Enforces configurable default page[size] if not provided.
    - Sort defaults to "-created_at" (most recent first).
    - Applies utils.filter_response to sanitize.
    - Uses consistent scalar filters: filter[project_id][eq], filter[task_id][eq]
    """
    try:
        await ctx.info("Fetching comments")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        params["page[size]"] = page_size
        if project_id is not None:
            params["filter[project_id][eq]"] = project_id
        if task_id is not None:
            params["filter[task_id][eq]"] = task_id
        if extra_filters:
            params.update(extra_filters)

        # Add default sorting
        params["sort"] = "-created_at"

        result = await client.get_comments(params=params if params else None)
        await ctx.info("Successfully retrieved comments")

        filtered = filter_response(result)

        return filtered

    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "comments")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching comments: {str(e)}")
        raise e


async def get_comment(ctx: Context, comment_id: int) -> ToolResult:
    """Fetch a single comment by ID and sanitize the response."""
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
    page_size: int = config.items_per_page,
    extra_filters: dict = None
) -> ToolResult:
    """List todo checklist items with optional filters.

    Developer notes:
    - task_id is an int; API expects filter[task_id] to be array or scalar; we send scalar.
    - Enforces configurable default page[size] when not provided.
    - Use extra_filters for status ints (1=open, 2=closed) or assignee filters.
    - Sorting not supported by API - uses default order.
    - Applies utils.filter_response.
    """
    try:
        await ctx.info("Fetching todos")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        params["page[size]"] = page_size
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


async def get_todo(ctx: Context, todo_id: int) -> ToolResult:
    """Fetch a single todo by ID and sanitize the response."""
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


async def get_recent_activity(
    ctx: Context,
    hours: int = 24,
    user_id: int = None,
    project_id: int = None,
    activity_type: int = None,
    item_type: str = None,
    event_type: str = None,
    task_id: int = None,
    max_results: int = None
) -> ToolResult:
    """Summarize recent activities within a time window.

    Developer notes:
    - Builds filter[after] from UTC now minus `hours`.
    - Optional filters map directly: person_id, project_id, type (1:Comment,2:Changeset,3:Email), item_type, event, task_id.
    - Respects API page[size] limit (<=200) via max_results.
    - Response is sanitized and meta is enriched with basic counts via _summarize_activities.
    - Avoids unsupported sorts on /activities.
    """
    try:
        from datetime import datetime, timedelta

        if max_results is None:
            max_results = config.items_per_page

        # Validate max_results
        if max_results > 200:
            await ctx.warning("max_results exceeds API limit of 200, using 200")
            max_results = 200
        
        # Calculate the cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        after_date = cutoff_time.isoformat() + "Z"
        
        await ctx.info(f"Fetching activities from the last {hours} hours")
        
        # Build comprehensive filter params
        params = {
            "filter[after]": after_date,
            "page[size]": max_results
        }
        
        # Apply optional filters
        if user_id:
            params["filter[person_id]"] = user_id
            
        if project_id:
            params["filter[project_id]"] = project_id
            
        if activity_type:
            params["filter[type]"] = activity_type
            
        if item_type:
            params["filter[item_type]"] = item_type
            
        if event_type:
            params["filter[event]"] = event_type
            
        if task_id:
            params["filter[task_id]"] = task_id
        
        result = await client.get_activities(params=params)
        
        if not result.get("data") or len(result["data"]) == 0:
            await ctx.info("No recent activities found")
            return {
                "data": [],
                "meta": {
                    "message": f"No activities found in the last {hours} hours",
                    "hours": hours,
                    "filters_applied": _get_applied_filters(params),
                    "cutoff_time": after_date
                }
            }
        
        filtered = filter_response(result)
        
        # Enhance metadata with activity summary
        activity_summary = _summarize_activities(filtered.get("data", []))
        filtered["meta"] = filtered.get("meta", {})
        filtered["meta"].update({
            "activity_summary": activity_summary,
            "total_activities": len(filtered.get("data", [])),
            "filters_applied": _get_applied_filters(params),
            "cutoff_time": after_date
        })
        
        await ctx.info(f"Successfully retrieved {len(result['data'])} recent activities")
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "activities")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching recent updates: {str(e)}")
        raise e


def _get_applied_filters(params: dict) -> dict:
    """Extract and format the filters that were actually applied."""
    applied_filters = {}
    
    # Remove pagination and standard params
    filter_params = {k: v for k, v in params.items() if k.startswith("filter[")}
    
    for key, value in filter_params.items():
        # Extract filter name from key like "filter[person_id]"
        filter_name = key.replace("filter[", "").replace("]", "")
        applied_filters[filter_name] = value
    
    return applied_filters


def _summarize_activities(activities: list) -> dict:
    """Create a summary of activities by type and event."""
    summary = {
        "by_type": {},
        "by_event": {},
        "by_item_type": {},
        "total": len(activities)
    }
    
    for activity in activities:
        if not isinstance(activity, dict):
            continue
            
        attributes = activity.get("attributes", {})
        activity_type = attributes.get("type")
        event_type = attributes.get("event")
        item_type = attributes.get("item_type")
        
        # Count by activity type
        if activity_type:
            summary["by_type"][activity_type] = summary["by_type"].get(activity_type, 0) + 1
            
        # Count by event type
        if event_type:
            summary["by_event"][event_type] = summary["by_event"].get(event_type, 0) + 1
            
        # Count by item type
        if item_type:
            summary["by_item_type"][item_type] = summary["by_item_type"].get(item_type, 0) + 1
    
    return summary


async def get_pages(
    ctx: Context,
    project_id: int = None,
    creator_id: int = None,
    page_number: int = None,
    page_size: int = config.items_per_page
) -> ToolResult:
    """List pages (docs) with optional filters and pagination.

    Developer notes:
    - Supports project_id and creator_id filters.
    - Enforces configurable default page[size] if not provided.
    - Sorts by most recent updates first.
    - Applies utils.filter_response to sanitize (body excluded via type='pages').
    - Uses consistent scalar filters: filter[project_id][eq], filter[creator_id][eq]
    """
    try:
        await ctx.info("Fetching pages")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        params["page[size]"] = page_size
        if project_id is not None:
            params["filter[project_id][eq]"] = project_id
        if creator_id is not None:
            params["filter[creator_id][eq]"] = creator_id
        params["sort"] = "-updated_at"
        result = await client.get_pages(params=params if params else None)
        await ctx.info("Successfully retrieved pages")
        
        # For lists, remove heavy fields like body explicitly
        filtered = filter_page_list_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "pages")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching pages: {str(e)}")
        raise e


async def get_page(ctx: Context, page_id: int) -> ToolResult:
    """Fetch a single page by ID.

    Developer notes:
    - Body is JSON in attributes.body (caller may parse if needed).
    - Applies utils.filter_response to sanitize (body included via type='page').
    """
    try:
        await ctx.info(f"Fetching page with ID: {page_id}")
        result = await client.get_page(page_id)
        await ctx.info("Successfully retrieved page")
        
        filtered = filter_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"page {page_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching page: {str(e)}")
        raise e


async def get_attachments(
    ctx: Context,
    page_number: int = None,
    page_size: int = config.items_per_page,
    extra_filters: dict = None
) -> ToolResult:
    """List attachments with optional filters and pagination (metadata only).

    Developer notes:
    - Enforces configurable default page[size] when not provided.
    - Sorting not supported by API - uses default order.
    """
    try:
        await ctx.info("Fetching attachments")
        params = {}
        if page_number is not None:
            params["page[number]"] = page_number
        params["page[size]"] = page_size
        if extra_filters:
            params.update(extra_filters)

        result = await client.get_attachments(params=params if params else None)
        await ctx.info("Successfully retrieved attachments")
        
        filtered = filter_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "attachments")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching attachments: {str(e)}")
        raise e


async def get_attachment(ctx: Context, attachment_id: int) -> ToolResult:
    """Fetch a single attachment by ID (metadata only)."""
    try:
        await ctx.info(f"Fetching attachment with ID: {attachment_id}")
        result = await client.get_attachment(attachment_id)
        await ctx.info("Successfully retrieved attachment")
        
        filtered = filter_response(result)
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, f"attachment {attachment_id}")
    except Exception as e:
        await ctx.error(f"Unexpected error fetching attachment: {str(e)}")


async def search_recent_entries(ctx: Context, query: str) -> ToolResult:
    """Search through recent entries across all Productive content types.

    Searches through the last 90 days of Productive activities and entries (tasks, pages,
    projects, comments, discussions, etc.) to find matches for your query. This provides
    a universal search across all content types without needing to search individual resources.

    Args:
        query: The search term to look for (case-insensitive)

    Returns:
        Recent entries containing the search term in titles, descriptions, comments,
        or any other text content from recent project activity
    """
    try:
        from datetime import datetime, timedelta
        
        if not query or not query.strip():
            return {
                "data": [],
                "meta": {
                    "message": "Empty search query provided",
                    "query": query,
                    "total_matches": 0
                }
            }
        
        # Search last 90 days (2160 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=2160)
        after_date = cutoff_time.isoformat() + "Z"
        
        await ctx.info(f"Searching 200 activities for '{query}' in the last 90 days")
        
        # Fetch all recent activities using the existing client method
        params = {
            "filter[after]": after_date,
            "page[size]": 200  # Maximum allowed by API
        }
        
        result = await client.get_activities(params=params)
        
        if not result.get("data") or len(result["data"]) == 0:
            await ctx.info("No activities found in the last 60 days")
            return {
                "data": [],
                "meta": {
                    "message": "No activities found in the last 60 days",
                    "query": query,
                    "total_matches": 0,
                    "cutoff_time": after_date
                }
            }
        
        # Prepare search query (case-insensitive)
        search_term = query.lower().strip()
        
        # Search through activities across all text fields
        matches = []
        searchable_fields = ["title", "body", "item_name", "person_name", "project_name"]
        
        for activity in result["data"]:
            if not isinstance(activity, dict):
                continue
                
            attributes = activity.get("attributes", {})
            
            # Check all searchable text fields
            for field in searchable_fields:
                field_value = attributes.get(field, "")
                if isinstance(field_value, str) and field_value:
                    if search_term in field_value.lower():
                        matches.append(activity)
                        break  # Found match, no need to check other fields
        
        # Filter the response
        filtered = filter_response({"data": matches})
        
        # Enhance metadata with search results
        search_metadata = {
            "query": query,
            "total_matches": len(matches),
            "total_searched": len(result["data"]),
            "cutoff_time": after_date,
            "search_fields": searchable_fields
        }
        
        filtered["meta"] = filtered.get("meta", {})
        filtered["meta"].update(search_metadata)
        
        await ctx.info(f"Search completed: {len(matches)} matches found out of {len(result['data'])} activities")
        
        return filtered
        
    except ProductiveAPIError as e:
        await _handle_productive_api_error(ctx, e, "activities for search")
    except Exception as e:
        await ctx.error(f"Unexpected error during search: {str(e)}")
        raise e
        raise e