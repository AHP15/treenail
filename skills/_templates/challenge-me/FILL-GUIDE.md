# Fill guide — `challenge-me` for any domain

`challenge-me` is a **domain-agnostic interview method** (order by leverage,
surface the unspoken premises, one question at a time each with a
recommendation, grow the decision tree as answers spawn branches, then write a
per-decision record) wrapped around **software examples**. The record schema
(`Status / Context / Decision / Rationale / …`) and every script
(`mint_id.py`, `reindex.py`, `graph_query.py`) already take a directory
argument, so they work unchanged on any records root. The template pulls the
software-specific *examples* and *paths* out into `{{PLACEHOLDERS}}`. Fill
them and you have the same interview for a different kind of work.

---

## Instantiate in 4 steps

1. **Copy** the template to a sibling of `_shared` — it must live directly
   under `skills/` so the `~/.claude/skills/_shared/...` paths resolve:
   ```
   mkdir -p ~/.claude/skills/challenge-me-<domain>
   cp ~/.claude/skills/_templates/challenge-me/SKILL.template.md \
      ~/.claude/skills/challenge-me-<domain>/SKILL.md
   ```
2. **Fill** every `{{PLACEHOLDER}}` (paste a block from the four worked
   domains below, or write your own). Then `grep '{{' SKILL.md` — nothing
   should remain.
3. **Delete** the `<!-- TEMPLATE … -->` comment header, and delete step `3b`
   entirely if you won't run the Graphiti knowledge graph for this domain.
4. **Tighten the triggers** in the frontmatter `description` (see *Gotchas*)
   so this skill doesn't fight other `challenge-me-*` skills over a bare
   "challenge me", then start a fresh session and try your domain phrase.

The interview writes to a **per-domain records root** (`{{DOCS_ROOT}}`, e.g.
`legal-docs/`) — its own decisions, its own ID space, its own retrospectives,
fully isolated from your software `docs/` and from other domains.

---

## Placeholder reference

Four carry the domain's soul — spend your thinking here:

| Placeholder | What it is | Software original it replaces |
|---|---|---|
| `{{GROUND_TRUTH_SOURCE}}` | What you *read to settle facts* instead of asking — the domain's source of truth | "the codebase" |
| `{{UNSTATED_PREMISES}}` | The implicit assumptions that hide in this domain's plans | "single-tenant, synchronous, one writer, never-deleted, trusted caller, English-only, fits-in-memory" |
| `{{LEVERAGE_EXAMPLES}}` | The hardest-to-reverse, most load-bearing decisions to resolve first | "data model, trust boundaries, core abstractions" |
| `{{DEPTH_DIMENSIONS}}` | The axes to stress each decision against in step 6b | "failure and partial failure, concurrency, scale limits, trust boundary, evolution/migration, observability" |

The rest are naming, paths, and one-line examples — quick:

| Placeholder | What it is | Example |
|---|---|---|
| `{{SKILL_NAME}}` | Skill id (lowercase-hyphen), matches the folder | `challenge-me-legal` |
| `{{DOMAIN_NOUN}}` | Noun phrase for what's being planned (include the article) | `a litigation strategy` |
| `{{DOMAIN_ADJ}}` | Short adjective for the trigger phrases | `legal` |
| `{{DOCS_ROOT}}` | The per-domain records root directory | `legal-docs` |
| `{{SUBSCOPE_NOUN}}` | This domain's word for a "feature" / sub-unit | `matter` |
| `{{GROUND_TRUTH_SHORT}}` | Short noun for the fact source, used inline | `the case file` |
| `{{EXISTING_COMMITMENTS}}` | Where existing material already commits the plan | "a claim already pleaded, a forum already elected" |
| `{{LEVERAGE_DEP_EXAMPLE}}` | A "don't decide X before Y" dependency example | "don't argue damages before liability is fixed" |
| `{{CHILDREN_EXAMPLE}}` | A decision that visibly spawns child decisions | "'Sue in federal court' spawns basis, venue, removal" |

---

## Four ready-to-paste domains

