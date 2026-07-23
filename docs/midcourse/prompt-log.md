# Prompt Log — Mid-Course Project

---

## Feature 1: Due Dates + Overdue Filter

### Prompt 1 — User Story Generation (Weak → Strong rewrite)

**Weak prompt:**
```
i want to add this feature Due dates + overdue filter, write me several user stories
```

**What the weak prompt returned:** 12 generic stories using "user" (not "team member")
as the role. Added out-of-scope features: calendar picker, combine filter with
project/tag, overdue count badge, sort by due date. No acceptance criteria, no
failure cases, no HTTP status codes.

**Accepted, edited, or rejected:** Rejected in full — wrong format, out-of-scope
features, no testable criteria.

---

**Strong prompt:** Specified the feature scope, backend/frontend work, test cases,
the exact example story format, role constraint ("team member"), failure case
requirement, and output format.

**What the strong prompt returned:** 5 structured stories in the correct format
with testable acceptance criteria, correct role, and failure cases.

**Accepted, edited, or rejected:**
- Edited Story 1: "a clear validation message" → "a detail message that names the `due_date` field."
- Edited Story 3: corrected AI assumption that Done tasks are never flagged; added `"completed_late"` state.
- Edited Story 5: "readable format" → "YYYY-MM-DD"; "visually distinct" → exact pill text.

---

### Prompt 2 — Requirements Review

**Prompt:** Senior developer role, checklist of four review criteria, constraints
to not regenerate stories, output as a table with four columns.

**What it returned:** Table identifying Stories 1, 3, and 5 as needing revision
with specific minimal edits. Flagged the backend-computation assumption as a
decision to record in the ADR.

**Accepted, edited, or rejected:** Accepted all three revisions as starting points;
applied my own wording for Story 3 (added "completed_late" beyond what the table suggested).

---

### Prompt 3 — Implementation Context Block (VS Code Agent)

**Prompt:** Full project state, exact feature specification with due_state logic,
overdue filter behavior, storage constraint (in-memory only), and workflow rules
(one file per step, no whole-file rewrites).

**What it returned:** Agent changed four files in one pass — more than the one-step
plan called for.

**Accepted, edited, or rejected:**
- Inspected the full diff before accepting: confirmed `@computed_field` uses UTC
  correctly and `model_dump(exclude_unset=True)` handles null-clearing without an
  `if value is not None` guard.
- Flagged that only one test was added; deferred full test generation to Prompt 4.

---

### Prompt 4 — Additive Test Generation

**Prompt:** 10 named test functions to ADD without regenerating conftest.py or
touching existing tests. Included transition-chain constraint, PAST_DATE/FUTURE_DATE
semantics, and specific-value assertions.

**What it returned:** 10 test functions; 29 passed.

**Accepted, edited, or rejected:** Accepted all 10. Caught a date-fragility flaw
on review (hardcoded future dates expire after those calendar days). Issued Prompt 5.

---

### Prompt 5 — Date Fragility Fix

**Prompt:** Add `PAST_DATE` and `FUTURE_DATE` constants and replace all hardcoded
future dates in the new tests only.

**What it returned:** Focused diff — only imports, two constants, and date literals changed.

**Accepted, edited, or rejected:** Accepted in full. Re-ran pytest: 29 passed.
This is the clearest "my review changed the result" example for Feature 1.

---

## Feature 2: Task Comments

### Prompt 1 — Architecture Evaluation (Weak → Strong rewrite)

**Weak prompt (what this would have looked like):**
```
How should I add comments to my task tracker?
```

**What a weak prompt returns:** Generic suggestions — likely SQLite, an ORM,
or embedding comments inside tasks — without considering the existing codebase,
deadline, or test suite impact.

**Strong prompt:** Full architecture evaluation prompt with both user stories,
all four constraints (simplicity, testability, local run, familiarity), two
options required (in-memory vs. SQLite), trade-offs per option, and explicit
instruction not to choose.

**What it returned:** Two clearly separated options with folder structure, data
model sketches, and three trade-offs each. Did not choose — left the decision
to me as required.

**Accepted, edited, or rejected:**
- Used the trade-off analysis to write the ADR myself.
- Rejected Option B (SQLite) — reasoning recorded in mini-adr.md.
- Noted the orphaned-comment risk in Option A and decided to fix it explicitly
  in the cascade delete route.

---

### Prompt 2 — Implementation Context Block (VS Code Agent)

**Prompt:** Full project state including Feature 1 already complete, exact
architecture decisions, exact model and function signatures, exact route specs,
cascade delete requirement, and one-file-per-step workflow rule.

**What it returned:** Agent implemented models.py, comments_storage.py, three
new routes in main.py, cascade in DELETE /tasks/{id}, conftest.py update, and
test_comments.py in one pass — again more files than specified.

**Accepted, edited, or rejected:**
- Inspected `delete_comment` for the ownership check (`comment.task_id != task_id`) — present and correct.
- Confirmed conftest.py only added `_reset_comments()` to existing fixture, did not create a new one.
- Noted 3 missing test cases (GET missing task, DELETE missing task, DELETE nonexistent comment) — added them manually.
- All 40 passed after the additions.

---

### Prompt 3 — Frontend Comments Section

**Prompt:** Full current frontend state, three backend comment routes already
working, explicit "edit modal ONLY" scope, exact behavior per action (open,
add, delete), and explicit constraints including "Do NOT add comment count to
cards" and `type="button"` implied by the constraint list.

**What it returned:** Agent added the comments section correctly but violated
two constraints: added comment count badges to cards (explicitly forbidden) and
the Add Comment button lacked `type="button"` (causing it to submit the task form).

**Accepted, edited, or rejected:**
- Rejected the diff as-is.
- Issued a focused bug-fix prompt naming both violations exactly.
- After fix: comments load in modal, add/delete work, cards have no badges,
  modal is scrollable and Save Task still works.

---

### Prompt 4 — Frontend Bug Fix (follow-up correction after inspection)

**Prompt:** Named both bugs explicitly — the missing `type="button"` and the
forbidden comment count badges — with constraints to touch only those two things
and return a focused diff.

**What it returned:** Minimal diff removing the badge fetch and render code and
adding `type="button"`. No other changes.

**Accepted, edited, or rejected:** Accepted in full after verifying in the browser.