"""Application entry point: creates the FastAPI instance and wires up routes."""

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import APP_ENV

from app.models import (
    CommentCreate,
    CommentResponse,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskCreate,
    TaskUpdate,
)
from app import storage
from app.comments_storage import add_comment, delete_comment, get_comments_by_task

from app.business_rules import validate_status_transition


app = FastAPI(
    title="Task Tracker API",
    description="Module 1 learning project: FastAPI + JSON file storage.",
    version="0.1.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Route:
        POST /tasks

    Args:
        payload: Task fields from the request body. Unknown fields are
            rejected (422) since ``TaskCreate`` uses ``extra="forbid"``.

    Returns:
        TaskResponse: The created task (201), including generated ``id``,
            ``created_at``, and ``updated_at``.
    """
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered.

    Route:
        GET /tasks

    Args:
        status: Optional query parameter; if given, only tasks with this
            exact status are returned.
        priority: Optional query parameter; if given, only tasks with this
            exact priority are returned.
        overdue: Optional query parameter; if given, only tasks whose
            computed ``due_state == "overdue"`` matches this boolean.
            Note this excludes ``"completed_late"`` tasks even when
            ``overdue=True``.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters
            (AND-combined).
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by id.

    Route:
        GET /tasks/{task_id}

    Args:
        task_id: The task's id, from the URL path.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Route:
        PATCH /tasks/{task_id}

    Only fields explicitly set in ``payload`` are changed; omitted fields
    are left as-is. If ``status`` is included, it is checked against
    ``app.business_rules.validate_status_transition`` before the update is
    applied (this requires an extra existence lookup, in addition to the
    one performed inside ``storage.update_task``).

    Args:
        task_id: The task's id, from the URL path.
        payload: Partial update fields. Unknown fields are rejected (422)
            since ``TaskUpdate`` uses ``extra="forbid"``.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists. 422 (via
            ``validate_status_transition``) if ``payload.status`` is set
            and is not a valid transition from the task's current status.
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {task_id} not found",
            )
        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["comments"],
)
def create_comment(task_id: str, payload: CommentCreate) -> CommentResponse:
    """Add a comment to a task.

    Route:
        POST /tasks/{task_id}/comments

    Args:
        task_id: The id of the task to attach the comment to, from the
            URL path.
        payload: Comment fields from the request body. Unknown fields are
            rejected (422) since ``CommentCreate`` uses ``extra="forbid"``.

    Returns:
        CommentResponse: The created comment (201).

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return add_comment(task_id, payload)


@app.get(
    "/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
    tags=["comments"],
)
def list_comments(task_id: str) -> list[CommentResponse]:
    """List all comments for a task.

    Route:
        GET /tasks/{task_id}/comments

    Args:
        task_id: The task's id, from the URL path.

    Returns:
        list[CommentResponse]: The task's comments, oldest first.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return get_comments_by_task(task_id)


@app.delete(
    "/tasks/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
)
def delete_task_comment(task_id: str, comment_id: str) -> None:
    """Delete a single comment from a task.

    Route:
        DELETE /tasks/{task_id}/comments/{comment_id}

    Args:
        task_id: The task's id, from the URL path.
        comment_id: The comment's id, from the URL path.

    Returns:
        None. Responds 204 No Content on success.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists. 404 if no
            comment with ``comment_id`` exists that belongs to
            ``task_id``.
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    deleted = delete_comment(task_id, comment_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Comment with id {comment_id} not found",
        )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task and cascade-delete its comments.

    Route:
        DELETE /tasks/{task_id}

    Comments are fetched and deleted individually before the task itself
    is removed. If ``task_id`` does not exist, comment lookup simply
    returns an empty list (no-op), and the 404 below is raised without
    side effects.

    Args:
        task_id: The task's id, from the URL path.

    Returns:
        None. Responds 204 No Content on success.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    comments = get_comments_by_task(task_id)
    for comment in comments:
        delete_comment(task_id, comment.id)

    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

@app.get("/", include_in_schema=False)
def root() -> dict:
    """Root endpoint, excluded from the OpenAPI schema.

    Route:
        GET /

    Returns:
        dict: A single ``message`` key confirming the API is running and
            naming the current ``APP_ENV``.
    """
    return {"message": f"Task Tracker API is running ({APP_ENV})"}