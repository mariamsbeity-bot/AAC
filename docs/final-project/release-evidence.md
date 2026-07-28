# Release Evidence

## Baseline
- Branch: final-project
- Date: 28 July 2026
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: `{"status": "ok", "timestamp": "2026-07-28T09:09:04.420064+00:00"}`
- Frontend check: Opened `frontend/index.html` via `python -m http.server 5500`. Board rendered with all three columns; created and edited a task successfully. Note: the due-state badge (Overdue/Completed late) reflected a drag-triggered status change only after a page refresh, not immediately.
- Test command: `pytest -v`
- Test result: `40 passed, 2 warnings in 0.81s`