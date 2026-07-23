# Task Tracker API

This repository contains a small FastAPI-based task tracker with a static HTML frontend and supporting midcourse documentation for the submission.

## What is included

- A FastAPI backend for managing tasks and comments
- Task CRUD endpoints with filters for status, priority, and overdue items
- Due-date handling and overdue state calculation
- Status transition validation for workflow rules
- Comment support with task-scoped create/list/delete operations
- A lightweight kanban-style frontend in `frontend/index.html`
- Submission documentation under `docs/midcourse/`
- Automated tests for backend behavior

## Project structure

- `app/` — backend application code, routes, models, storage, and business rules
- `frontend/` — static UI for interacting with the API
- `tests/` — backend test suite
- `docs/midcourse/` — submission artifacts such as the ADR, reflection, verification notes, prompt log, and user stories

## Requirements

- Python 3.11+
- `pip` and a virtual environment

## Setup

```bash
# From the project root
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

## Run the frontend

The frontend is a static page served from `frontend/index.html`.

Option 1: open the file directly in a browser.

Option 2: serve it locally:

```bash
cd frontend
python -m http.server 5500
```

Then open:

- http://127.0.0.1:5500/index.html

The frontend expects the backend to be running at `http://127.0.0.1:8000`.

## Run the tests

From the project root:

```bash
pytest -q
```

## Submission docs

The `docs/midcourse/` folder includes the supporting material for this submission, including:

- `mini-adr.md` — architecture decision notes
- `reflection.md` — implementation reflection
- `verification.md` — verification summary
- `prompt-log.md` — prompt and iteration log
- `user-stories.md` — user requirements and acceptance coverage

## API summary

Key endpoints include:

- `GET /health`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /tasks/{task_id}/comments`
- `GET /tasks/{task_id}/comments`
- `DELETE /tasks/{task_id}/comments/{comment_id}`

This project is intended as a working task tracker submission rather than a single-endpoint skeleton.