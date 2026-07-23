# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Tech stack

- Python 3.11+ (per README "Requirements" section; not version-pinned in code)
- FastAPI (`fastapi>=0.115`, per `requirements.txt`)
- Pydantic v2 (`pydantic>=2.12`, per `requirements.txt`; models use `ConfigDict`, `field_validator`, `computed_field` — v2-only APIs)
- Uvicorn (`uvicorn[standard]>=0.34`, per `requirements.txt`)
- python-dotenv (`python-dotenv>=1.1`, per `requirements.txt`, used in `app/core/config.py`)
- pytest — used by the test suite (`tests/`), but **not listed in `requirements.txt`**; exact version `[VERIFY]`
- httpx — required transitively by `fastapi.testclient.TestClient` (used in `tests/conftest.py`); **not imported directly anywhere and not listed in `requirements.txt`**; exact version `[VERIFY]`
- Frontend: vanilla JavaScript, no framework/build step — single static file `frontend/index.html` with inline `<style>`/`<script>`

## 2. Run command (this course)

```bash
uvicorn app.main:app --reload --port 8000
```

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- App: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Frontend (static file; see section 6 for the base-URL caveat):

```bash
cd frontend
python -m http.server 5500
```

## 3. Test command (this course)

```bash
pytest -v
```

Run a single test file or test:

```bash
pytest tests/test_tasks.py -v
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body -v
```

## 4. Architecture summary

**Backend** (`app/`):
- `app/main.py` — all route handlers live directly on the FastAPI app (no per-resource router for tasks/comments; only `health` uses `APIRouter`, included from `app/api/routes/health.py`). Handlers do HTTP-level validation (404s, status-transition checks) and delegate persistence to the storage modules.
- `app/storage.py` — in-memory task store (`dict[str, TaskResponse]`), plus `_reset()` used only by tests.
- `app/comments_storage.py` — in-memory comment store, a **separate** dict keyed by `comment_id` (not embedded in `TaskResponse`); each comment carries `task_id` for ownership/filtering.
- `app/models.py` — all Pydantic v2 models/enums. All models use `extra="forbid"`, so unknown request fields are a 422.
- `app/core/config.py` — env config via `python-dotenv` (`APP_ENV`, `PORT`).

**Frontend**: `frontend/index.html` — single static file, no build step (see section 6).

**Tests** (`tests/`):
- `tests/conftest.py` — `_reset_storage` autouse fixture clears both stores (`storage._reset()`, `_reset_comments()`) before/after every test; `client` fixture wraps `TestClient(app)`.
- `tests/test_tasks.py`, `tests/test_comments.py` — endpoint-level tests via `TestClient`.
- `tests/verify_a.py` — present in the suite; contents not reviewed for this change.

**Where task rules live**:
- `app/business_rules.py` — status-transition validation (see section 5), enforced in `main.py`'s `update_task` before calling `storage.update_task`.
- `app/models.py` — field-level rules (title non-blank/≤200 chars, comment text non-blank, `extra="forbid"`) and the `due_state` computed field.
- `app/main.py` — cross-resource rule: `DELETE /tasks/{id}` manually cascades, deleting all comments for that task before deleting the task itself (no DB-level FK to do this automatically).

No persistence: all tasks/comments are wiped on every server restart (in-memory dicts only, by design per `docs/midcourse/mini-adr.md`).

## 5. Business rules

**Task status values** (`app/models.py`, `TaskStatus` enum):
- `ToDo`
- `InProgress`
- `Done`

**Valid status transitions** (`app/business_rules.py`, `VALID_TRANSITIONS`):
- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`

Any pair not in that set — including same-status (`X -> X`) — raises `HTTPException(422)` from `validate_status_transition()`. This is called from `update_task` in `app/main.py` only when `payload.status is not None`.

**Due-state derivation** (`TaskResponse.due_state`, a `@computed_field` in `app/models.py`, not stored):
- `None` if `due_date` is unset or not in the past
- `"overdue"` if `due_date` is in the past and status is not `Done`
- `"completed_late"` if `due_date` is in the past and status is `Done`
- Computed against `datetime.now(timezone.utc).date()` — server UTC, not per-user timezone. `[VERIFY]` if this still holds if `app/business_rules.py` or `app/models.py` change.

## 6. UI states and CORS notes

**CORS** (`app/main.py`, `CORSMiddleware`): explicitly allowlists origins on ports 3000, 5500, and 8080, for both `localhost` and `127.0.0.1`. Add any new local dev port to both host variants there.

**Frontend base URL caveat**: `frontend/index.html` hardcodes `const API_BASE_URL = 'http://localhost:8000'` — only the `localhost` form, not `127.0.0.1`, even though CORS allows both. If the frontend is opened via a `127.0.0.1` origin this still works (CORS allows it), but calls always target `localhost:8000` regardless of how the page itself was loaded.

**UI states implemented in `frontend/index.html`**:
- Task list: `"Loading tasks..."` (info) while fetching, `"No tasks available yet."` / `"No overdue tasks found."` (info, empty state) when the list is empty, `"Unable to load tasks. Please refresh the page."` (error) on fetch failure.
- Task form modal: inline field error under Title (`"Title is required"`), a modal-level error banner for API-rejected submits (422 or other non-OK responses), separate error region for comment submission and for comment fetch failures.
- Comments panel: `"Loading comments..."` while fetching, `"No comments yet."` when empty, `"Unable to load comments. Please try again."` on failure.
- Drag-and-drop status change: optimistic UI update, reverted via `revertTaskStatus()` with an error status message if the PATCH request fails or the network errors.

## 7. Do-not rules

Do not do any of the following without asking first:
- Add authentication/authorization.
- Add a database or persistence layer (current storage is in-memory by design, per `docs/midcourse/mini-adr.md`).
- Add deployment steps/configuration (this project's documented run path is local `uvicorn` only).
- Make major UI changes to `frontend/index.html` (layout, framework adoption, new pages/views).

## Submission docs

`docs/midcourse/` contains course-submission artifacts (ADR, reflection, verification notes, prompt log, user stories) — not application documentation. `mini-adr.md` documents *why* comments got their own storage dict and why in-memory storage (not SQLite) was chosen for both features — read it before proposing a storage redesign.
