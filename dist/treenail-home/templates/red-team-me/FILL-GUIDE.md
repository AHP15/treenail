# Fill guide — `red-team-me` for any domain

`red-team-me` is a **domain-agnostic adversarial pass** (apply the prior
retrospective's failure patterns first, hunt failure modes per accepted
decision, one risk per *concrete* failure mode, ground it in evidence, never
propose fixes, never pad, then write a per-risk record) wrapped around
**software examples**. The record schema (`Disposition / Severity / Related
decisions / …`) and every script (`mint_id.py`, `reindex.py`,
`graph_query.py`) already take a directory argument, so they work unchanged on
any records root. The template pulls the software-specific *examples* and
*paths* out into `{{PLACEHOLDERS}}`. Fill them and you have the same adversarial
pass for a different kind of work.

This is the counterpart to `challenge-me-<domain>`: challenge writes the
decisions, red-team hunts the risks against them. Point both at the same
`{{DOCS_ROOT}}` and reuse the same values for the shared placeholders.

---

## Instantiate in 4 steps

1. **Copy** the template to in your agent's skills directory — it must live directly
   under `skills/` so the `~/.treenail/...` paths resolve:
   ```
   mkdir -p ~/.claude/skills/red-team-me-<domain>
   cp ~/.treenail/templates/red-team-me/SKILL.template.md \
      ~/.claude/skills/red-team-me-<domain>/SKILL.md
   ```
2. **Fill** every `{{PLACEHOLDER}}` (paste a block from the four worked
   domains below, or write your own). Then `grep '{{' SKILL.md` — nothing
   should remain.
3. **Delete** the `<!-- TEMPLATE … -->` comment header, and delete step `3b`
   entirely if you won't run the Graphiti knowledge graph for this domain.
4. **Tighten the triggers** in the frontmatter `description` (see *Gotchas*)
   so this skill doesn't fight other `red-team-me-*` skills over a bare
   "red-team me", then start a fresh session and try your domain phrase.

The pass reads and writes the same **per-domain records root** (`{{DOCS_ROOT}}`,
e.g. `legal-docs/`) that `challenge-me-<domain>` wrote its decisions into — its
own risks, its own ID space, fully isolated from your software `docs/` and from
other domains.

---

## Placeholder reference

Four carry the domain's soul — spend your thinking here:

| Placeholder | What it is | Software original it replaces |
|---|---|---|
| `{{FAILURE_MODE_LENSES}}` | The domain's *characteristic ways things break* — the lenses that turn "hunt failure modes" from generic into pointed | "a concurrency race, a trust-boundary hole, a scale cliff, a data migration that strands state, a silent dependency change" |
| `{{GROUND_TRUTH_SOURCE}}` | What you *read to tell a real exposure from an imagined one* — the domain's source of truth | "the codebase and the traffic/usage data" |
| `{{MISCALIBRATION_EXAMPLE}}` | The over-prediction pattern to avoid, seeded into the calibration step | "over-predicting contention without traffic evidence" |
| `{{BLAST_RADIUS_EXAMPLE}}` | What "blast radius if it's wrong" concretely looks like here | "one request errors vs. the whole datastore is corrupted" |

The rest are naming, paths, and one-line examples — quick:

| Placeholder | What it is | Example |
|---|---|---|
| `{{SKILL_NAME}}` | Skill id (lowercase-hyphen), matches the folder | `red-team-me-legal` |
| `{{DOMAIN_NOUN}}` | Noun phrase for what's being critiqued (include the article) | `a litigation strategy` |
| `{{DOMAIN_ADJ}}` | Short adjective for the trigger phrases | `legal` |
| `{{DOCS_ROOT}}` | The per-domain records root directory (same as the challenge-me instance) | `legal-docs` |
| `{{SUBSCOPE_NOUN}}` | This domain's word for a "feature" / sub-unit | `matter` |
| `{{GROUND_TRUTH_SHORT}}` | Short noun for the fact source, used inline | `the case file` |

Keep `{{SKILL_NAME}}`, `{{DOMAIN_NOUN}}`, `{{DOMAIN_ADJ}}`, `{{DOCS_ROOT}}`,
`{{SUBSCOPE_NOUN}}`, `{{GROUND_TRUTH_SOURCE}}`, `{{GROUND_TRUTH_SHORT}}`
identical to the values you used in `challenge-me-<domain>` (swap `challenge`
for `red-team` in the skill id) so the pair stays coherent.

---

## Four ready-to-paste domains

