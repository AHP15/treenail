// The seven-skill planning pipeline (D-012 centerpiece content), as plain
// data so it is the SINGLE source rendered by every path of the diagram —
// the animated reveal AND the prefers-reduced-motion static fallback. Keeping
// it here (not inline JSX) is what makes R-006 testable: the explanatory
// "what each skill reads and writes" is real, always-in-DOM content, never a
// hover-only tooltip, and test/pipeline.test.mjs asserts it stays complete.

export type RecordKind = 'decision' | 'risk' | 'task' | 'none';

export interface PipelineStage {
  /** The skill's canonical name, as it is invoked. */
  skill: string;
  /** One line on what the stage does. */
  summary: string;
  /** What the stage reads in — the prior records or input. */
  reads: string;
  /** What the stage writes out — the records or artifact it produces. */
  writes: string;
  /** The record ID form this stage mints, for the blueprint chip (if any). */
  chip: string | null;
  /** Record kind produced, for styling the chip. */
  produces: RecordKind;
}

// Canonical order: challenge → red-team → triage → decompose → sequence →
// build → reconcile. Reads/writes are the honest data flow between the
// decision, risk, and task records the pipeline maintains.
export const PIPELINE: PipelineStage[] = [
  {
    skill: 'challenge-me',
    summary: 'Interrogates your plan until the hidden choices are settled.',
    reads: 'your plan, in prose',
    writes: 'Decisions',
    chip: 'D-NNN',
    produces: 'decision',
  },
  {
    skill: 'red-team-me',
    summary: 'Adversarially stress-tests each decision for how it breaks.',
    reads: 'Decisions',
    writes: 'Risks',
    chip: 'R-NNN',
    produces: 'risk',
  },
  {
    skill: 'triage-risks',
    summary: 'Assigns every risk a disposition and reconciles the decisions.',
    reads: 'Risks + Decisions',
    writes: 'dispositions + updated Decisions',
    chip: null,
    produces: 'none',
  },
  {
    skill: 'decompose-plan',
    summary: 'Breaks the hardened plan into atomic, shippable tasks.',
    reads: 'Decisions + Risks',
    writes: 'Tasks',
    chip: 'T-NNN',
    produces: 'task',
  },
  {
    skill: 'sequence-work',
    summary: 'Orders the tasks into phases that front-load risk.',
    reads: 'Tasks + Risks',
    writes: 'a phased order',
    chip: null,
    produces: 'none',
  },
  {
    skill: 'task-brief',
    summary: 'Briefs and drives each task, then records verified evidence.',
    reads: 'Tasks + Decisions + Risks',
    writes: 'code + task status & evidence',
    chip: null,
    produces: 'task',
  },
  {
    skill: 'reconcile-status',
    summary: 'Recomputes what is actually built from current task state.',
    reads: 'Tasks',
    writes: 'the implementation view',
    chip: null,
    produces: 'none',
  },
];
