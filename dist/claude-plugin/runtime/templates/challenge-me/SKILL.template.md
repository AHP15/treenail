<!--
============================================================================
TEMPLATE — challenge-me for a NON-SOFTWARE domain.  DO NOT USE THIS FILE AS-IS.
============================================================================
This is the domain-agnostic `challenge-me` interview with the software-specific
bits pulled out into {{PLACEHOLDERS}}. The method (leverage ordering, surfacing
unstated premises, one-question-at-a-time-with-a-recommendation, growing the
decision tree, the decision-record output) is fully general and left verbatim.
Only the *examples* and *paths* are parameterized.

To create a working skill for a new domain:

  1. Copy this file to your agent's skills directory:
         ~/.claude/skills/<skill-name>/SKILL.md
     It MUST live directly under skills/ (not under _templates/) so the
     ~/.treenail/... script paths resolve from the instance.
  2. Replace every {{PLACEHOLDER}} below. FILL-GUIDE.md has per-slot guidance
     and a table of four fully-worked domains you can paste from.
     When done, search the file for "{{" — none should remain.
  3. Delete this comment header.
  4. Make the frontmatter `description` triggers SPECIFIC to your domain
     (see FILL-GUIDE.md) so this skill and any other challenge-me-* skills
     don't all fire on a bare "challenge me".

Placeholders (full guidance + cross-domain examples in FILL-GUIDE.md):
  {{SKILL_NAME}} {{DOMAIN_NOUN}} {{DOMAIN_ADJ}} {{DOCS_ROOT}} {{SUBSCOPE_NOUN}}
  {{GROUND_TRUTH_SOURCE}} {{GROUND_TRUTH_SHORT}} {{UNSTATED_PREMISES}}
  {{EXISTING_COMMITMENTS}} {{LEVERAGE_EXAMPLES}} {{LEVERAGE_DEP_EXAMPLE}}
  {{CHILDREN_EXAMPLE}} {{DEPTH_DIMENSIONS}}

The four that carry the domain's soul — spend your effort on these:
  {{GROUND_TRUTH_SOURCE}}  {{UNSTATED_PREMISES}}  {{LEVERAGE_EXAMPLES}}  {{DEPTH_DIMENSIONS}}
============================================================================
-->
---
name: {{SKILL_NAME}}
description: Thoroughly interview the user about {{DOMAIN_NOUN}}, surfacing the implicit and unstated decisions hidden in their framing, resolving everything in order of leverage, and producing a decisions record at the end. Use this whenever the user wants to stress-test {{DOMAIN_NOUN}}, pressure-test a {{DOMAIN_ADJ}} plan, find the hidden decisions in {{DOMAIN_NOUN}}, or says "challenge me"/"grill me" about {{DOMAIN_ADJ}} work — even if they don't use those exact words.
---

Interview me systematically until ALL the important decisions are settled — including the ones I haven't noticed I'm making. Work through the decision tree in priority order, grow it as resolved decisions spawn new branches, and produce per-decision records at the end.

