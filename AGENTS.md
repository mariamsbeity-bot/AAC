# AGENTS.md

## Project summary

Task Tracker is a learning-project REST API with a small vanilla-JavaScript Kanban frontend.

The current implementation provides task CRUD endpoints, task filtering, priority and status handling, and in-memory storage. It does not persist tasks across server restarts. See `app/main.py`, `app/models.py`, and `app/storage.py`.

## Tech stack and supported commands

- Python 3.11+ is documented in `README.md`.
- FastAPI, Pydantic v2, Uvicorn, and python-dotenv are declared in `requirements.txt`.
- The backend is a FastAPI application at `app.main:app`.
- The frontend is a single static file at `frontend/index.html`, with inline CSS and JavaScript.
- Tests use `pytest` and FastAPI's `TestClient`; pytest is not listed in `requirements.txt`.

Setup and run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Supported endpoints include:

- App: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

Test command used by the repository test suite:

```bash
pytest -v
```

Whether `pytest` is installed by `pip install -r requirements.txt` is not confirmed; it is not declared in that file.

## Current architecture

- `app/main.py` defines the task routes and local-development CORS configuration.
- `app/models.py` defines Pydantic request/response models and task enums.
- `app/business_rules.py` enforces allowed task-status transitions.
- `app/storage.py` keeps tasks in an in-memory dictionary and supplies test-only reset support.
- `tests/` exercises API behavior through `TestClient`; the autouse fixture resets storage between tests.
- `frontend/index.html` calls `http://localhost:8000` and renders the three task-status columns.

## Visible business rules

Task statuses (`app/models.py`):

- `ToDo`
- `InProgress`
- `Done`

Allowed status transitions (`app/business_rules.py`):

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`

All other transitions, including a transition to the same status, return HTTP 422.

Task priorities:

- `Low`
- `Medium`
- `High`

Task creation defaults:

- Status: `ToDo`
- Priority: `Medium`
- Description: empty string
- Assignee: `null`

Validation rules:

- A title is required, trimmed, must not be blank, and must be at most 200 characters.
- Unknown fields are rejected for task-create and task-update payloads.
- Invalid status or priority enum values are rejected.
- `GET /tasks` can filter by status and/or priority.
- Missing task IDs return HTTP 404 for get, update, and delete operations.
- Task IDs are generated UUID4 hex values; timestamps are generated in UTC.
- Tasks are held only in memory and are lost when the server restarts.

Due dates, comments, authentication, database persistence, and deployment configuration are not confirmed by the inspected implementation.

## Module 5 guardrails

- Work docs-first: read `README.md`, this file, relevant source files, and relevant tests before making recommendations or changes.
- Default to read-only investigation and reporting.
- Keep one clearly scoped task per Codex task/thread.
- Do not modify anything under `app/` unless the user explicitly approves that application change.
- Do not broaden scope from documentation or analysis into implementation without explicit approval.
- Treat the current in-memory storage design as intentional unless the user asks to change it.

## Security and governance

- Never paste, log, commit, or expose secrets, tokens, passwords, `.env` contents, or private data.
- Do not run destructive commands or irreversible Git operations without explicit user approval.
- Cite the relevant repository files when reporting findings or proposing changes.
- Do not claim behavior that is not visible in code, tests, or documentation. Mark it as "not confirmed."
- Preserve unrelated user changes in a dirty working tree.
