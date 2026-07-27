# Architecture A: Task Tracker

## 1. What the app does
The Task Tracker is a small FastAPI-based web app for managing tasks in a Kanban-style workflow. It supports creating, listing, updating, deleting, and commenting on tasks, with a simple static HTML/JavaScript frontend that calls the backend over HTTP.

## 2. Data model
The main entity is a Task with fields for id, title, description, status, priority, assignee, due_date, created_at, and updated_at. Tasks also expose a computed due_state derived from the current UTC date and whether the task is done. Comments are a separate entity with id, task_id, text, and created_at. Supported task statuses are ToDo, InProgress, and Done; supported priorities are Low, Medium, and High.

## 3. Request flow
When a user creates a task, the frontend sends a POST request to /tasks. The FastAPI app validates the payload, rejects invalid or unknown fields with 422, and then stores the task in an in-memory dictionary with a generated UUID and UTC timestamps. The created task is returned to the frontend, which updates the visible board state.

## 4. Key files
- [app/main.py](../app/main.py) — API endpoints for tasks, comments, health checks, and HTTP error handling.
- [app/models.py](../app/models.py) — Pydantic models, enums, validation rules, and computed due_state.
- [app/storage.py](../app/storage.py) — In-memory task persistence and task CRUD operations.
- [app/comments_storage.py](../app/comments_storage.py) — In-memory comment persistence and comment-scoped operations.
- [app/business_rules.py](../app/business_rules.py) — Business rules that restrict allowed task status transitions.
- [frontend/index.html](../frontend/index.html) — Static Kanban UI and client-side API calls.
- [tests/test_tasks.py](../tests/test_tasks.py) — Endpoint tests for task creation, update, and deletion flows.
- [tests/test_comments.py](../tests/test_comments.py) — Endpoint tests for comment behavior.
- [README.md](../README.md) — Setup, run, and project overview.
- [requirements.txt](../requirements.txt) — Declared Python dependencies.

## 5. Conventions
Validation is enforced at the model layer: titles and comments are trimmed and must not be blank, invalid enum values and unknown fields are rejected, and status transitions outside the allowed set return 422. Storage is intentionally in-memory only, so data is lost on restart and tests reset the stores between runs. Error handling is mostly explicit: missing tasks/comments return 404 and validation/rule failures return 422. The frontend and backend interact through REST calls, with the frontend using a hardcoded local API base URL.

## 6. Not visible or assumptions
The repository does not show a database, authentication layer, or deployment configuration. The document reflects what is implemented and documented in the current repo, not any unconfirmed production design.