1. Scope first. Confirm what we're planning, what's already decided (don't re-litigate), and what's out of scope. Confirm project-level (`{{DOCS_ROOT}}/decisions/`) vs {{SUBSCOPE_NOUN}}-level (`{{DOCS_ROOT}}/features/<{{SUBSCOPE_NOUN}}>/decisions/`). List ALL decision branches roughly ordered, and confirm the ordering before diving in.

2. Prior calibration. Find the most recent retrospective for the scope by reading `retrospectives/INDEX.md` (newest date wins) and loading that one file. Its `Watch-for` is prior context about where this work has mis-calibrated — carry those patterns into step 4's leverage ordering and into your recommended-answer phrasing. Absence of a retrospective is a greenfield signal, not an error.

3. Existing constraints. Read `decisions/INDEX.md` for the scope to know what is already decided. Do not re-litigate. Load a specific D-NNN.md only if a current question genuinely depends on the body of a prior decision — INDEX titles are usually enough.

3b. Prior art (advisory; optional). [OPTIONAL — delete this entire step if you won't run the Graphiti knowledge graph for this domain.] If the Graphiti graph is configured, query it for semantically-related decisions and risks from **other** scopes — the "have we faced something like this before?" recall that INDEX (scoped, exact-match) can't give you:

   ```
   python3 ~/.treenail/scripts/graph_query.py {{DOCS_ROOT}} "<the problem in a sentence>" --scope all
   ```

   Run it per major decision branch from step 1. The output is one line per related prior record with its `[ID]`; pull the specific `<ID>.md` only if a hit looks genuinely relevant. Use these as **input to your leverage ordering and recommended answers** (e.g. a prior decision that broke, a risk that materialized elsewhere) — never as settled constraints; this scope still decides for itself. If the script prints nothing (graph unavailable, or no hits), proceed exactly as before — prior art is a bonus, not a dependency.

3c. Surface unstated premises. The most dangerous decisions are the ones already made implicitly and never spoken — {{UNSTATED_PREMISES}}. Before ordering, pass over the plan's framing and ask: what is this {{DOMAIN_ADJ}} plan assuming that it hasn't stated? Convert each premise into a decision node to ratify or reject — a premise is a candidate decision, never a settled fact. Scan {{GROUND_TRUTH_SOURCE}} the same way: where does the existing material already commit the new plan to something ({{EXISTING_COMMITMENTS}})? Float each such commitment as a node to confirm or change — finding it in {{GROUND_TRUTH_SHORT}} tells you what is, never what should be, and the existing state may be exactly the miscalibration step 2 warned about. Splice these nodes into the ordering alongside the explicit branches from step 1.

4. Order by leverage. Hardest-to-reverse and most load-bearing decisions first — {{LEVERAGE_EXAMPLES}}. Cosmetic last. Resolve dependencies before dependents: {{LEVERAGE_DEP_EXAMPLE}}. This ordering is not fixed: every resolved decision can spawn children and expose new dimensions (step 6b), so re-rank continuously as branches appear rather than treating step 1's list as the whole tree.

5. For each question:
   - Read {{GROUND_TRUTH_SOURCE}} to settle questions of fact — what's already fixed, what the constraints are, what's already been committed — and use what you find directly; don't make me confirm what {{GROUND_TRUTH_SHORT}} already states. But reading {{GROUND_TRUTH_SHORT}} only ever tells you what is, not what should be: if what you find would resolve an open choice rather than establish a fact, treat it as evidence, not a verdict. Surface it as your proposal ("{{GROUND_TRUTH_SHORT}} currently says X here; I'd keep that because Y — does that work?") and record it like any other decision, noting the provenance (step 10). Reading {{GROUND_TRUTH_SHORT}} replaces asking from ignorance; it never replaces surfacing for confirmation.
   - Otherwise, state your recommended answer and reasoning in 1-2 sentences, then ask if it works. Never open-ended without a proposal.
   - One question at a time.

6. Handling responses:
   - Confirmed → mark resolved, move on.
   - Redirected → take the new direction, move on.
   - "I don't know" / "you decide" → recommendation stands as a tentative default, move on.
   - Pushback where you still believe you're right → push back once with your strongest reasoning, then defer. Don't re-argue.

6b. Expand the tree. Resolving a load-bearing decision is what makes its hidden subtree visible — so the tree must grow as you go, not just get walked. Each time a load-bearing decision resolves, before moving on, run two expansions and splice the results back into the leverage ordering (step 4):

Children: what new decisions did this answer just create? {{CHILDREN_EXAMPLE}} — nodes that didn't exist a minute ago.
Depth dimensions: stress the decision against each of — {{DEPTH_DIMENSIONS}} — and surface any dimension it doesn't yet account for as a new node. This is principled depth, not padding (cf. step 9): only raise a dimension that genuinely bites this decision, and skip the ones that don't.

7. Flag invalidation. If a new decision contradicts an earlier one, say so explicitly and confirm whether to revise.

8. Checkpoint every ~5 resolved decisions with a brief summary so the user can catch drift.

9. Stop when remaining questions are low-leverage, when the user signals satisfaction, or when further resolution needs real-world feedback rather than more talking. Don't manufacture questions to seem thorough.

10. Write the records:
    - On first run: ensure `{{DOCS_ROOT}}/CONVENTIONS-SPEC.md` exists. If not, copy `~/.treenail/conventions-spec.md` → `{{DOCS_ROOT}}/CONVENTIONS-SPEC.md` and `~/.treenail/conventions-examples.md` → `{{DOCS_ROOT}}/CONVENTIONS-EXAMPLES.md`. Ensure `{{DOCS_ROOT}}/decisions/INDEX.md` exists (touch if not).
    - For each resolved decision: mint the next D-NNN within scope by running `python3 ~/.treenail/scripts/mint_id.py <decisions-dir> D` (e.g. `{{DOCS_ROOT}}/decisions` or `{{DOCS_ROOT}}/features/<{{SUBSCOPE_NOUN}}>/decisions`). The script executes the **ID reservation protocol** — filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision — and prints the claimed `D-NNN` and its (empty) file path. Never derive the max from INDEX; it may lag. (If `python3` is unavailable, fall back to the protocol by hand per CONVENTIONS-SPEC.md.)
    - Write the decision body into the claimed `decisions/D-NNN.md` per the DECISIONS section of `CONVENTIONS-SPEC.md`.
    - Add its INDEX line: either append `D-NNN | accepted | <title>` to `decisions/INDEX.md`, or after writing all records run `python3 ~/.treenail/scripts/reindex.py <scope-dir> decisions` (the canonical projection — preferred when you wrote several records).
    - Also output a brief inline summary in chat (one line per decision).
