"""In-memory task storage for the Task Tracker API (Module 2)."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task.

    Generates a new id (uuid4 hex) and sets ``created_at``/``updated_at`` to
    the current UTC time. An empty/None ``description`` on the payload is
    stored as ``""``.

    Args:
        payload: Validated task creation data.

    Returns:
        TaskResponse: The newly created task, as stored.
    """
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=uuid4().hex,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered.

    Filters are applied independently and combined with AND: a task must
    match every filter that is not None to be included. The ``overdue``
    filter compares against ``TaskResponse.due_state == "overdue"`` only,
    so ``"completed_late"`` tasks are excluded even when ``overdue=True``.

    Args:
        status: If given, only return tasks with this exact status.
        priority: If given, only return tasks with this exact priority.
        overdue: If given, only return tasks whose computed ``due_state``
            being ``"overdue"`` matches this boolean.

    Returns:
        list[TaskResponse]: Matching tasks, in the underlying dict's
            insertion order (no explicit sort is applied).
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    if overdue is not None:
        tasks = [t for t in tasks if (t.due_state == "overdue") == overdue]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by id.

    Args:
        task_id: The task's id.

    Returns:
        Optional[TaskResponse]: The matching task, or None if no task with
            this id exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` are applied (via
    ``model_dump(exclude_unset=True)``); omitted fields are left
    unchanged. ``updated_at`` is refreshed to the current UTC time
    whenever at least one field changes. This function does not validate
    status transitions itself — that is done by the caller
    (``app.business_rules.validate_status_transition``) before this is
    invoked.

    Args:
        task_id: The id of the task to update.
        payload: Partial update data; unset fields are ignored.

    Returns:
        Optional[TaskResponse]: The updated task, the unchanged existing
            task if ``payload`` had no set fields, or None if no task with
            this id exists.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return existing
    updated = existing.model_copy(
        update={**changes, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        bool: True if a task with this id existed and was removed, False
            if no such task existed.
    """
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    """Clear all tasks. For tests only."""
    _tasks.clear()