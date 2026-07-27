# Comments on Tasks: Generic Plan

## 1. Data Model

Add a comment entity with:

- `id`: server-generated UUID string.
- `task_id`: required reference to the parent task.
- `author`: required string, 1–100 characters.
- `body`: required string, 1–2,000 characters.
- `created_at`: server-generated, timezone-aware UTC datetime.

Represent the task relationship according to the application’s existing persistence pattern. Enforce the parent-task relationship so comments cannot reference nonexistent tasks. Decide whether deleting a task should cascade-delete its comments or prevent deletion while comments exist.

Validate required fields, reject blank values, and define whether leading or trailing whitespace is trimmed.

## 2. API Routes

### Create a comment

`POST /tasks/{task_id}/comments`

Request body: `author` and `body`.

Response: HTTP 201 with the complete comment, including generated `id`, `task_id`, and `created_at`.

Possible errors:

- 404 if the task does not exist.
- 422 if required fields are missing, blank, too long, or incorrectly typed.
- 422 for unsupported fields.

### List task comments

`GET /tasks/{task_id}/comments`

Request body: none.

Response: HTTP 200 with comments for the task, ordered by creation time, normally oldest first. Return an empty list when the task exists but has no comments.

Possible errors:

- 404 if the task does not exist.

### Delete a comment

`DELETE /tasks/{task_id}/comments/{comment_id}`

Request body: none.

Response: HTTP 204 with no body.

Possible errors:

- 404 if the task does not exist.
- 404 if the comment does not exist.
- 404 if the comment exists but belongs to another task.

Comment editing, pagination, filtering, and standalone comment lookup are optional extensions and should not be assumed without a product decision.

## 3. Tests

### Happy path

- Create a comment for an existing task.
- Verify the response contains all required fields.
- Verify the server generates the ID and UTC timestamp.
- List comments for a task.
- Verify multiple comments are returned in creation order.
- Verify an existing task with no comments returns an empty list.
- Delete a comment successfully.
- Verify the deleted comment no longer appears.
- Verify task deletion follows the chosen comment-cascade policy.

### Validation

- Missing `author`.
- Missing `body`.
- Blank or whitespace-only `author`.
- Blank or whitespace-only `body`.
- Author at exactly 100 characters.
- Author over 100 characters.
- Body at exactly 2,000 characters.
- Body over 2,000 characters.
- Invalid field types.
- Unknown request fields.
- Client attempts to provide `id`, `task_id`, or `created_at` in the request body.

### Edge cases

- Create a comment for a nonexistent task.
- List comments for a nonexistent task.
- Delete a nonexistent comment.
- Delete a comment using the wrong task ID.
- Confirm comments from different tasks remain isolated.
- Confirm timestamps are UTC and server-generated.
- Confirm concurrent creation/deletion behavior if the application supports concurrent requests.
- Confirm behavior when a task is deleted with existing comments.

## 4. Frontend Changes

Update the task-detail, task-edit, or task-modal interface to support:

- Displaying comments associated with the selected task.
- Showing author, body, and creation time.
- An author input limited to 100 characters.
- A body textarea limited to 2,000 characters.
- Client-side required-field and length validation.
- Submission through the create-comment endpoint.
- Refreshing or appending the comment list after successful creation.
- Deleting individual comments.
- Empty, loading, validation-error, and network-error states.
- Safe rendering of user-supplied author and body content.

The exact files and component locations depend on the application’s frontend structure. The UI should make clear whether comments are available during task creation, task editing, or both.

## 5. Migration or Data-Shape Notes

Changing the API from no comments to comments requires deciding how existing task records represent comments:

- Embedded comments require a task-record shape change.
- Separate comment storage requires a new collection/table/store and a task reference.
- A relational database requires a foreign key and an index on `task_id`.
- Existing records may need an empty-comment default or a backfill.

The response and request contract should be versioned or transitioned carefully if clients already exist. Decide whether legacy field names are accepted temporarily.

If the application currently stores data only in memory, no durable migration may be needed, but all data will still be lost on restart. If comments become persistent, define indexes, foreign-key behavior, timestamp serialization, and rollback procedures.

## 6. Open Questions

1. Should deleting a task cascade-delete its comments, reject deletion, or soft-delete both?
2. Should comments be editable after creation?
3. Should `author` be free-form text or derived from authenticated user identity?
4. Should comment IDs use canonical hyphenated UUIDs or another existing ID format?
5. Should leading and trailing whitespace be trimmed?
6. Should comments support pagination or maximum response sizes?
7. Should comments be sorted oldest-first or newest-first?
8. Should the API support markdown, plain text only, or sanitized rich text?
9. Should clients be allowed to supply any timestamp or metadata? The proposed contract says timestamps are server-generated.
10. Is backward compatibility required for existing clients or data formats?

## Assumptions this plan makes

- The application has an existing task resource and can identify tasks by string IDs.
- The API uses JSON request and response bodies.
- The application can enforce validation constraints at the API boundary.
- The persistence layer can represent a one-to-many task-to-comment relationship.
- Authentication and authorization requirements are not specified.
- No actual repository file names, storage approach, frontend structure, route layout, or test framework have been inferred.
- The initial scope includes creating, listing, and deleting comments, but not editing them.