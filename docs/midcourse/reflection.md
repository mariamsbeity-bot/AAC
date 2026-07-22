# Reflection — Mid-Course Project

---

For this project I used two AI tools in different roles: Claude (claude.ai) for
planning, requirements design, and prompt engineering, and the VS Code agent
(Cursor/Copilot) for code generation inside the editor. Claude handled the
upstream workflow — user stories, ADR review, and designing the implementation
prompts. The VS Code agent handled file-level code generation from those prompts.

**Feature 1 — One moment AI helped:** The implementation context block prompt
was the most effective single prompt of the project. By providing the project
state, exact feature specification, decision already made (backend-computed
due_state), and explicit storage constraints, the VS Code agent correctly placed
`due_state` as a Pydantic `@computed_field` on `TaskResponse` using UTC and
handled the `model_dump(exclude_unset=True)` null-clearing path without an
accidental `if value is not None` guard that would have silently broken the
"PATCH due_date to null clears it" story. A vague prompt would have required
several correction rounds to reach the same result.

**Feature 1 — One moment AI slowed me down:** Despite the prompt specifying
"one file per step," the agent changed four files in one pass. This forced a
full multi-file diff inspection before running anything, which took longer than
a true incremental approach. The lesson: one-file constraints need to be enforced
by splitting the prompt into separate messages, not just stated as a rule.

**Feature 1 — One place where my review changed the result:** After the agent
generated 10 passing tests, I noticed hardcoded future dates (`"2026-07-30"`,
`"2026-08-15"`) that would flip to past dates after those calendar days, causing
correct code to fail. I issued a follow-up prompt to replace them with a computed
constant `FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()`. The fix
cost five minutes; catching it required reading the generated test bodies rather
than accepting the green run as proof.

**Feature 2 — One moment AI helped:** The architecture evaluation prompt produced
a clear two-option comparison with honest trade-offs that made the ADR straightforward
to write. Specifically, it flagged the orphaned-comment risk in Option A (comments
staying in the dict after a task is deleted) — a problem I had not considered. I
corrected this by specifying a cascade delete in the implementation prompt, which
the agent then implemented correctly and the break test confirmed.

**Feature 2 — One place where my review changed the result:** The frontend
implementation produced two bugs that the prompt had explicitly prevented. The
Add Comment button lacked `type="button"`, causing it to submit the task form
and trap the modal. The agent also added comment count badges to every card
despite the prompt containing "Do NOT add comment count to cards." Both were
caught by reading the diff and testing before accepting — not by the test suite,
since these were purely frontend behavioral bugs. A focused follow-up prompt fixed
both in a single minimal diff. This is the clearest example across both features
of why inspection cannot be skipped even when a green test run exists.