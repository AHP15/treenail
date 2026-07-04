---
name: triage-risks
description: Reconcile decisions with the risk list by assigning each pending risk a disposition (fix, mitigate, accept, defer) and updating decisions accordingly. Use after red-team-me, before implementation planning.
---
> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead.

Read `risks/INDEX.md` and `decisions/INDEX.md`. For each risk with `Disposition: pending`, decide and write back.

1. Scope. Match `risks/` and `decisions/` scope (project- or feature-level).

2. Identify pending risks. Read `risks/INDEX.md` and list every line whose disposition column is `pending`.

3. For each pending risk, in order:
   a. Load `risks/R-NNN.md` (full body) and any `Related decisions: D-NNN.md` cited (full body — you need the rationale to triage well).
   b. Choose disposition. Weigh **Severity × Likelihood** (both are on the risk body you just loaded): high severity *and* high likelihood pushes toward `fix`/`mitigate` (address now); high severity but low likelihood usually fits `defer` with a real trigger, or `accept`; low/low is usually `accept`. At equal severity, Likelihood is what separates "must address now" from "watch for" — don't let it sit unused.
      - **fix**: change a decision so the failure mode disappears. Old decision → `superseded`; new decision created with `Supersedes` link. Risk Action references the new decision.
      - **mitigate**: keep the decision; add a guard. Action describes the guard narratively. `decompose-plan` will mint task IDs and backfill them later.
      - **accept**: live with it. Action is a rationale for why blast radius is acceptable, or "none".
      - **defer**: revisit at a future trigger. Action **must** include an observable trigger (threshold, date, event). "When it becomes a problem" is not a trigger.
   c. Update `risks/R-NNN.md`: Disposition (chosen), Date (today, ISO), Disposition rationale, Action.
   d. Update `risks/INDEX.md` line for this risk: replace `pending` with the chosen disposition. For `mitigate`, leave the `[tasks: ...]` suffix to `decompose-plan`.

4. **fix flow** — when supersession is required:
   - Edit the old D-NNN.md: Status → `superseded`, add `Date superseded: <today>` and `Superseded by: D-MMM`. Do not edit Context/Decision/Rationale (historical record).
   - Update `decisions/INDEX.md` line: change status to `superseded`, append `(→ D-MMM)` to title.
   - Mint D-MMM by running `python3 ~/.treenail/scripts/mint_id.py <decisions-dir> D` (the **ID reservation protocol**: filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision — not from INDEX). It prints the claimed `D-MMM` and its file path. Write the body into `decisions/D-MMM.md` per CONVENTIONS-SPEC.md with `Supersedes: D-NNN`. (Fall back to the protocol by hand if `python3` is unavailable.)
   - Add D-MMM's INDEX line — append it, or run `python3 ~/.treenail/scripts/reindex.py <scope-dir> decisions` to reproject the whole decisions index (which also refreshes the superseded D-NNN line from the two bullets above, so you needn't hand-edit it).
   - In the risk's Action field, link to the new decision: e.g. "Superseded by D-MMM (replaces the failure mode)".
   - The new decision D-MMM is itself unexamined — a supersession can introduce its own failure modes. Recommend the `red-team-me` skill scoped to D-MMM before it ships. (`reconcile-status`'s "un-red-teamed decision" smell will catch it later as a backstop, but flag it now rather than waiting.)

4a. **Re-triage flow** — dispositions evolve in place (no supersession; a
   risk is durable, its disposition is current state). Besides fresh
   `pending` risks, this skill also re-dispositions an existing risk when
   `reconcile-status` surfaces a judgment smell on it:
   - **Mitigation complete** (a `mitigate` risk whose every mitigating task
     is `done`): if the shipped guard makes the residual acceptable, change
     `Disposition: mitigate → accept`, set Date (today), and write an Action
     rationale citing the tasks (e.g. "Residual acceptable — mitigated by
     T-031, T-032, both shipped"). Update the INDEX line's disposition
     column. This is what gives a completed mitigation a way *out* of the
     active set: a `mitigate` risk has no reap path, but once it is `accept`
     it reaps at the next retrospective via `archive-cycle`. If the residual
     is *not* acceptable (the mitigation reduces but doesn't close it), leave
     it `mitigate` — it is a permanent standing concern by choice.
   - **Thin defer** (a high/critical `defer` whose trigger is vacuous): add a
     real observable trigger to the Action — a threshold, a date, or a
     concrete event — or, if there is genuinely no future trigger, it was an
     `accept`, so re-disposition it to `accept` with the honest rationale.
   Re-triage never supersedes and never deletes; it edits Disposition, Date,
   rationale, and Action in place and updates the one INDEX line.

5. After triaging all pending risks, recommend running the `audit-artifacts` skill before `decompose-plan`.

6. Conventions. Reference `docs/CONVENTIONS-SPEC.md`. If missing, copy from [~/.treenail/conventions-spec.md](~/.treenail/conventions-spec.md) and [~/.treenail/conventions-examples.md](~/.treenail/conventions-examples.md) to `docs/`.
