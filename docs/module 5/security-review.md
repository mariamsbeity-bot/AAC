# Security Review

## AI Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence | Grade | Reason |
|---|---|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/models.py:25`, `app/storage.py:9`, `app/main.py:66` | Stored text and collection responses are unbounded, enabling memory/resource exhaustion if the API is reachable by untrusted clients. | Only `title` has a 200-character limit. `description`, `assignee`, and comment `text` have no maximum; task/comment stores are in-memory dicts; list endpoints return all matching records without pagination. | Before any shared deployment, add server-side length limits, request-size limits at the proxy/server, pagination or result caps, and appropriate rate/usage limits. | High | Good | Text limits are important, but they are applied only to the title. |
| SEC-02 | Informational — course-scope decision; High if deployed/shared | `README.md:148`, `app/main.py:49` | All task and comment data is readable and mutable by any caller; there is no authentication or authorization boundary. | README explicitly states “No authentication/authorization: every endpoint is open.” Route handlers have no identity or ownership checks. | This is acceptable for the documented local learning scope. Treat it as a deployment blocker: add authentication, per-resource authorization, and an appropriate CSRF strategy if browser credentials are introduced. | High | Bad / Reject | This is a learning project; ownership checks and authentication are not needed within its stated scope. |
| SEC-03 | Low | `requirements.txt:1`, `Dockerfile:2`, `.github/workflows/ci.yml:12` | Builds are not dependency-reproducible or integrity-pinned. | Python packages use lower bounds or no version pin; Docker uses a mutable `python:3.11-slim` tag; CI actions use mutable major-version tags rather than commit SHAs. Each build can resolve different artifacts. | For a production-bound project, use a reviewed lockfile with hashes, pin the base image by digest, pin CI actions to reviewed SHAs, and add dependency/image vulnerability scanning. | High | Very Good | The library versions are not fully pinned, which can cause future version issues and library incompatibilities. |

## My Manual Findings

| Severity | File:Line | Finding | Suggested Fix | Reason |
|---|---|---|---|---|
| Low | `app/main.py`; `app/comments_storage.py` | If someone adds a comment while another person deletes the same task, the comment can still be saved after its task is gone. This leaves unused comment data in memory. | When concurrent use is needed, handle the task check and comment save together with a lock or transaction. | The task is checked before the comment is saved, while task deletion is a separate sequence. The two requests can overlap. |
| Low | `requirements.txt; `Dockerfile` | The Docker image includes test tools (`pytest` and `httpx`) even though the app does not need them to run. | Use separate runtime and development requirements, and copy only runtime dependencies into the final image. | The build installs every dependency from `requirements.txt` and copies them into the runtime image. Keeping only app dependencies makes the image smaller and reduces packages that may need security updates. |

## Reconciliation

AI coverage was strongest on broad API validation, authorization scope, and dependency hygiene.  
The manual scan added a more code-flow-specific concurrency and data-integrity issue; its Docker observation reinforced the AI's deployment/dependency coverage.

### Agreement

- Dependency/container hygiene: AI finding SEC-03 identified non-reproducible dependency and image pinning; the manual scan found the related issue that test dependencies are included in the runtime image.

### AI-only

- SEC-01: Unbounded text and unpaginated in-memory collections can exhaust resources.
- SEC-02: No authentication/authorization; recorded as a course-scope limitation and rejected for this learning project.

### You-only

- Comment/task deletion race: a comment can be saved after its parent task is deleted. Evidence: `app/main.py:186-188, 270-274` and `app/comments_storage.py:27-34`.

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|---|---|---|---|---|
| 1 | Unbounded task/comment text and collection reads (SEC-01) | Medium | Backend | Set field-length limits and add pagination/result limits before shared use. |
| 2 | Dependency and runtime-image hygiene (SEC-03 and related manual Docker finding) | Low | DevOps | Create separate runtime/development requirements; add a lockfile and pin image/action versions for production use. |
| 3 | Comment creation/deletion race | Low | Backend | Make the existence check and comment write atomic when concurrent use is required. |
