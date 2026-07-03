---
name: sequence-work
description: Order a task list into a phased plan that front-loads risk, ships value early, and respects dependencies. Use after decompose-plan, before implementation begins.
---

Read `tasks/INDEX.md` and produce a phased plan. Output is ephemeral — does not write files.

1. Scope. Project- or feature-level matches the `tasks/INDEX.md` you're reading.

2. Read `tasks/INDEX.md`. Identify all tasks with Status `todo` or `in_progress` (the open set — both are unfinished work that still needs ordering; an `in_progress` task is already started, so it sorts to the front of its phase). Load full T-NNN.md only when a sequencing decision turns on a task's nuance — specific dependency reasoning, ambiguous acceptance, unclear Mitigates linkage.

3. Group into phases:
   - **Phase 0 — risk front-loading.** Spike tasks first; tasks that mitigate `critical`/`high` risks; tasks unblocking later decisions. Read `risks/INDEX.md` to identify the high-severity set, then order *within* it by **Likelihood**: load the (few) high/critical risk bodies for their `Likelihood` field and front-load high-severity × high-likelihood mitigations first (the INDEX carries severity but not likelihood, so this is the one place the body is worth opening).
   - **Phase 1 — thin demo-able slice.** Smallest set that ships something testable end-to-end.
   - **Subsequent phases.** Layer in capabilities. Each phase ends on a demo-able milestone.

4. Within a phase, order by dependency. Tasks with no `Depends on` go first; respect transitive deps.

5. Output: phased list with one line per task (`T-NNN | <size> | <title>`). Note rationale for each phase boundary — what's now demo-able, what risk has been retired.

6. Phased plans are ephemeral. The user should copy anything durable into working notes before the session ends. `tasks/INDEX.md` is the durable state; the order over tasks is not.

7. Do not modify TASKS, the INDEX, decisions, or risks. Do not assign owners or calendar dates.
