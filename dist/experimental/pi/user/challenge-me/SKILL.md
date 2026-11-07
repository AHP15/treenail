---
name: challenge-me
description: Thoroughly interview the user about a plan or design, surfacing the implicit and unstated decisions hidden in their framing, resolving everything in order of leverage, and producing a decisions record at the end. Use this whenever the user wants to stress-test a plan, pressure-test a design, find the hidden decisions in a plan, or mentions "challenge me" or "grill me" — even if they don't use those exact words.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill ends in a scripted write (mint-id / reindex) that needs Python 3. Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the interview, so no completed work is lost to a mint-time failure.

Interview me systematically until ALL the important decisions are settled — including the ones I haven't noticed I'm making. Work through the decision tree in priority order, grow it as resolved decisions spawn new branches, and produce per-decision records at the end.

1. Scope first. Confirm what we're designing, what's already decided (don't re-litigate), and what's out of scope. Confirm project-level (`/docs/decisions/`) vs feature-level (`/docs/features/<feature>/decisions/`). List ALL decision branches roughly ordered, and confirm the ordering before diving in.

2. Prior calibration. Find the most recent retrospective for the scope by reading `retrospectives/INDEX.md` (newest date wins) and loading that one file. Its `Watch-for` is prior context about where this project has mis-calibrated — carry those patterns into step 4's leverage ordering and into your recommended-answer phrasing. Absence of a retrospective is a greenfield signal, not an error.

3. Existing constraints. Read `decisions/INDEX.md` for the scope to know what is already decided. Do not re-litigate. Load a specific D-NNN.md only if a current question genuinely depends on the body of a prior decision — INDEX titles are usually enough.

3b. Prior art (advisory; optional). If the Graphiti graph is configured, query it for semantically-related decisions and risks from **other** scopes — the "have we faced something like this before?" recall that INDEX (scoped, exact-match) can't give you:

   ```
   python3 ~/.treenail/scripts/graph_query.py docs "<the design problem in a sentence>" --scope all
   ```

   Run it per major decision branch from step 1. The output is one line per related prior record with its `[ID]`; pull the specific `<ID>.md` only if a hit looks genuinely relevant. Use these as **input to your leverage ordering and recommended answers** (e.g. a prior decision that broke, a risk that materialized elsewhere) — never as settled constraints; this scope still decides for itself. If the script prints nothing (graph unavailable, or no hits), proceed exactly as before — prior art is a bonus, not a dependency.

3c. Surface unstated premises. The most dangerous decisions are the ones already made implicitly and never spoken — single-tenant, synchronous, one writer, never-deleted, trusted caller, English-only, fits-in-memory. Before ordering, pass over the plan's framing and ask: what is this design assuming that it hasn't stated? Convert each premise into a decision node to ratify or reject — a premise is a candidate decision, never a settled fact. Scan the codebase the same way: where does the existing code already commit the new plan to something (a schema, a boundary, a concurrency model, an error contract)? Float each such commitment as a node to confirm or change — finding it in code tells you what is, never what should be, and the existing behavior may be exactly the miscalibration step 2 warned about. Splice these nodes into the ordering alongside the explicit branches from step 1.

4. Order by leverage. Hardest-to-reverse and most load-bearing decisions first — data model, trust boundaries, core abstractions. Cosmetic last. Resolve dependencies before dependents: don't ask about caching before persistence is decided. This ordering is not fixed: every resolved decision can spawn children and expose new dimensions (step 6b), so re-rank continuously as branches appear rather than treating step 1's list as the whole tree.

5. For each question:
   - Read the codebase to settle questions of fact — what's wired up, what the schema is, what test framework runs — and use what you find directly; don't make me confirm what the code already states. But reading code only ever tells you what is, not what should be: if what you find would resolve an open design choice rather than establish a fact, treat it as evidence, not a verdict. Surface it as your proposal ("the code currently does X here; I'd keep that because Y — does that work?") and record it like any other decision, noting the provenance (step 10). Reading the codebase replaces asking from ignorance; it never replaces surfacing for confirmation.
   - Otherwise, propose — never ask open-ended without a recommendation. The recommendation-plus-rationale that must accompany the question is a hard rule; see step 5b.
   - One question at a time.

5b. Rationale-first — hard rule (never surface a choice without a visible "why"). Before or alongside **every** question, the recommended answer plus a 1-2 sentence rationale ("this over the alternatives because…") MUST appear in the chat as prose. This holds unchanged when the agent also renders a structured selectable-option list (e.g. Claude Code's `AskUserQuestion`): the prose recommendation and rationale still appear in the message — terse per-option descriptions do NOT count as the rationale, and the recommended option is marked as such. A question that reaches the user without a preceding or accompanying rationale line is a defect, not a stylistic choice.

6. Handling responses:
   - Confirmed → mark resolved, move on.
   - Redirected → take the new direction, move on.
   - "I don't know" / "you decide" → recommendation stands as a tentative default, move on.
   - Pushback where you still believe you're right → push back once with your strongest reasoning, then defer. Don't re-argue.

6b. Expand the tree. Resolving a load-bearing decision is what makes its hidden subtree visible — so the tree must grow as you go, not just get walked. Each time a load-bearing decision resolves, before moving on, run two expansions and splice the results back into the leverage ordering (step 4):

Children: what new decisions did this answer just create? "Event sourcing" spawns snapshotting, event versioning, and replay strategy — nodes that didn't exist a minute ago.
Depth dimensions: stress the decision against each of — failure and partial failure, concurrency, scale limits, trust boundary, evolution/migration, observability — and surface any dimension it doesn't yet account for as a new node. This is principled depth, not padding (cf. step 9): only raise a dimension that genuinely bites this decision, and skip the ones that don't.

7. Flag invalidation. If a new decision contradicts an earlier one, say so explicitly and confirm whether to revise.

8. Checkpoint every ~5 resolved decisions with a brief summary so the user can catch drift.

9. Stop when remaining questions are low-leverage, when the user signals satisfaction, or when further resolution needs implementation feedback rather than more talking. Don't manufacture questions to seem thorough.

10. Write the records:
    - On first run: ensure `docs/CONVENTIONS-SPEC.md` exists. If not, copy [~/.treenail/conventions-spec.md](~/.treenail/conventions-spec.md) → `docs/CONVENTIONS-SPEC.md` and [~/.treenail/conventions-examples.md](~/.treenail/conventions-examples.md) → `docs/CONVENTIONS-EXAMPLES.md`, and write the spec version (the `Spec-version:` line from conventions-spec.md, e.g. `1`) into `docs/.treenail-version` so the scripts can dispatch on it later. Ensure `docs/decisions/INDEX.md` exists (touch if not).
    - For each resolved decision: mint the next D-NNN within scope by running `python3 ~/.treenail/scripts/mint_id.py <decisions-dir> D` (e.g. `docs/decisions` or `docs/features/<feature>/decisions`). The script executes the **ID reservation protocol** — filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision — and prints the claimed `D-NNN` and its (empty) file path. Never derive the max from INDEX; it may lag. (If `python3` is unavailable, fall back to the protocol by hand per CONVENTIONS-SPEC.md.)
    - Write the decision body into the claimed `decisions/D-NNN.md` per the DECISIONS section of `CONVENTIONS-SPEC.md`.
    - Add its INDEX line: either append `D-NNN | accepted | <title>` to `decisions/INDEX.md`, or after writing all records run `python3 ~/.treenail/scripts/reindex.py <scope-dir> decisions` (the canonical projection — preferred when you wrote several records).
    - Also output a brief inline summary in chat (one line per decision).