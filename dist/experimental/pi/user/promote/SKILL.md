---
name: promote
description: Promote a feature-level decision or risk to project-level scope. Copies the record up, freezes the feature-level source with a cross-scope link, and surfaces related records as candidates. On-demand only — the user decides what to promote; this skill executes the mechanics correctly across files and indices.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill ends in a scripted write (mint-id / reindex) that needs Python 3. Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the interview, so no completed work is lost to a mint-time failure.

Take a feature-level D-NNN or R-NNN and execute the cross-scope promotion. One record per invocation.

1. Confirm input. The user invokes with `feature:<feature>/D-NNN` or `feature:<feature>/R-NNN`. Refuse if the source is at project-level, already `promoted`, `superseded`, or `deprecated`.

2. Load full source record (`docs/features/<feature>/decisions/D-NNN.md` or `risks/R-NNN.md`).

3. Mint the destination ID by running `python3 ~/.treenail/scripts/mint_id.py docs/decisions D` (or `docs/risks R`) — the **project-level** dir, since promotion targets project scope. The script executes the **ID reservation protocol** (filesystem-arbitrated max over the project-level active + archive files, atomic no-clobber claim, retry on collision) and prints the claimed destination ID and path. Do not derive the max from INDEX; it may lag. (Fall back to the protocol by hand if `python3` is unavailable.)

4. **Decisions**:
   - Write `docs/decisions/D-MMM.md` with the source's body content. Status: `accepted`. Add `Promoted from: feature:<feature>/D-NNN`. Rewrite every bare intra-scope ID in the copy to qualified form (`feature:<feature>/D-003`) — left bare it would resolve to an unrelated project record (spec § SCOPE, qualified references).
   - Append to project-level `decisions/INDEX.md`: `D-MMM | accepted | <title>`.
   - Edit feature-level D-NNN.md: Status → `promoted`, add `Date promoted: <today>` and `Promoted to: project:D-MMM`. Body otherwise frozen.
   - Update feature-level `decisions/INDEX.md` line: status `promoted`, append `(→ project:D-MMM)` to title.

5. **Risks**:
   - Write `docs/risks/R-MMM.md` with body, add `Promoted from: feature:<feature>/R-NNN`. Disposition unchanged. Qualify every bare ID in `Related decisions` and `Action` (`feature:<feature>/D-003`, `feature:<feature>/T-007`); `audit-artifacts` warns on any that were copied bare.
   - Append to project-level `risks/INDEX.md` line.
   - Edit feature-level R-NNN.md: add `Promoted to: project:R-MMM`. Body otherwise frozen.
   - Update feature-level `risks/INDEX.md` line (no status change — risks have no Status field; the `Promoted to` field is the marker).

6. Surface candidates. Scan the source's **explicit** links — `Related decisions`, `Mitigates`, mitigating tasks, `Supersedes` chain — and recommend other records the user may want to promote next. Then, if the Graphiti graph is configured, widen the net with **semantic** candidates the explicit links miss — feature-level records elsewhere that resemble this one and may deserve the same project-level promotion:

   ```
   python3 ~/.treenail/scripts/graph_query.py docs "<source title/description>" --scope all
   ```

   Present both sets clearly labelled (explicit vs semantic-advisory). Do not promote any of them automatically — promotion is one record per invocation, and the user decides. If the graph is unavailable the step simply yields no extra candidates.

7. Tasks do not migrate. Existing tasks keep their feature-level `Implements`/`Mitigates` references; the cross-scope chain resolves them. New tasks should target the project-level ID.

8. Recommend running the `audit-artifacts` skill after the promotion to verify symmetric links.

9. Conventions. Reference `docs/CONVENTIONS-SPEC.md`.
