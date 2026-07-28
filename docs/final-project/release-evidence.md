# Release Evidence

## Baseline
- Branch: final-project
- Date: 28 July 2026
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: `{"status": "ok", "timestamp": "2026-07-28T09:09:04.420064+00:00"}`
- Frontend check: Opened `frontend/index.html` via `python -m http.server 5500`. Board rendered with all three columns; created and edited a task successfully. Note: the due-state badge (Overdue/Completed late) reflected a drag-triggered status change only after a page refresh, not immediately.
- Test command: `pytest -v`
- Test result: `40 passed, 2 warnings in 0.81s`

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Latest run link: https://github.com/mariamsbeity-bot/AAC/actions/runs/30346244058
- Test command used by CI: `pytest -v`
- Shortcut check: no `continue-on-error` / no `|| true` / pytest is not skipped / Python pinned to 3.11

## Docker evidence
- Build command: `docker build -t task-tracker .`
- Run command: `docker run -d --name tt-dev -p 8000:8000 task-tracker`
- /health check: `{"status":"ok","timestamp":"2026-07-28T09:27:16.533264+00:00"}` — HTTP 200
- Non-root check: `docker exec tt-dev whoami` → `app` (confirmed non-root user)
- No-baked-secrets check: `docker exec tt-dev ls -la /app` → only `app/` and
  `requirements.txt` present; no `.env` or secrets in image

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `AGENTS.md` and `CLAUDE.md` claim `pytest` and `httpx` are not listed in `requirements.txt` | Read `requirements.txt` directly — both `pytest` and `httpx` are listed (unpinned) | Claim was inaccurate | Left as-is; stale comment, does not affect runtime or test execution |
| README claims CORS allows `localhost` and `127.0.0.1` on ports 3000, 5500, and 8080 | Read `app/main.py` lines 33–41; all six origins confirmed in `allow_origins` list | Claim accurate | No change needed |
| README claims `DELETE /tasks/{id}` returns HTTP 204 with no body | Ran `Invoke-WebRequest -Method Delete` against a live task; `$response.StatusCode` → `204`, `$response.Content.Length` → `0` | Claim accurate | No change needed |