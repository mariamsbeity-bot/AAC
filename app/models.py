"""Pydantic v2 models and enums for the Task Tracker API (Module 2)."""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Normalize and validate the task title.

        Strips leading/trailing whitespace, then rejects blank or overly
        long titles.

        Args:
            value: The raw title string from the request payload.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty, or longer than 200
                characters. Pydantic converts this into a 422 response.
        """
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        if len(value) > 200:
            raise ValueError("title must be at most 200 characters")
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        """Normalize and validate the task title, if provided.

        None is passed through unchanged, which allows a PATCH payload to
        omit ``title`` without triggering validation. Otherwise, strips
        leading/trailing whitespace and rejects blank or overly long
        titles.

        Args:
            value: The raw title string from the request payload, or None
                if the field was not supplied.

        Returns:
            Optional[str]: None if not supplied, otherwise the stripped
                title.

        Raises:
            ValueError: If a supplied title is blank after stripping, or
                longer than 200 characters. Pydantic converts this into a
                422 response.
        """
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        if len(value) > 200:
            raise ValueError("title must be at most 200 characters")
        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    def due_state(self) -> Optional[str]:
        """Derive the task's overdue state; not a stored field.

        Computed fresh on every access/serialization against the current
        UTC date, so the same stored task can report a different
        ``due_state`` across two calls made on different days.

        Returns:
            Optional[str]: None if there is no due date or the due date is
                today or in the future; ``"overdue"`` if the due date is
                in the past and status is not Done; ``"completed_late"``
                if the due date is in the past and status is Done.
        """
        if self.due_date is None:
            return None
        utc_today = datetime.now(timezone.utc).date()
        if self.due_date < utc_today:
            return "completed_late" if self.status == TaskStatus.DONE else "overdue"
        return None


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """Normalize and validate comment text.

        Strips leading/trailing whitespace and rejects a blank result.

        Args:
            value: The raw comment text from the request payload.

        Returns:
            str: The stripped comment text.

        Raises:
            ValueError: If the stripped text is empty. Pydantic converts
                this into a 422 response.
        """
        value = value.strip()
        if not value:
            raise ValueError("text must not be blank")
        return value


class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    text: str
    created_at: datetime