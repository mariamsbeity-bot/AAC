# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

## AI code review mini-log

Diff reviewed: commit `016fa7a` — "Adding Feature 1: Due Dates"
Files: `app/models.py`, `app/storage.py`, `app/main.py`

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| `due_state` returns `None` for `due_date == today` — a task due today is not considered overdue | Noise | Logic is consistent with "past only" interpretation but there is no comment or boundary test to prove intent; a maintainer cannot tell which interpretation was deliberate | Accepted as-is; the existing tests cover past dates and future dates but not today's date specifically — a known gap, acceptable at course scope |
| `?overdue=false` filter returns tasks with no due date, future tasks, and completed-late tasks — anything that is not exactly `"overdue"` | Useful | A real behaviour surprise for a teammate; the `completed_late` state silently leaks into the false bucket, which is counterintuitive | Left unfixed; would require a more precise filter spec and new tests; noted here as a backlog item |
| Import whitespace fix (`TaskStatus,TaskCreate` → `TaskStatus, TaskCreate`) bundled into the feature commit | Noise | Not wrong, but mixes cosmetic and functional changes in one commit; makes future bisect harder | No action needed |

## AI security mini-review

Source: `docs/security-review.md` (produced during Module 5)

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| Stored text fields are unbounded — only `title` has a 200-char limit; `description`, `assignee`, and comment `text` have no maximum; list endpoints return all results with no pagination | `app/models.py:25`, `app/storage.py:9`, `app/main.py:66` | Valid | Real gap; an attacker or careless client could exhaust memory with large payloads or very large collections | Backlog: add field-length limits and result caps before any shared deployment |
| No authentication or authorization — all endpoints are open to any caller | `README.md`, `app/main.py:49` | False Positive | Correctly identified as a risk in a real app, but explicitly out of course scope; README documents this limitation; graded as False Positive for this project | No action; course-scope decision already documented |
| Dependencies are not reproducible — packages use lower-bound pins, Docker base image uses a mutable tag, CI actions use mutable major-version tags | `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml` | Valid | Each build can resolve different versions; a future `fastapi` or `pydantic` release could silently break the app | Backlog: add a lockfile and pin base image by digest before production use |

## Manual security check

I read `app/main.py` lines 162–215 (the comment creation and task deletion routes) directly, checking whether a comment could be saved after its parent task was deleted. The task existence check (`get_task_by_id`) and the comment write (`add_comment`) are two separate operations with no lock between them. A concurrent delete between those two calls would leave an orphaned comment in memory. This is a real data-integrity gap — not covered by the AI findings, which focused on field limits and auth — and is only relevant if the app is accessed by multiple simultaneous users. At single-user course scope it is safe to leave unfixed; noted here as a known limitation.

## One AI output I rejected or corrected

During the Module 5 security review, AI finding SEC-02 flagged the absence of authentication and authorization as a medium-to-high severity issue and suggested adding auth before sharing the app. I rejected this as out of scope: the course brief explicitly excludes authentication from every module, the README documents the open-endpoint design as a known limitation, and adding auth would ripple through all 40 tests. I graded it False Positive for this project. The finding is valid for a real deployment — I just confirmed the scope boundary rather than implementing it.

## Three AI usage rules
1. Never paste: real credentials, `.env` values, tokens, or personal data into any AI tool
2. Always verify: run the app and tests after applying AI-generated code before committing
3. Record AI contributions by: noting what was generated, what I changed or rejected, and why — in the prompt log or review doc at the time it happens, not reconstructed afterward

## Ownership statement
I built the core task tracker experience myself, including the FastAPI endpoints, task and comment behavior, and the frontend board interactions, and I verified the result by running the app and the full test suite. AI helped with planning and review ideas, but I made the final decisions about what to keep, what to reject, and what was out of scope for this course project.I consider the final result to be my own work because I tested it, reviewed it, and made sure it matched the project requirements and the evidence collected.