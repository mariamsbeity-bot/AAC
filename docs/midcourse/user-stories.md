# User Stories — Mid-Course Project

---

## Feature 1: Due Dates + Overdue Filter

### Story 1
**As a team member,** I want to set an optional due date when creating a task so that I can plan when work should be finished.

**Acceptance Criteria:**
- `due_date` is optional; a task created without one is accepted and stored with `due_date` as null.
- A valid ISO 8601 date (e.g., `2026-07-30`) is accepted and returned in the task response.
- An invalid date format (e.g., `"next week"`, `30-07-2026`) returns HTTP 422 with a detail message that names the `due_date` field, so the error is clearly attributable to this feature.

### Story 2
**As a team member,** I want to add, change, or remove the due date on an existing task so that I can adjust plans when priorities shift.

**Acceptance Criteria:**
- `PATCH /tasks/{id}` with a valid `due_date` updates the task and returns the new value.
- `PATCH` with `due_date` set to `null` clears the due date.
- A `PATCH` that does not include `due_date` leaves the existing due date unchanged.
- Updating the due date of a missing task id returns HTTP 404.

### Story 3
**As a team member,** I want tasks to be flagged relative to their due date so that I can see which work has slipped and which work finished late.

**Acceptance Criteria:**
- A task is overdue when its `due_date` is before the server's current UTC date and its status is not Done.
- A task with status Done whose `due_date` is before the server's current UTC date is flagged as `"completed_late"`, not overdue.
- A task with status Done on or before its `due_date` carries neither flag.
- Tasks with no `due_date` carry neither flag.

### Story 4
**As a team member,** I want to filter the task list to only overdue tasks so that I can focus on late work first.

**Acceptance Criteria:**
- `GET /tasks?overdue=true` returns only tasks whose `due_state` is `"overdue"`; `"completed_late"` tasks are excluded.
- If no tasks are overdue, the response is HTTP 200 with an empty list, not 404.
- An invalid overdue value (e.g., `?overdue=banana`) returns HTTP 422.

### Story 5
**As a team member,** I want to see the due date and lateness state on each task card so that I can judge urgency at a glance without opening the task.

**Acceptance Criteria:**
- Cards for tasks with a `due_date` show the date as `YYYY-MM-DD`; cards without one show no date element.
- Tasks whose `due_state` is `"overdue"` display a pill element containing the text `"Overdue"`.
- Done tasks whose `due_state` is `"completed_late"` display a pill element containing the text `"Completed late"`.
- The due date field appears in the create/edit modal, is optional, and an invalid entry surfaces the server's 422 detail message without closing the modal.

### AI Assumptions — Feature 1

| Assumption | Status | Action taken |
|---|---|---|
| AI assumed Done tasks are never flagged regardless of due date. | **Corrected** | Done tasks past their due date are now flagged as `"completed_late"` — a distinct state from overdue. |
| AI used `"before today"` without specifying timezone. | **Corrected** | Changed to "before the server's current UTC date" to make the rule unambiguous and tests non-flaky. |
| AI assumed overdue is computed in the backend. | **Confirmed** | Backend computation chosen so the filter and UI share one definition. Recorded in mini-adr.md. |
| AI assumed `due_date` is a calendar date with no time component. | **Confirmed** | Date-only reduces complexity and is appropriate for this scope. |

---

## Feature 2: Task Comments

### Story 1
**As a team member,** I want to add a comment to a task so that I can record notes or updates about the work.

**Acceptance Criteria:**
- `POST /tasks/{task_id}/comments` with a non-blank `text` field creates a comment and returns HTTP 201 with the comment body including `id`, `task_id`, `text`, and `created_at`.
- A blank or whitespace-only `text` returns HTTP 422 with a detail message that names the `text` field.
- Posting a comment to a missing `task_id` returns HTTP 404 with a detail message identifying the task.

### Story 2
**As a team member,** I want to view all comments on a task so that I can follow the history of updates.

**Acceptance Criteria:**
- `GET /tasks/{task_id}/comments` returns HTTP 200 with a list of comments for that task, ordered by `created_at` ascending.
- A test that creates two comments in sequence asserts the first created comment appears at index 0 in the response list.
- If the task exists but has no comments, the response is HTTP 200 with an empty list, not 404.
- Requesting comments for a missing `task_id` returns HTTP 404.

### Story 3
**As a team member,** I want to delete a comment so that I can remove notes that are no longer relevant.

**Acceptance Criteria:**
- `DELETE /tasks/{task_id}/comments/{comment_id}` returns HTTP 204 with no response body on success.
- If the `task_id` does not exist, returns HTTP 404 naming the task.
- If the `comment_id` does not exist on that task, returns HTTP 404 naming the comment.
- If `comment_id` exists but belongs to a different `task_id`, returns HTTP 404 naming the comment.

### Story 5
**As a team member,** I want to read and add comments inside the task edit modal so that I can manage notes without leaving the board.

**Acceptance Criteria:**
- Opening the edit modal for a task loads and displays its existing comments, each showing `text` and `created_at`.
- Submitting a blank or whitespace-only comment is blocked client-side before any network request, with a visible message.
- A server 422 on `text` is shown inside the modal without closing it.
- After a comment is successfully added, the comment list in the modal refreshes.
- Delete is available per comment; after the delete request returns 204 the comment disappears from the list immediately.

### AI Assumptions — Feature 2

| Assumption | Status | Action taken |
|---|---|---|
| AI proposed an edit-comment route (`PATCH /comments/{id}`). | **Rejected** | The brief does not mention editing comments. Add and delete only. |
| AI left the orphaned-comment problem unresolved. | **Corrected** | Deleting a task now cascade-deletes all its comments in the `DELETE /tasks/{id}` route. |
| AI assumed a comment count badge on cards would be useful (Story 4). | **Rejected** | Dropped as out of scope — marked optional in the brief and adds extra fetch complexity. |
| AI's frontend added comment count badges to cards despite the prompt forbidding it, and the Add Comment button lacked `type="button"`. | **Caught on review and fixed** | Both bugs were caught by reading the diff and manual browser testing before accepting. |