Feature 1: Due Dates + overdue filter

Story 1: As a team member, I want to set an optional due date when creating a task so that I can plan when work should be finished. 

Acceptance Criteria:
    due_date is optional; a task created without one is accepted and stored with due_date as null.
    A valid ISO 8601 date (e.g., 2026-07-30) is accepted and returned in the task response.
    An invalid date format (e.g., "next week", 30-07-2026) returns HTTP 422 with a clear validation message.

Story 2: As a team member, I want to add, change, or remove the due date on an existing task so that I can adjust plans when priorities shift. 

Acceptance Criteria:
    PATCH /tasks/{id} with a valid due_date updates the task and returns the new value.
    PATCH with due_date set to null clears the due date.
    A PATCH that does not include due_date leaves the existing due date unchanged.
    Updating the due date of a missing task id returns HTTP 404.

Story 3: As a team member, I want overdue tasks to be clearly identified so that I can see which work has slipped. 

Acceptance Criteria:
    A task is overdue when its due_date is before today and its status is not Done.
    Tasks with status Done are never marked overdue, regardless of due date.
    Tasks with no due_date are never marked overdue.

Story 4: As a team member, I want to filter the task list to only overdue tasks so that I can focus on late work first. 

Acceptance Criteria:
    GET /tasks?overdue=true returns only tasks that meet the overdue definition.
    If no tasks are overdue, the response is HTTP 200 with an empty list, not 404.
    An invalid overdue value (e.g., ?overdue=banana) returns HTTP 422.

Story 5: As a team member, I want to see the due date on each task card so that I can judge urgency at a glance without opening the task. 

Acceptance Criteria:
    Cards for tasks with a due date show the date in a readable format; cards without one show no date element.
    Overdue tasks display a visually distinct overdue pill on the card.
    The due date field appears in the create/edit modal, is optional, and an invalid entry surfaces the server's 422 message without closing the modal.

edit story 1, the validation message should include the due_date field to know that the error belong to this feature

edit story 3, to be more precise some tasks may be in Done but after their due date so they should be flagged as "completed late"
