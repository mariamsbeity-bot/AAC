# Mini-ADR — Feature Implementation Decisions

---

## Feature 1: Due Dates + Overdue Filter

We are adding a new feature to our task management API that will enable due dates
and due states (e.g., tracking if a task is overdue or completed late). We must
choose how to handle and store this new data. A basic in-memory storage method is
used in our current application. Due to an impending deadline, we have to decide
between moving to a persistent database (Option B) or continuing with this
in-memory method (Option A).

We decided to keep the in-memory dictionary and extend it with `due_date` as a
stored field and `due_state` as a value computed at response time. We chose this
because it is the simplest option, it keeps our existing pytest suite and reset
fixture working without changes, the app still runs locally with a single uvicorn
command, and the whole team is already familiar with the current storage code from
Modules 2 and 3.

During planning we rejected or corrected two AI suggestions. First, the AI proposed
a SQLite-based storage layer (Option B); we rejected it because rewriting the storage
foundation a week before the deadline added risk without improving what the project
actually assesses. Second, the AI originally assumed that Done tasks are never
flagged regardless of their due date; we corrected this so that Done tasks past
their due date are flagged as "completed late" instead of overdue.

If the project grew, the first risk to address is data loss: in-memory storage wipes
all tasks on every server restart, so persistence would become necessary. The second
is the `due_state` definition, which uses the server's UTC date; with real users in
different timezones, "overdue" would need a clearer timezone rule.

---

## Feature 2: Task Comments

We are adding task comments to the API — the ability to add, list, and delete
text notes attached to a task. We must choose how to store comment data alongside
the existing in-memory task storage. The main options are to embed comments as a
list inside each TaskResponse, or to use a separate in-memory dictionary keyed
by comment_id.

We decided to use a separate in-memory dictionary in a new file
`app/comments_storage.py`, keying comments by `comment_id` and storing `task_id`
as a field on each comment object for filtering and ownership checks. We chose
this because it is the simplest option, it keeps the existing task storage and
all 29 existing tests completely untouched, the storage pattern is already
familiar from `app/storage.py`, and the diff is tightly isolated to two new
files and three new routes without touching anything that already works.

During planning we rejected or corrected two AI suggestions. First, the AI proposed
a SQLite-based storage layer with two tables (Option B); we rejected it because
rewriting the entire storage foundation and re-verifying all 29 existing tests four
days before the deadline added massive risk that the feature alone did not justify.
Second, the AI initially left the orphaned-comment problem unresolved, where
comments would remain stuck in the dictionary if their parent task was deleted;
we corrected this so that deleting a task explicitly cascades to delete all
associated comments, manually maintaining referential integrity in the route.

If the project grew, the cascade delete handled manually in the route would become
error-prone at scale — a real database with foreign key constraints would handle
this more reliably. The second risk is that the in-memory storage for both tasks
and comments wipes on every server restart, which becomes impractical once real
users depend on the data.