# Comments on Tasks Feature Plan

## 1. Data Model

The repository already has comment models in [`app/models.py`]( AAC\task-tracker\task-tracker-api\app\models.py), but they currently use a `text` field without an author or maximum-length constraint. The planned contract should evolve these models to:

- Comment-create fields: `author` (required string, 1–100 characters) and `body` (required string, 1–2,000 characters).
- Comment-response fields: `id`, `task_id`, `author`, `body`, and server-generated `created_at`.
- Request models should continue the repository convention of `ConfigDict(extra="forbid")`.
- Validation should follow the existing title/comment normalization pattern: trim surrounding whitespace, reject blank values, and enforce maximum lengths.
- `created_at` should be timezone-aware UTC, matching task timestamps generated in [`app/storage.py`]( AAC\task-tracker\task-tracker-api\app\storage.py).
- IDs should follow the current storage convention of UUID4-generated string values. The implementation currently uses `uuid4().hex`, so whether canonical hyphenated UUID strings are required should be confirmed.

Comments should remain separate from `TaskResponse`, stored in [`app/comments_storage.py`]( AAC\task-tracker\task-tracker-api\app\comments_storage.py) as an in-memory dictionary keyed by comment ID. Each comment retains `task_id` for filtering and parent-task ownership checks. This matches the existing architecture and ADR decision in [`docs/midcourse/mini-adr.md`]( AAC\task-tracker\task-tracker-api\docs\midcourse\mini-adr.md).

Deleting a task should continue manually deleting its comments first, as currently done in [`app/main.py`]( AAC\task-tracker\task-tracker-api\app\main.py).

## 2. API Routes

### Create a comment

`POST /tasks/{task_id}/comments`

Request body:

- `author`: required string, 1–100 characters.
- `body`: required string, 1–2,000 characters.

Response:

- HTTP 201.
- Comment object containing generated `id`, the supplied `task_id`, normalized `author` and `body`, and UTC `created_at`.

Errors:

- HTTP 404 when `task_id` does not identify an existing task.
- HTTP 422 for missing, blank, overlong, or incorrectly typed `author` or `body`.
- HTTP 422 for unknown request fields.

### List comments

`GET /tasks/{task_id}/comments`

Request body: none.

Response:

- HTTP 200.
- Array of comments belonging to the task, ordered oldest first by `created_at`.
- An existing task with no comments returns an empty array.

Errors:

- HTTP 404 when the task does not exist.

### Delete a comment

`DELETE /tasks/{task_id}/comments/{comment_id}`

Request body: none.

Response:

- HTTP 204 with no response body.

Errors:

- HTTP 404 when the parent task does not exist.
- HTTP 404 when the comment does not exist.
- HTTP 404 when the comment exists but belongs to another task.

The current implementation does not expose comment update or standalone comment lookup routes. Adding `PATCH` or `GET /comments/{comment_id}` should remain out of scope unless the team decides otherwise.

### Task deletion interaction

`DELETE /tasks/{task_id}` should retain cascade behavior:

- Delete all comments associated with the task.
- Delete the task.
- Return HTTP 204.
- Return HTTP 404 for a missing task without creating or deleting unrelated comments.

## 3. Tests

Tests should follow the existing `pytest` and FastAPI `TestClient` style in [`tests/test_comments.py`]( AAC\task-tracker\task-tracker-api\tests\test_comments.py), using the autouse reset fixture in [`tests/conftest.py`]( AAC\task-tracker\task-tracker-api\tests\conftest.py).

### Happy path

- `test_create_comment_with_author_and_body_returns_201_with_full_body`
- `test_create_comment_generates_uuid_and_utc_created_at`
- `test_list_comments_returns_200_and_empty_list_for_task_with_no_comments`
- `test_list_comments_returns_comments_sorted_by_creation_time`
- `test_delete_comment_returns_204_and_comment_is_removed`
- `test_delete_task_cascades_all_comments`

### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_author_returns_422_naming_author`
- `test_create_comment_blank_body_returns_422_naming_body`
- `test_create_comment_author_at_100_characters_is_accepted`
- `test_create_comment_author_over_100_characters_returns_422`
- `test_create_comment_body_at_2000_characters_is_accepted`
- `test_create_comment_body_over_2000_characters_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_invalid_field_types_returns_422`

### Edge cases and ownership

- `test_create_comment_for_missing_task_returns_404`
- `test_list_comments_for_missing_task_returns_404`
- `test_delete_comment_for_missing_task_returns_404`
- `test_delete_nonexistent_comment_returns_404`
- `test_delete_comment_with_wrong_task_returns_404`
- `test_comments_are_isolated_between_tasks`
- `test_comment_created_at_is_server_generated_even_if_client_supplies_one`
- `test_comment_id_is_not accepted_from_request_body`
- `test_deleting_missing_task_does_not_remove_comments_from_other_tasks`

