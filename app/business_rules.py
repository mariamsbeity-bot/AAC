"""Business rules for the Task Tracker API (status-transition validation)."""

from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status transition is allowed.

    Checks the ``(current, new)`` pair against ``VALID_TRANSITIONS``. A
    transition to the same status (``current == new``) is always invalid,
    since no such pair is present in ``VALID_TRANSITIONS``.

    Args:
        current: The task's existing status before the update.
        new: The requested status to transition to.

    Returns:
        None. The function only validates; it does not return a value.

    Raises:
        HTTPException: With status code 422 if ``(current, new)`` is not in
            ``VALID_TRANSITIONS``. The ``detail`` includes the list of
            allowed transitions.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to {new.value}. "
                f"Allowed transitions: {allowed}"
            ),
        )