Each block fills every placeholder for one domain. Copy the one closest to
your work, drop the values into `SKILL.md`, adjust to taste.

### Legal — case / litigation strategy
```
{{SKILL_NAME}}          = challenge-me-legal
{{DOMAIN_NOUN}}         = a litigation strategy
{{DOMAIN_ADJ}}          = legal
{{DOCS_ROOT}}           = legal-docs
{{SUBSCOPE_NOUN}}       = matter
{{GROUND_TRUTH_SOURCE}} = the case file — pleadings, key documents, the controlling statutes and precedent, and the client's stated goals
{{GROUND_TRUTH_SHORT}}  = the case file
{{UNSTATED_PREMISES}}   = solvent defendant, admissible evidence, a single jurisdiction, the client will ultimately settle, the limitations period hasn't run, liability implies collectability, our client is the sympathetic party
{{EXISTING_COMMITMENTS}}= a claim already pleaded, a forum already elected, a theory of liability, a demand already sent, the retainer's scope
{{LEVERAGE_EXAMPLES}}   = forum and jurisdiction, the theory of the case, who is named as a party, and the remedy sought
{{LEVERAGE_DEP_EXAMPLE}}= don't argue the damages model before the liability theory is fixed
{{CHILDREN_EXAMPLE}}    = "Sue in federal court" spawns the diversity-vs-federal-question basis, venue, and whether the other side can remove or transfer
{{DEPTH_DIMENSIONS}}    = the adversary's likely response, burden and standard of proof, cost and time to trial, appeal exposure, collectability/enforceability of a judgment, and reputational or ethical risk
```

### Marketing — go-to-market / launch plan
```
{{SKILL_NAME}}          = challenge-me-gtm
{{DOMAIN_NOUN}}         = a go-to-market plan
{{DOMAIN_ADJ}}          = go-to-market
{{DOCS_ROOT}}           = gtm-docs
{{SUBSCOPE_NOUN}}       = campaign
{{GROUND_TRUTH_SOURCE}} = the brief, the positioning and brand guidelines, prior-campaign performance data, and the actual product capabilities
{{GROUND_TRUTH_SHORT}}  = the brief
{{UNSTATED_PREMISES}}   = one buyer persona, the buyer is the user, a single channel carries the launch, what resonates internally resonates in-market, demand exists and only needs capturing, English-only, the budget is fixed
{{EXISTING_COMMITMENTS}}= a launch date already promised, a price already published, a channel already contracted, a tagline already in market, a named target segment
{{LEVERAGE_EXAMPLES}}   = the target segment, the core positioning/message, the pricing and packaging, and the primary channel
{{LEVERAGE_DEP_EXAMPLE}}= don't pick channels and creative before the segment and positioning are fixed
{{CHILDREN_EXAMPLE}}    = "Lead with a free tier" spawns the conversion trigger, where the paywall sits, and how you message the upgrade
{{DEPTH_DIMENSIONS}}    = competitor reaction, channel saturation and CAC, budget and time limits, brand/positioning consistency, how it scales past the beachhead segment, and measurability/attribution
```

### Research — empirical study design
```
{{SKILL_NAME}}          = challenge-me-research
{{DOMAIN_NOUN}}         = a research study design
{{DOMAIN_ADJ}}          = research
{{DOCS_ROOT}}           = research-docs
{{SUBSCOPE_NOUN}}       = study
{{GROUND_TRUTH_SOURCE}} = the research question, the prior literature, any pilot data, the available sample/dataset, and any preregistration or protocol
{{GROUND_TRUTH_SHORT}}  = the protocol
{{UNSTATED_PREMISES}}   = the sample is representative, the measure is valid and reliable, the effect is stable across contexts, no meaningful attrition, one analysis was always the plan, correlation implies causation, the manipulation actually moves the construct
{{EXISTING_COMMITMENTS}}= a hypothesis already registered, a measure already chosen, a sample already collected, an analysis already named, the IRB's approved scope
{{LEVERAGE_EXAMPLES}}   = the research question and hypothesis, the design (experimental vs. observational), the operationalized measures, and the analysis/inference plan
{{LEVERAGE_DEP_EXAMPLE}}= don't choose the statistical test before the design and the measurement scale are fixed
{{CHILDREN_EXAMPLE}}    = "Run a between-subjects RCT" spawns the randomization procedure, power/sample-size, and how attrition and dropouts are handled
{{DEPTH_DIMENSIONS}}    = confounds and alternative explanations, statistical power, ethics and consent, generalizability, replicability/preregistration, and measurement validity
```