The existing tests that refer to `text` should be renamed and updated to the `author`/`body` contract. The fixture should continue clearing both task and comment stores before and after each test.

## 4. Frontend Changes

The frontend is a single inline HTML/CSS/JavaScript file at [`frontend/index.html`]( AAC\task-tracker\task-tracker-api\frontend\index.html).

The current UI already:

- Loads comments when opening the task edit modal.
- Displays comments oldest first.
- Adds comments through `POST /tasks/{task_id}/comments`.
- Deletes individual comments.
- Shows a “No comments yet.” placeholder.
- Keeps the comments section hidden in create mode.
- Avoids comment count badges on task cards.

For the planned contract, this file would change to:

- Replace the single comment text input with an author input and body textarea.
- Enforce client-side limits matching the API: author 1–100 characters and body 1–2,000 characters.
- Submit `{author, body}` instead of `{text}`.
- Render author, body, and formatted `created_at`.
- Preserve visible validation errors without closing the modal.
- Preserve the existing `type="button"` behavior for the Add Comment control.
- Continue escaping rendered user content and showing per-comment delete errors.
- Update empty-state and network-error messaging as needed.

No separate frontend file or build step is visible in the repository.

## 5. Migration Notes

The repository uses in-memory dictionaries only; there is no database schema or durable migration process. Existing task data is lost on process or container restart, as documented in [`README.md`]( AAC\task-tracker\task-tracker-api\README.md).

The main compatibility change is the comment payload shape:

- Existing implementation: `text`.
- Planned implementation: `author` and `body`.

Because storage is process-local, no persistent data migration is required. However:

- Existing clients and frontend code sending `text` must be updated together with the API.
- Existing comment tests must be rewritten around `author` and `body`.
- The response model and in-memory comment records must change consistently.
- The test reset hook must remain connected to the comment store.
- Task deletion’s manual comment cascade must continue to operate against the revised comment model.
- The team should decide whether any temporary backward compatibility for `text` is needed; the current `extra="forbid"` convention favors rejecting the old shape.

The current README and ADR describe comments as already implemented, while the requested contract differs from the visible implementation. This plan therefore describes the required contract adjustment rather than a first-time addition.

## 6. Open Questions

1. Should comment IDs remain the current UUID4 hex format (`uuid4().hex`) or change to canonical hyphenated UUID strings?
2. Should author and body be trimmed before storage, as task titles and current comment text are, or should whitespace be preserved within the length limits?
3. Is comment editing intentionally excluded, or should a future `PATCH` route be designed now?
4. Should the API temporarily accept legacy `{text: ...}` payloads during the frontend transition, or should the new schema reject them immediately?
5. Should comments eventually be persisted in the same database/storage layer as tasks, or is the separate in-memory store still intentional?
6. Should author values be free-form display names, or should they later reference authenticated users?
7. Should comment list responses eventually support pagination or result limits? The security review identifies unbounded comment reads as a current limitation.
8. Should task/comment creation and task deletion be made atomic if concurrent requests become part of the supported deployment model?

## Files read

- [`AGENTS.md`]( AAC\task-tracker\task-tracker-api\AGENTS.md)
- [`README.md`]( AAC\task-tracker\task-tracker-api\README.md)
- [`app/models.py`]( AAC\task-tracker\task-tracker-api\app\models.py)
- [`app/main.py`]( AAC\task-tracker\task-tracker-api\app\main.py)
- [`app/storage.py`]( AAC\task-tracker\task-tracker-api\app\storage.py)
- [`app/comments_storage.py`]( AAC\task-tracker\task-tracker-api\app\comments_storage.py)
- [`app/business_rules.py`]( AAC\task-tracker\task-tracker-api\app\business_rules.py)
- [`tests/conftest.py`]( AAC\task-tracker\task-tracker-api\tests\conftest.py)
- [`tests/test_tasks.py`]( AAC\task-tracker\task-tracker-api\tests\test_tasks.py)
- [`tests/test_comments.py`]( AAC\task-tracker\task-tracker-api\tests\test_comments.py)
- [`frontend/index.html`]( AAC\task-tracker\task-tracker-api\frontend\index.html)
- [`docs/midcourse/mini-adr.md`]( AAC\task-tracker\task-tracker-api\docs\midcourse\mini-adr.md)
- [`docs/security-review.md`]( AAC\task-tracker\task-tracker-api\docs\security-review.md)

## Assumptions to verify

- The requested `author`/`body` contract supersedes the currently implemented `text` contract.
- No authentication or author identity service is available; author is therefore treated as client-supplied display text.
- UUID4 hex IDs remain acceptable unless the team requires canonical UUID formatting.
- No persistent storage migration is needed while the documented in-memory architecture remains intentional.
- Comment editing, pagination, and standalone comment retrieval are not required for the initial scope.
- The frontend should continue managing comments only inside the task edit modal.