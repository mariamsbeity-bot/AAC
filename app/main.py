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
    """Create a new task and return it with generated id and timestamps."""
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List all tasks, optionally filtered by status, priority, and overdue state."""
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by id, or 404 if it does not exist."""
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task; status changes must follow allowed transitions."""
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
    """Create a new comment for a task, or return 404 if the task does not exist."""
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return add_comment(task_id, payload)


@app.get(
    "/tasks/{task_id}/comments",
    response_model=list[CommentResponse],
    tags=["comments"],
)
def list_comments(task_id: str) -> list[CommentResponse]:
    """List comments for a task, or return 404 if the task does not exist."""
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return get_comments_by_task(task_id)


@app.delete(
    "/tasks/{task_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["comments"],
)
def delete_task_comment(task_id: str, comment_id: str) -> None:
    """Delete a comment for a task, returning 404 if the task or comment is missing."""
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
    """Delete a task by id and cascade-delete its comments."""
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
    """Simple root message so the base URL is not a 404."""
    return {"message": f"Task Tracker API is running ({APP_ENV})"}