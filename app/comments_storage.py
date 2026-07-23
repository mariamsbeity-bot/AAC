"""In-memory comment storage for the Task Tracker API."""

from datetime import datetime, timezone
from uuid import uuid4

from app.models import CommentCreate, CommentResponse

_comments: dict[str, CommentResponse] = {}


def add_comment(task_id: str, payload: CommentCreate) -> CommentResponse:
    """Create and persist a new comment on a task.

    Generates a new id (uuid4 hex) and sets ``created_at`` to the current
    UTC time. Does not itself verify that ``task_id`` refers to an
    existing task — that check is performed by the caller in
    ``app.main.create_comment`` before this is invoked. [VERIFY] if a new
    call site is ever added that skips that existence check first.

    Args:
        task_id: The id of the task this comment belongs to.
        payload: Validated comment creation data.

    Returns:
        CommentResponse: The newly created comment, as stored.
    """
    now = datetime.now(timezone.utc)
    comment = CommentResponse(
        id=uuid4().hex,
        task_id=task_id,
        text=payload.text,
        created_at=now,
    )
    _comments[comment.id] = comment
    return comment


def get_comments_by_task(task_id: str) -> list[CommentResponse]:
    """Return all comments for a task, oldest first.

    Args:
        task_id: The id of the task to fetch comments for.

    Returns:
        list[CommentResponse]: Comments belonging to ``task_id``, sorted
            ascending by ``created_at``. Empty list if the task has no
            comments (or does not exist — this function does not check
            task existence).
    """
    comments = [comment for comment in _comments.values() if comment.task_id == task_id]
    return sorted(comments, key=lambda comment: comment.created_at)


def delete_comment(task_id: str, comment_id: str) -> bool:
    """Delete a comment, scoped to its parent task.

    Args:
        task_id: The id of the task the comment is expected to belong to.
        comment_id: The id of the comment to delete.

    Returns:
        bool: True if a comment with ``comment_id`` existed, belonged to
            ``task_id``, and was removed. False if no such comment exists,
            or it exists but belongs to a different task (in which case it
            is not deleted).
    """
    comment = _comments.get(comment_id)
    if comment is None or comment.task_id != task_id:
        return False
    _comments.pop(comment_id)
    return True


def _reset_comments() -> None:
    """Clear all comments. For tests only."""
    _comments.clear()