### Writing — long-form / book plan
```
{{SKILL_NAME}}          = challenge-me-writing
{{DOMAIN_NOUN}}         = a book/manuscript plan
{{DOMAIN_ADJ}}          = narrative
{{DOCS_ROOT}}           = writing-docs
{{SUBSCOPE_NOUN}}       = arc
{{GROUND_TRUTH_SOURCE}} = the outline, the series bible and character sheets, existing chapters and drafts, and the pitch or synopsis
{{GROUND_TRUTH_SHORT}}  = the manuscript
{{UNSTATED_PREMISES}}   = a single POV, linear chronology, the protagonist is sympathetic, one genre's conventions apply, the reader knows what the author knows, the ending is fixed, the theme is obvious from the plot
{{EXISTING_COMMITMENTS}}= a POV already chosen, a timeline already established, a character already killed off, a promise already made to the reader, a premise already pitched
{{LEVERAGE_EXAMPLES}}   = POV and narrative distance, tense and timeline structure, the central dramatic question, and who the protagonist is
{{LEVERAGE_DEP_EXAMPLE}}= don't plot individual scenes before the central dramatic question and POV are fixed
{{CHILDREN_EXAMPLE}}    = "Unreliable first-person narrator" spawns when the unreliability is revealed, what the reader is allowed to know, and how other characters' truth reaches the page
{{DEPTH_DIMENSIONS}}    = reader expectation and genre promise, pacing and momentum, internal consistency/continuity, setup-and-payoff, theme coherence, and how it holds up on a re-read
```

---

## Gotchas & notes

- **Keep the directory literally named `features/`.** Your prose can call the
  sub-unit a *matter / campaign / study / arc* (`{{SUBSCOPE_NOUN}}`), but the
  on-disk path stays `{{DOCS_ROOT}}/features/<name>/` — the optional knowledge
  graph derives its per-sub-scope grouping from that exact folder name.
- **Make the `description` triggers domain-specific.** All `challenge-me-*`
  skills would otherwise match a bare "challenge me". Phrase yours so it fires
  on the *domain* ("stress-test this case strategy", "grill me on the launch
  plan") and leave the bare phrase to the original software `challenge-me`.
- **Step 2 (retrospectives) and step 3 (existing decisions) are already
  generic** — no fill needed. On a brand-new domain root both are simply
  empty; that's the greenfield path, not an error.
- **Optional: domain-flavored exemplars.** Step 10 copies the shared
  `conventions-examples.md`, whose examples are software (Postgres, OAuth).
  Harmless (it's only read when a human tailors conventions), but if you want,
  hand-edit `{{DOCS_ROOT}}/CONVENTIONS-EXAMPLES.md` after first run to show a
  decision from your domain. The *spec* needs no change.
- **The rest of the pipeline mostly comes along for free.** `red-team-me`,
  `triage-risks`, `promote`, `reconcile-status`, `retrospective`,
  `audit-artifacts`, `archive-cycle`, and `reindex` all operate on the same
  decision/risk records and take a scope dir — point them at `{{DOCS_ROOT}}`
  and they largely work. The exception is the **task-execution** skills
  (`decompose-plan`, `sequence-work`, `task-brief`): their task `Evidence`
  anchors (`file:` / `grep:` / `symbol:` / `test:`) and their "checkable
  against a diff" acceptance are code-specific. To take a domain all the way to
  execution you'd give those the same template treatment — replacing the code
  anchor with your domain's "proof it actually happened" (a filed document, a
  shipped asset, a collected dataset). Out of scope here; flagged so you know
  the boundary.
