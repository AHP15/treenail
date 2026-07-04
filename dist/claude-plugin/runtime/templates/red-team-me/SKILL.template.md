<!--
============================================================================
TEMPLATE — red-team-me for a NON-SOFTWARE domain.  DO NOT USE THIS FILE AS-IS.
============================================================================
This is the domain-agnostic `red-team-me` adversarial pass with the
software-specific bits pulled out into {{PLACEHOLDERS}}. The method (prior-
calibration first, hunt failure modes per accepted decision, one risk per
concrete failure mode, ground it in evidence, don't propose fixes, don't pad,
write per-risk records) is fully general and left verbatim. Only the *examples*
and *paths* are parameterized.

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
     (see FILL-GUIDE.md) so this skill and any other red-team-me-* skills
     don't all fire on a bare "red-team me".

Pair this with the matching challenge-me-<domain> instance: challenge writes
the decisions, red-team hunts the risks against them. Same {{DOCS_ROOT}}.

Placeholders (full guidance + cross-domain examples in FILL-GUIDE.md):
  {{SKILL_NAME}} {{DOMAIN_NOUN}} {{DOMAIN_ADJ}} {{DOCS_ROOT}} {{SUBSCOPE_NOUN}}
  {{GROUND_TRUTH_SOURCE}} {{GROUND_TRUTH_SHORT}} {{MISCALIBRATION_EXAMPLE}}
  {{BLAST_RADIUS_EXAMPLE}} {{FAILURE_MODE_LENSES}}

The four that carry the domain's soul — spend your effort on these:
  {{FAILURE_MODE_LENSES}}  {{GROUND_TRUTH_SOURCE}}  {{MISCALIBRATION_EXAMPLE}}  {{BLAST_RADIUS_EXAMPLE}}
============================================================================
-->
---
name: {{SKILL_NAME}}
description: Adversarially stress-test the {{DOMAIN_ADJ}} decisions record by hunting for failure modes, hidden assumptions, and missing pieces. Use after the {{DOMAIN_ADJ}} decisions are drafted, before execution, or whenever the user wants an outside-view critique of {{DOMAIN_NOUN}} — even if they don't say "red-team me" in those words.
---

Read the decisions in scope and produce per-risk files. Adversarial — find what breaks, don't validate.

1. Scope. Project-level (`{{DOCS_ROOT}}/decisions/INDEX.md`) or {{SUBSCOPE_NOUN}}-level (`{{DOCS_ROOT}}/features/<{{SUBSCOPE_NOUN}}>/decisions/INDEX.md`). Risks live in the same scope under `risks/`.

2. Prior calibration. Read the latest retrospective for the scope (most recent file in `retrospectives/`). Its `Watch-for` is prior context — apply those failure-mode patterns first. Note past mis-calibrations to avoid ({{MISCALIBRATION_EXAMPLE}}). Absence of a retrospective is a greenfield signal, not an error.

3. Read `decisions/INDEX.md`. Load full D-NNN.md bodies only for the accepted decisions you're actively stress-testing. You don't need every decision's prose to think about failure modes — titles are usually enough to know what to load.

3b. Prior failures (advisory; optional). [OPTIONAL — delete this entire step if you won't run the Graphiti knowledge graph for this domain.] If the Graphiti graph is configured, query it per decision you're stress-testing for risks that materialized — or decisions that broke — elsewhere, including other {{SUBSCOPE_NOUN}}s:

   ```
   python3 ~/.treenail/scripts/graph_query.py {{DOCS_ROOT}} "<the decision being tested>" --scope all
   ```

   A hit on a related prior risk is a strong steer toward a concrete, evidence-backed failure mode rather than a speculative one (and it counters the over-prediction patterns the retrospective Watch-for warns about). Treat results as leads to investigate, not as risks to copy verbatim — re-derive the failure mode for *this* decision. If the script is silent (graph unavailable or no hits), continue with step 4 unchanged.

4. Hunt failure modes per accepted decision. For each, ask:
   - What hidden assumption makes this work?
   - What does this implicitly forbid that might be needed later?
   - What environment/dependency is it sensitive to?
   - What's the blast radius if it's wrong — {{BLAST_RADIUS_EXAMPLE}}?
   - What does it not cover that probably should be covered?
   Stress each decision against this domain's characteristic ways things break — {{FAILURE_MODE_LENSES}} — and raise any that genuinely bites. One risk per concrete failure mode — not abstract categories. Ground each in {{GROUND_TRUTH_SOURCE}} where you can: a failure you can actually point to in {{GROUND_TRUTH_SHORT}} beats a speculative one, and reading {{GROUND_TRUTH_SHORT}} is how you tell a real exposure from an imagined one. Where step 3b surfaced a real prior failure, prefer it over a speculative one.

5. For each risk:
   - Mint the next R-NNN by running `python3 ~/.treenail/scripts/mint_id.py <risks-dir> R` (e.g. `{{DOCS_ROOT}}/risks` or `{{DOCS_ROOT}}/features/<{{SUBSCOPE_NOUN}}>/risks`). The script executes the **ID reservation protocol** — filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision — and prints the claimed `R-NNN` and its (empty) file path. Don't take the max from INDEX; it may lag. (Fall back to the protocol by hand per CONVENTIONS-SPEC.md if `python3` is unavailable.)
   - Write the body into the claimed `risks/R-NNN.md` per the RISKS section of `CONVENTIONS-SPEC.md`. Disposition: `pending`. Date, Disposition rationale, and Action stay empty — `triage-risks` fills them in.
   - Set `Related decisions: D-NNN` linking to the source decision(s).
   - Add its INDEX line: append `R-NNN | pending | <severity> | <title>` to `risks/INDEX.md`, or after writing all risks run `python3 ~/.treenail/scripts/reindex.py <scope-dir> risks` (preferred when you wrote several).

6. Don't propose fixes. Triage is the next skill's job. Stay in failure-mode-finding mode.

7. Don't pad. If you don't see a meaningful risk in an area, say so. A short honest list beats a long ceremonial one.

8. On first run, ensure `{{DOCS_ROOT}}/CONVENTIONS-SPEC.md` exists; if not, copy `~/.treenail/conventions-spec.md` → `{{DOCS_ROOT}}/CONVENTIONS-SPEC.md` and `~/.treenail/conventions-examples.md` → `{{DOCS_ROOT}}/CONVENTIONS-EXAMPLES.md`.
