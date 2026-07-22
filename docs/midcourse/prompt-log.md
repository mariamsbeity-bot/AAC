# Prompt Log — Mid-Course Project

---

## Feature 1: Due Dates + Overdue Filter

---

### Prompt 1 — User Story Generation (Weak → Strong rewrite)

**Weak prompt:**
```
i want to add this feature Due dates + overdue filter, write me several user stories
```

**What the weak prompt returned:**
- 12 generic stories using "user" (not "team member") as the role.
- Added out-of-scope features: calendar picker with quick options ("Today", "Tomorrow",
  "Next week"), combine filter with project/tag, overdue count badge, sort by due date.
- No acceptance criteria — only story statements.
- No failure cases or HTTP status codes.

**Accepted, edited, or rejected:** Rejected in full — wrong format, out-of-scope features,
no testable criteria.

---

**Strong prompt:**
```
I want to add the feature Due dates + overdue filter,
with Expected backend work:
- Add optional due_date validation. Support create/update.
- Decide whether overdue is computed in the backend or UI.
- Optional query filter for overdue.

with expected frontend work:
- Add due date to the modal.
- Show due date or overdue pill on cards.
- Add an overdue filter or visual indicator.

and create tests for this feature:
- Valid due date, invalid date format, overdue detection, update due date,
  filter returns only overdue tasks.

I want from you to give me several user stories in the same format and quality
as this example.

Example:
Story: As a team member, I want to create a task so that I can track work.
Acceptance Criteria:
- Title is required; missing or blank title returns HTTP 422.
- Description is optional.
- A created task appears in the task list with status, priority, and assignee.

Constraints:
- Use "team member" as the user role.
- Do not mention login, authentication, user accounts, admin roles,
  notifications, mobile, or real-time updates.
- Include at least one failure case across the generated stories.

Output format: Return each story with Story and Acceptance Criteria headings.
```

**What the strong prompt returned:** 5 structured stories in the correct format with
testable acceptance criteria, correct role, failure cases, and in-scope content.

**Accepted, edited, or rejected:**
- Accepted Stories 2, 4 and 5 as written.
- Edited Story 1: changed "a clear validation message" to "a detail message that names
  the `due_date` field" — "clear" is not testable.
- Edited Story 3: corrected the AI assumption that Done tasks are never flagged;
  added the `"completed_late"` state for Done tasks past their due date.

---

### Prompt 2 — Requirements Review

**Prompt:**
```
You are a senior developer reviewing requirements before implementation.

Context: simple FastAPI backend and simple web frontend, no auth, no accounts,
no multi-tenancy, no real-time updates, no mobile, no notifications.

Task: Review the user stories for testability and scope alignment.
Check: in scope? specific and testable? failure cases? vague words? unrequested assumptions?

Constraints: Do not generate a new story set. Suggest minimal edits only.

Output format: Return a table with columns: Story ID, Pass / Needs revision,
Issue, Minimal edit.
```

**What it returned:** Four-column review table identifying Stories 1, 3, and 5 as
needing revision with specific minimal edits. Flagged the backend-computation
assumption (S3) as a decision to record in the ADR.

**Accepted, edited, or rejected:**
- Accepted all three revisions as starting points.
- Applied my own wording for Story 3 (added "completed_late" distinction beyond
  what the table suggested).
- Used the cross-set checks to note that `?overdue=banana → 422` is FastAPI framework
  behavior, not custom validation code.

---

### Prompt 3 — Additive Test Generation

**Prompt:** Specified 10 named test functions to ADD to the existing suite without
regenerating conftest.py or touching existing tests. Included the transition-chain
constraint (never jump ToDo → Done directly), PAST_DATE / FUTURE_DATE semantics,
and required specific-value assertions — not just status codes.

**What it returned:** 10 test functions appended to test_tasks.py; 29 passed, 2 warnings.

**Accepted, edited, or rejected:**
- Accepted all 10 test functions.
- Identified a date-fragility flaw on review: hardcoded future dates (`"2026-07-30"`,
  `"2026-08-15"`) would become past dates after those calendar days, flipping
  `due_state` and breaking correct code. Issued follow-up Prompt 5.

---