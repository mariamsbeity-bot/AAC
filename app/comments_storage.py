"""In-memory comment storage for the Task Tracker API."""

from datetime import datetime, timezone
from uuid import uuid4

from app.models import CommentCreate, CommentResponse

_comments: dict[str, CommentResponse] = {}


def add_comment(task_id: str, payload: CommentCreate) -> CommentResponse:
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
    comments = [comment for comment in _comments.values() if comment.task_id == task_id]
    return sorted(comments, key=lambda comment: comment.created_at)


def delete_comment(task_id: str, comment_id: str) -> bool:
    comment = _comments.get(comment_id)
    if comment is None or comment.task_id != task_id:
        return False
    _comments.pop(comment_id)
    return True


def _reset_comments() -> None:
    """Clear all comments. For tests only."""
    _comments.clear()
