---
name: sequence-work
description: Order a task list into a phased plan that front-loads risk, ships value early, and respects dependencies. Use after decompose-plan, before implementation begins.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

Order the open tasks into phases that retire risk first and reach a demo-able slice early. The plan is ephemeral, output in chat only; `tasks/` stays the durable state.

**Reads:** `tasks/INDEX.md`, `risks/INDEX.md`, the bodies of high and critical risks, and task bodies only where ordering depends on nuance.
**Writes:** nothing.

## Steps

1. **Scope.** The scope of the `tasks/INDEX.md` you read.

2. **Open set.** Every `todo` and `in_progress` task. `in_progress` ones lead their phase.

3. **Phase 0: retire risk.** Spikes, tasks that unblock later decisions, and tasks that mitigate `high`/`critical` risks. Order those by **Likelihood** (high first). INDEX carries severity but not likelihood, so load those few risk bodies.

4. **Phase 1: thin slice.** The smallest set that ships something testable end to end.

5. **Later phases.** Add capabilities, each phase ending on a demo-able milestone.

6. **Dependencies.** Respect `Depends on`, transitively. Inside a phase, tasks with no dependencies go first. If a task depends on one in a later phase, pull the dependency forward. Never order a task before its dependency.

7. **Output.**
   ```
   Phase 0 — <milestone / risk retired>
   T-NNN | <size> | <title>
   ...
   Why this boundary: <what is now demo-able or de-risked>
   ```
   Then flag any task you could not place (blocked on an unfinished dependency, or with no clear phase).

## Never

- Modify any file.
- Assign owners or calendar dates.

## Next

- `task-brief` to start building. Remind the user to copy the phasing into working notes if they want to keep it.
