---
name: extract-decisions
description: Reverse-engineer planning artifacts from an existing, undocumented codebase by anchoring in what shipped — inventory the built capabilities as `done` tasks (real git dates, verified Evidence anchors), factor the load-bearing decisions those tasks embody (as `accepted`), surface the standing risks visible in the tree (as `pending`), and flag the built-but-not-decided code no decision explains. Use to bootstrap `docs/` for a brownfield project that has code but no decision/risk/task records, before running the normal pipeline (`audit-artifacts` → `reconcile-status` → `triage-risks`). The code-reading, tasks-first counterpart of `challenge-me`. Reach for this whenever you're staring at an undocumented codebase and need its planning record reconstructed, even if the user doesn't name the skill.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Reconstruct the planning record an existing codebase never wrote. This is the brownfield way in: `challenge-me` elicits decisions about to be made; this recovers decisions already made and shipped.

In brownfield the most certain artifact is shipped code, and code is task-shaped. So **observe tasks-first** (what was built is the lowest-inference fact), then **write decisions-first** (tasks and risks hold foreign keys to decisions, so decisions must exist on disk first). The headline finding falls out of this: **built-but-not-decided** code that no decision explains.

**Reads:** the working tree, `git log` / `blame`, optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `decisions/`, `tasks/`, `risks/` records + INDEX files, and the conventions bootstrap.

## Phase A — Observe (read-only)

1. **Scope.** Project or one feature. Use only for undocumented code — if `decisions/` already covers the area, use `challenge-me` instead. Confirm scope with the user.

2. **Inventory built capabilities, git included.** Walk the tree by capability, not by file: manifests and lockfiles, entrypoints, config and environment, schema and migrations, module boundaries, trust boundaries (auth, validation, external calls), and the core abstractions everything imports. Each one becomes a provisional task with:
   - Evidence anchors you have verified resolve;
   - the **real landing date from git**;
   - a provisional *why* from commit or PR messages.

3. **Factor decisions by leverage.** Pull the hard-to-reverse choices out of the inventory. The mapping is many-to-many: Postgres runs through many tasks, and one auth task embodies several choices. Recurse into load-bearing sub-choices. Tag each choice **deliberate** (a commit weighs the tradeoff) or **emergent** (a pattern that just appeared).

4. **Prior art (optional, advisory).** `python3 ~/.treenail/scripts/graph_query.py docs "<area>" --scope all`. Hits are framing input only; this scope's code is the authority.

5. **Observed vs inferred.** Decision and Context are observed, so anchor them to paths, symbols, and config keys. Rationale is usually inferred: write `Rationale (inferred): …` where it is a guess. A short honest record beats a confident fictional one.

6. **Surface risks.** One per concrete failure mode visible in the tree (unbounded query, unauthenticated path, committed secret, single point of failure, untested critical path). Assess **Severity and Likelihood** now; the disposition is `triage-risks`' job. **An actively exploitable finding (a live secret, an open auth bypass) is an incident: tell the user immediately.**

7. **Find the orphans.** Built things (step 2) minus built things a decision explains (step 3) = built-but-not-decided. Classify each:
   - **Forgotten intent** → it deserves a decision; mint it in Phase B.
   - **Genuine accretion** → report only (a task must `Implements`/`Mitigates` something). Exception: if its unknown intent is a hazard (fragile, or might be deleted wrongly), record a standalone `pending` risk with no `Related decisions`.

## Phase B — Record (decisions → tasks → risks)

8. **Bootstrap.** `python3 ~/.treenail/scripts/bootstrap.py <scope-dir>`.

9. **Gate, then mint decisions.** Before writing, confirm with the user every extraction where the rationale *or the decision-hood itself* is a guess. Decisions have no status weaker than `accepted`, so the gate is the only place for doubt to go. Record an emergent but load-bearing pattern as `accepted`, saying plainly in the body that it appears emergent.
   - `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/decisions D`, body per spec § DECISIONS.
   - `Date:` today (the date it was accepted into the record). Context gives the git date since which the code has embodied it, and cites that code.

10. **Mint tasks.** `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/tasks T`, body per spec § TASKS:
    - `Status: done`; `Date done:` the **git landing date**;
    - `Size:` the capability's rough magnitude; `Implements: D-NNN`;
    - Acceptance checkable against the current tree; `Notes:` "brownfield-observed at extraction".
    - **Evidence:** anchor the decision's *invariant* as a behavior-naming `grep:<term> in <dir>/`, not an incidental exact symbol, so a faithful refactor doesn't cause false drift. Verify that every anchor resolves (`rg -l` / path check) before writing it. Explanation goes in Notes, never in Evidence.
    - Orphans get no task.

11. **Mint risks.** `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/risks R`, body per spec § RISKS: Severity and Likelihood from step 6, `Disposition: pending` with Date/rationale/Action empty, and `Related decisions` where one applies.

12. **Project.** `python3 ~/.treenail/scripts/reindex.py <scope-dir>`.

13. **Report**, headline first:
    - **Built-but-not-decided** — each orphan, marked forgotten intent (now a decision) or accretion (report-only, or escalated to a risk).
    - **Decisions** — ID, title, deliberate/emergent, confidence, and whether confirmed at the gate.
    - **Tasks** — ID, title, git date, and whether every anchor resolved.
    - **Mappings** — any non-obvious task↔decision links.
    - **Risks** — ID, severity, title.
    - **Left out** — anything deliberately left unrecorded.

    Caveat to state: at extraction every anchor verifies *by construction*. Their value is as a tripwire for later drift: "verified" means the invariant is still in the tree, not that the decision is faithfully realized.

## Never

- Assert intent nobody recorded, or mint an `accepted` decision that is really a guess without passing the gate.
- Invent a decision for accretion, or a task without an `Implements`/`Mitigates`.
- Record this pipeline's own modeling choices as decisions in the user's project. Those are tooling decisions, not decisions about their codebase.

## Next

- `audit-artifacts` → `reconcile-status` → `triage-risks`, in that order. The audit also catches a partial run (an empty claimed record, or a decision with no tasks): re-run it and continue from there. Go-forward decisions use `challenge-me`.