Each block fills every placeholder for one domain. Copy the one closest to
your work, drop the values into `SKILL.md`, adjust to taste. (The shared
placeholders match the `challenge-me` fill guide's four domains.)

### Legal — case / litigation strategy
```
{{SKILL_NAME}}            = red-team-me-legal
{{DOMAIN_NOUN}}           = a litigation strategy
{{DOMAIN_ADJ}}            = legal
{{DOCS_ROOT}}             = legal-docs
{{SUBSCOPE_NOUN}}         = matter
{{GROUND_TRUTH_SOURCE}}   = the case file — pleadings, the evidentiary record, the controlling statutes and precedent, and the procedural posture
{{GROUND_TRUTH_SHORT}}    = the case file
{{FAILURE_MODE_LENSES}}   = a counter-move the adversary is actually incentivized to make, a missing element of proof, an inadmissible key exhibit, a limitations or jurisdictional bar, a judgment that turns out uncollectable, and an ethical or sanctions exposure
{{MISCALIBRATION_EXAMPLE}}= over-predicting a defense the adversary has no incentive or standing to raise
{{BLAST_RADIUS_EXAMPLE}}  = one argument gets struck vs. the whole claim is dismissed with prejudice
```

### Marketing — go-to-market / launch plan
```
{{SKILL_NAME}}            = red-team-me-gtm
{{DOMAIN_NOUN}}           = a go-to-market plan
{{DOMAIN_ADJ}}            = go-to-market
{{DOCS_ROOT}}             = gtm-docs
{{SUBSCOPE_NOUN}}         = campaign
{{GROUND_TRUTH_SOURCE}}   = prior-campaign performance data, the actual product capabilities, the funnel/analytics, and the real budget and channel constraints
{{GROUND_TRUTH_SHORT}}    = the performance data
{{FAILURE_MODE_LENSES}}   = a competitor's counter-move, a channel that saturates or spikes CAC, a message that lands internally but not in-market, a claim the product can't back, a funnel stage with no conversion trigger, and attribution you can't actually measure
{{MISCALIBRATION_EXAMPLE}}= over-predicting a price-war response a competitor has no margin to sustain
{{BLAST_RADIUS_EXAMPLE}}  = one channel underperforms vs. the whole launch misses and the brand takes the hit
```

### Research — empirical study design
```
{{SKILL_NAME}}            = red-team-me-research
{{DOMAIN_NOUN}}           = a research study design
{{DOMAIN_ADJ}}            = research
{{DOCS_ROOT}}             = research-docs
{{SUBSCOPE_NOUN}}         = study
{{GROUND_TRUTH_SOURCE}}   = the prior literature, any pilot data, the available sample/dataset, and the preregistration or protocol
{{GROUND_TRUTH_SHORT}}    = the protocol
{{FAILURE_MODE_LENSES}}   = an uncontrolled confound, an underpowered cell, a measure with poor validity or reliability, differential attrition, a result that won't generalize past the sample, a researcher-degrees-of-freedom / p-hacking path, and an ethics or consent gap
{{MISCALIBRATION_EXAMPLE}}= over-predicting a confound the design already randomizes away
{{BLAST_RADIUS_EXAMPLE}}  = one covariate is noisy vs. the central inference is unidentifiable and the study is unpublishable
```

### Writing — long-form / book plan
```
{{SKILL_NAME}}            = red-team-me-writing
{{DOMAIN_NOUN}}           = a book/manuscript plan
{{DOMAIN_ADJ}}            = narrative
{{DOCS_ROOT}}             = writing-docs
{{SUBSCOPE_NOUN}}         = arc
{{GROUND_TRUTH_SOURCE}}   = the outline, the series bible and character sheets, and the existing chapters and drafts
{{GROUND_TRUTH_SHORT}}    = the manuscript
{{FAILURE_MODE_LENSES}}   = a setup with no payoff (or a payoff with no setup), a sagging-middle pacing collapse, a continuity or timeline break, a POV violation, a genre promise left unkept, a protagonist the reader has no reason to follow, and a twist the text hasn't earned
{{MISCALIBRATION_EXAMPLE}}= over-predicting reader confusion the surrounding chapters already resolve
{{BLAST_RADIUS_EXAMPLE}}  = one scene drags vs. the ending doesn't land and the whole arc feels pointless
```

---

## Gotchas & notes

- **Keep the directory literally named `features/`.** Your prose can call the
  sub-unit a *matter / campaign / study / arc* (`{{SUBSCOPE_NOUN}}`), but the
  on-disk path stays `{{DOCS_ROOT}}/features/<name>/` — the optional knowledge
  graph derives its per-sub-scope grouping from that exact folder name.
- **Make the `description` triggers domain-specific.** All `red-team-me-*`
  skills would otherwise match a bare "red-team me". Phrase yours so it fires
  on the *domain* ("poke holes in this case strategy", "stress-test the launch
  plan for what breaks") and leave the bare phrase to the original software
  `red-team-me`.
- **It reads decisions the challenge-me instance wrote — instantiate that
  first.** With no `decisions/INDEX.md` in `{{DOCS_ROOT}}`, red-team has
  nothing to stress-test. Run `challenge-me-<domain>` (or draft decisions by
  hand) before this skill.
- **Step 2 (retrospectives) and step 3 (decisions) are already generic** — no
  fill needed beyond the one `{{MISCALIBRATION_EXAMPLE}}` seed. On a brand-new
  domain root the retrospective is simply absent; that's the greenfield path,
  not an error.
- **Stay in failure-finding mode.** Step 6 forbidding fixes is not domain
  flavor — it's the seam with `triage-risks`, which assigns
  `fix`/`mitigate`/`accept`/`defer` next. Don't fill the template in a way that
  smuggles remedies into the risk body.
- **The rest of the pipeline mostly comes along for free.** `triage-risks`,
  `reconcile-status`, `promote`, `retrospective`, `audit-artifacts`,
  `archive-cycle`, and `reindex` all operate on the same risk/decision records
  and take a scope dir — point them at `{{DOCS_ROOT}}` and they largely work.
  The exception is the **task-execution** skills (`decompose-plan`,
  `sequence-work`, `task-brief`): their `Evidence` anchors (`file:` / `grep:` /
  `symbol:` / `test:`) and "checkable against a diff" acceptance are
  code-specific. To take a domain all the way to execution you'd give those the
  same template treatment. Out of scope here; flagged so you know the boundary.
