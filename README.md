# Task Tracker API

A small FastAPI-based task tracker (Module 4 course project) with task CRUD,
status-transition rules, due-date/overdue tracking, task-scoped comments, a
static HTML/JS kanban frontend, a Dockerfile for the backend, and a GitHub
Actions CI workflow that runs the test suite on every push/PR.

Storage is in-memory only (plain Python dicts) — there is no database, no
authentication, and this module does not include or claim any deployment
step. See [Project conventions and current limitations](#project-conventions-and-current-limitations)
below before assuming otherwise.

## Prerequisites

- Python 3.11+ (pinned in `Dockerfile` and `.github/workflows/ci.yml`; the
  interpreter version itself is not enforced at runtime by the app code)
- `pip` and the ability to create a virtual environment
- Docker Desktop (or a Docker Engine install) — only needed if you want to
  run the backend in a container; no specific version is required by
  anything in this repo

## Local setup

Run from the project root:

```bash
python -m venv venv
```

Activate it:

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently pins: `fastapi>=0.115`, `uvicorn[standard]>=0.34`,
`pydantic>=2.12`, `python-dotenv>=1.1`, plus unpinned `pytest` and `httpx`
(both needed for the test suite; `[VERIFY]` if a specific version of either
should be pinned instead).

## Run the app locally

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### Run the frontend

The frontend is a static file, served independently of the API:

```bash
cd frontend
python -m http.server 5500
```

Then open http://127.0.0.1:5500/index.html. The page itself calls the API at
`http://localhost:8000` (hardcoded in `frontend/index.html`); CORS in
`app/main.py` allows both `localhost` and `127.0.0.1` on ports 3000, 5500,
and 8080.

## Run tests

From the project root:

```bash
pytest -v
```

Run a single file or test:

```bash
pytest tests/test_tasks.py -v
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body -v
```

## Run with Docker

The `Dockerfile` is a multi-stage build (`python:3.11-slim`) that packages
only the backend (`app/` + `requirements.txt`) and runs as a non-root `app`
user. The frontend is not included in the image — it is not proxied or
served by the container in any way.

Build:

```bash
docker build -t task-tracker:dev .
```

Run, mapping container port 8000 to the host:

```bash
docker run -d --name tt-dev -p 8000:8000 task-tracker:dev
```

Verify:

```bash
curl -i http://localhost:8000/health
```

Stop and remove when done:

```bash
docker rm -f tt-dev
```

## CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request`:

1. Checks out the repo (`actions/checkout@v4`).
2. Sets up Python, pinned to `3.11` (`actions/setup-python@v5`).
3. Installs dependencies: `python -m pip install --upgrade pip` then
   `pip install -r requirements.txt`.
4. Runs `pytest -v` directly — a failing test fails the job; there is no
   `continue-on-error`, no `|| true`, and no output piping that could mask
   the exit code.

There is no build, publish, or deploy step in this workflow.

## Project structure

- `app/` — backend application code (routes, models, storage, business rules); see `CLAUDE.md` for the per-file breakdown
- `frontend/` — static UI for interacting with the API
- `tests/` — backend test suite
- `docs/midcourse/` — submission artifacts such as the ADR, reflection, verification notes, prompt log, and user stories
- `Dockerfile`, `.dockerignore` — backend container image (see [Run with Docker](#run-with-docker))
- `.github/workflows/ci.yml` — CI workflow (see [CI workflow summary](#ci-workflow-summary))
- `requirements.txt` — Python dependencies
- `CLAUDE.md` — detailed architecture/business-rules reference for AI-assisted work in this repo

## Project conventions and current limitations

- **No persistence**: all tasks/comments are stored in in-memory Python
  dicts and are wiped on every server/container restart. There is no
  database in this module.
- **No authentication/authorization**: every endpoint is open.
- **No deployment**: the only documented run paths are local `uvicorn` and
  the local Docker image above; nothing in this repo deploys the app
  anywhere.
- **Status transitions are restricted**: only `ToDo -> InProgress`,
  `InProgress -> Done`, and `Done -> InProgress` are valid; any other
  transition (including no-op same-status) is rejected with 422.
- **`due_state` is computed, not stored**, and is evaluated against the
  server's UTC date — not any per-user timezone.
- **Comments cascade-delete manually**: deleting a task explicitly deletes
  its comments first (no DB foreign key is enforcing this).
- **All request models use `extra="forbid"`**: unknown fields in a request
  body are rejected with 422 rather than silently ignored.
- **The Docker image only contains the backend**: the frontend must be run
  separately (see [Run the frontend](#run-the-frontend)) if you want the UI.
- **`pytest`/`httpx` are unpinned** in `requirements.txt` — `[VERIFY]` if a
  specific version should be pinned for reproducibility.

## Decisions and submission docs

Architecture/scope decisions for this project — including *why* comments
got their own in-memory store instead of a database, and why in-memory
storage was chosen over SQLite under deadline constraints — are recorded in
[`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md).

The rest of `docs/midcourse/` holds other submission artifacts:

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
