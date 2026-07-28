# Architecture B: Task Tracker

## 1. What the app does
The Task Tracker is a small learning-project web app that combines a FastAPI backend with a static vanilla-JavaScript Kanban frontend for managing tasks and task-scoped comments.

## 2. Data model
The main entity is a Task with fields such as id, title, description, status, priority, assignee, due_date, created_at, and updated_at. The app also supports Comments as a separate entity with id, task_id, text, and created_at. Task statuses are ToDo, InProgress, and Done, and priorities are Low, Medium, and High.

## 3. Request flow
When a user creates a task, the frontend sends a POST request to /tasks. The FastAPI app validates the payload, applies the task creation defaults, generates an id and UTC timestamps, and stores the task in memory. The created task is then returned to the client for display in the board.

## 4. Key files
- [app/main.py](../app/main.py) — Defines the FastAPI routes for tasks, comments, health, and local CORS behavior.
- [app/models.py](../app/models.py) — Defines the Pydantic models, enums, validation rules, and computed due_state.
- [app/storage.py](../app/storage.py) — Holds task data in memory and implements task CRUD behavior.
- [app/comments_storage.py](../app/comments_storage.py) — Holds comments in memory and implements comment-scoped operations.
- [app/business_rules.py](../app/business_rules.py) — Enforces the allowed task status transitions.
- [frontend/index.html](../frontend/index.html) — Provides the static Kanban UI and calls the backend API.
- [tests/test_tasks.py](../tests/test_tasks.py) — Verifies task endpoint behavior.
- [tests/test_comments.py](../tests/test_comments.py) — Verifies comment endpoint behavior.
- [README.md](../README.md) — Documents setup, run steps, and project scope.
- [requirements.txt](../requirements.txt) — Declares backend dependencies.

## 5. Conventions
Validation is handled by the request models: titles and comments are trimmed and must not be blank, unknown fields are rejected, and invalid enum values fail validation. Storage is intentionally in-memory only, so data is not persisted across restarts. Error handling is explicit for missing tasks or comments (404) and invalid requests or rule violations (422). The frontend and backend communicate over HTTP with the frontend using a hardcoded local API base URL.

## 6. Not visible or assumptions
The repository does not show a database, authentication layer, or deployment configuration, so those are not described as implemented. The document stays limited to what is supported by the provided context and inspected files.
