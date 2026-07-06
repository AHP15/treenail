// Pipeline centerpiece content-path test (T-008, R-006). Run: node --test.
//
// R-006's failure mode: the "what each skill reads and writes" explanation
// lives in a hover/tap-only state, so mobile/keyboard/AT users never reach it.
// The mitigation is architectural — that content is real data in
// lib/pipeline-data.ts, rendered as always-in-DOM text by app/components/
// pipeline.tsx in BOTH the animated and reduced-motion paths. These tests
// guard that content: every stage carries a non-empty reads AND writes, so a
// regression that empties or hover-gates the explanation fails the build.
//
// (node --test strips TS types but not JSX, so the .tsx render itself is
// covered by the typechecked `next build`; the content contract is here.)

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { PIPELINE } from '../lib/pipeline-data.ts';

test('the pipeline has the seven canonical skills in order', () => {
  assert.equal(PIPELINE.length, 7);
  assert.deepEqual(
    PIPELINE.map((s) => s.skill),
    [
      'challenge-me',
      'red-team-me',
      'triage-risks',
      'decompose-plan',
      'sequence-work',
      'task-brief',
      'reconcile-status',
    ]
  );
});

test('every stage carries real, non-empty reads/writes/summary content', () => {
  for (const stage of PIPELINE) {
    for (const field of ['skill', 'summary', 'reads', 'writes']) {
      assert.equal(
        typeof stage[field] === 'string' && stage[field].trim().length > 0,
        true,
        `stage ${stage.skill} must have non-empty ${field} (R-006 content path)`
      );
    }
  }
});

test('the flow chains: what a stage writes feeds a later stage', () => {
  // challenge-me writes Decisions; red-team-me reads Decisions.
  assert.match(PIPELINE[0].writes, /Decision/i);
  assert.match(PIPELINE[1].reads, /Decision/i);
  // decompose-plan writes Tasks; sequence-work reads Tasks.
  assert.match(PIPELINE[3].writes, /Task/i);
  assert.match(PIPELINE[4].reads, /Task/i);
});
