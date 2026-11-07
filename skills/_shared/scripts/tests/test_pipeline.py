#!/usr/bin/env python3
"""test_pipeline.py — golden / determinism / invariant tests for the
deterministic core of the planning pipeline.

The pipeline's whole value proposition is that the per-record `<ID>.md`
files are the source of truth and every projection (INDEX, the audit
report, compaction eligibility, the reconcile view) is a DETERMINISTIC,
rebuildable function of them. That guarantee lives entirely in these
scripts, so it needs to be pinned: a future "small improvement" to
`parse_record` or a regex must not silently change what every INDEX and
audit produces.

These tests build throwaway `docs/` trees in a tmp dir and drive the
scripts exactly as the skills do — via subprocess for the CLI tools
(`audit.py`, `compact-select.py`, `reconcile.py`, `reconcile_smells.py`,
`archive_cycle.py`, `mint_id.py`) and via direct import for the projection
unit tests.

Run:  python3 -m unittest discover -s _shared/scripts/tests
  or: python3 _shared/scripts/tests/test_pipeline.py
"""

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS)

import reindex  # noqa: E402  (path set above)

PY = sys.executable


def run(script, *args, **kw):
    """Run a scripts/ CLI tool, return (rc, stdout, stderr)."""
    cmd = [PY, os.path.join(SCRIPTS, script), *args]
    # The scripts reconfigure stdio to UTF-8 (R-010); decode the same way
    # so captures don't depend on the host locale (Windows cp1252).
    p = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                       errors="replace", **kw)
    return p.returncode, p.stdout, p.stderr


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(textwrap.dedent(body).lstrip("\n"))


def build_clean_scope(root):
    """A structurally-valid project scope exercising the interesting shapes:
    a superseded↔supersedes pair, a mitigate risk with a task, a defer with
    an observable trigger, a `done` task with an Evidence anchor, and a
    `dropped` task carrying Date dropped. Returns the docs dir. Runs reindex
    so all INDEX files are present and correct."""
    docs = os.path.join(root, "docs")
    write(f"{docs}/decisions/D-001.md", """
        ## D-001: Use Postgres as the primary datastore
        - **Status**: accepted
        - **Date**: 2025-03-14
        - **Context**: Need a transactional store.
        - **Decision**: Use Postgres 15+.
        - **Rationale**: One datastore is simpler.
    """)
    write(f"{docs}/decisions/D-002.md", """
        ## D-002: Authenticate via OAuth2
        - **Status**: accepted
        - **Date**: 2025-08-21
        - **Context**: Mobile clients in scope.
        - **Decision**: OAuth2 with PKCE.
        - **Rationale**: Standards-based.
    """)
    # Superseded pair, both active (tests intra-scope symmetry + the
    # terminal-in-active INFO).
    write(f"{docs}/decisions/D-003.md", """
        ## D-003: Session cookies
        - **Status**: superseded
        - **Date**: 2025-04-02
        - **Date superseded**: 2025-08-21
        - **Context**: Browser-only admin panel.
        - **Decision**: Opaque session cookies.
        - **Rationale**: Path of least resistance.
        - **Superseded by**: D-004
    """)
    write(f"{docs}/decisions/D-004.md", """
        ## D-004: OAuth2 refresh tokens
        - **Status**: accepted
        - **Date**: 2025-08-21
        - **Context**: Replaces cookies.
        - **Decision**: Opaque refresh tokens.
        - **Rationale**: Revocation under our control.
        - **Supersedes**: D-003
    """)
    write(f"{docs}/risks/R-001.md", """
        ## R-001: Refresh tokens leaked from client storage
        - **Severity**: high
        - **Likelihood**: medium
        - **Disposition**: mitigate
        - **Date**: 2025-08-23
        - **Description**: Token exfiltration grants long access.
        - **Disposition rationale**: Bound blast radius.
        - **Action**: Rotate on use. Tracked as T-010.
        - **Related decisions**: D-004
    """)
    write(f"{docs}/risks/R-002.md", """
        ## R-002: Postgres write throughput under tenant growth
        - **Severity**: high
        - **Likelihood**: medium
        - **Disposition**: defer
        - **Date**: 2025-03-20
        - **Description**: Lock contention at month-end.
        - **Disposition rationale**: Trigger is far off.
        - **Action**: Revisit when active tenants exceed 300 or p95 > 500ms.
        - **Related decisions**: D-001
    """)
    write(f"{docs}/tasks/T-010.md", """
        ## T-010: Rotate refresh token on every use
        - **Status**: done
        - **Size**: M
        - **Implements**: D-004
        - **Mitigates**: R-001
        - **Acceptance**: every refresh rotates the token.
        - **Evidence**:
          - `symbol:src/auth/refresh.ts:rotateRefreshToken`
        - **Date done**: 2025-09-04
    """)
    write(f"{docs}/tasks/T-011.md", """
        ## T-011: Add OAuth2 PKCE flow
        - **Status**: todo
        - **Size**: M
        - **Implements**: D-002
        - **Acceptance**: PKCE authorization code flow works end to end.
    """)
    # dropped task carrying a parseable Date dropped (the #3 fix).
    write(f"{docs}/tasks/archive/T-012.md", """
        ## T-012: Per-device anomaly detection
        - **Status**: dropped
        - **Size**: L
        - **Implements**: D-002
        - **Acceptance**: alert on fingerprint changes.
        - **Date done**:
        - **Date dropped**: 2025-10-12
        - **Notes**: Redundant after D-004.
    """)
    write(f"{docs}/retrospectives/2025-12-01.md", """
        ## Retrospective: 2025-12-01
        - **Cycle**: Q4
        - **Boundary-end**: 2025-12-01
        - **Date**: 2025-12-01
    """)
    rc, out, err = run("reindex.py", docs)
    assert rc == 0, f"fixture reindex not clean: {out}\n{err}"
    return docs


class TestReindexProjection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.docs = build_clean_scope(self.tmp)

    def idx(self, rel):
        with open(os.path.join(self.docs, rel), encoding="utf-8") as fh:
            return fh.read()

    def test_determinism_byte_identical(self):
        # Snapshot every index that exists (an empty archive dir gets no
        # INDEX file — that is correct), rebuild, compare byte-for-byte.
        candidates = [
            "decisions/INDEX.md", "decisions/archive/INDEX.md",
            "risks/INDEX.md", "risks/archive/INDEX.md",
            "tasks/INDEX.md", "tasks/archive/INDEX.md",
            "retrospectives/INDEX.md",
        ]
        indexes = [p for p in candidates
                   if os.path.exists(os.path.join(self.docs, p))]
        self.assertIn("tasks/archive/INDEX.md", indexes)  # fixture sanity
        before = {p: self.idx(p) for p in indexes}
        rc, _, _ = run("reindex.py", self.docs)
        self.assertEqual(rc, 0)
        for p in indexes:
            self.assertEqual(before[p], self.idx(p), f"{p} not byte-identical")

    def test_decision_supersede_suffix(self):
        self.assertIn("D-003 | superseded | Session cookies (→ D-004)",
                      self.idx("decisions/INDEX.md"))

    def test_risk_mitigate_task_suffix(self):
        self.assertIn(
            "R-001 | mitigate | high | Refresh tokens leaked from client "
            "storage [tasks: T-010]", self.idx("risks/INDEX.md"))

    def test_done_task_projects_date_done(self):
        self.assertIn(
            "T-010 | done | M | D-004,R-001 | Rotate refresh token on every "
            "use | 2025-09-04", self.idx("tasks/INDEX.md"))

    def test_dropped_task_projects_date_dropped(self):
        # Regression for the #3 fix: the terminal-date column for a dropped
        # task is Date dropped, not empty.
        self.assertIn(
            "T-012 | dropped | L | D-002 | Per-device anomaly detection | "
            "2025-10-12", self.idx("tasks/archive/INDEX.md"))

    def test_open_task_does_not_project_stale_terminal_date(self):
        write(f"{self.docs}/tasks/T-013.md", """
            ## T-013: Reopened work
            - **Status**: todo
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Date done**: 2025-01-01
        """)
        run("reindex.py", self.docs, "tasks")
        self.assertIn(
            "T-013 | todo | S | D-001 | Reopened work |",
            self.idx("tasks/INDEX.md"))
        self.assertNotIn("Reopened work | 2025-01-01", self.idx("tasks/INDEX.md"))

    def test_index_no_trailing_whitespace_or_blank_lines(self):
        for p in ("decisions/INDEX.md", "tasks/INDEX.md", "risks/INDEX.md"):
            txt = self.idx(p)
            self.assertTrue(txt.endswith("\n"))
            for ln in txt.splitlines():
                self.assertEqual(ln, ln.rstrip(), f"trailing ws in {p}")
                self.assertTrue(ln.strip(), f"blank line in {p}")


    def test_ids_in_skips_scope_qualified_refs(self):
        self.assertEqual(
            reindex.ids_in("D-001, project:D-002, feature:billing/D-003 and D-004", "D"),
            ["D-001", "D-004"])


class TestReindexParser(unittest.TestCase):
    """Direct unit tests of the authoritative parser/projector."""

    def test_multiline_action_recovers_task_ids(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "R-009.md")
        write(p, """
            ## R-009: Some risk
            - **Severity**: high
            - **Likelihood**: medium
            - **Disposition**: mitigate
            - **Date**: 2025-01-01
            - **Description**: x.
            - **Disposition rationale**: y.
            - **Action**: Implement rotation across
              T-031, T-032 and also T-033 for coverage.
            - **Related decisions**: D-019
        """)
        rid, title, fields = reindex.parse_record(p)
        self.assertEqual(rid, "R-009")
        line = reindex.project("risks", rid, title, fields, [])
        self.assertIn("[tasks: T-031,T-032,T-033]", line)

    def test_malformed_missing_status_is_reported(self):
        tmp = tempfile.mkdtemp()
        p = os.path.join(tmp, "D-001.md")
        write(p, """
            ## D-001: No status here
            - **Date**: 2025-01-01
        """)
        rid, title, fields = reindex.parse_record(p)
        malformed = []
        reindex.project("decisions", rid, title, fields, malformed)
        self.assertIn(("D-001", "Status"), malformed)


class TestAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.docs = build_clean_scope(self.tmp)

    def test_clean_tree_has_no_blockers(self):
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 0, f"expected clean, got:\n{out}")
        self.assertIn("0 blocker(s)", out)

    def test_pending_disposition_is_blocker(self):
        write(f"{self.docs}/risks/R-003.md", """
            ## R-003: Untriaged risk
            - **Severity**: low
            - **Likelihood**: low
            - **Disposition**: pending
            - **Description**: not yet triaged.
        """)
        run("reindex.py", self.docs, "risks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("pending", out)

    def test_dangling_implements_is_blocker(self):
        write(f"{self.docs}/tasks/T-013.md", """
            ## T-013: Points at a missing decision
            - **Status**: todo
            - **Size**: S
            - **Implements**: D-999
            - **Acceptance**: whatever.
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("D-999", out)

    def test_done_without_date_is_blocker(self):
        write(f"{self.docs}/tasks/T-014.md", """
            ## T-014: Done but no date
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("Date done", out)

    def test_dropped_without_date_dropped_is_warn(self):
        # #3 regression: warn (not blocker) so the body can't silently
        # become permanently un-compactable.
        write(f"{self.docs}/tasks/archive/T-015.md", """
            ## T-015: Dropped, no Date dropped
            - **Status**: dropped
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Notes**: dropped.
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 0, "missing Date dropped must not be a blocker")
        self.assertIn("Date dropped", out)

    def test_index_drift_is_blocker(self):
        # Hand-corrupt an INDEX line; audit must flag drift, not accept it.
        idx = os.path.join(self.docs, "tasks/INDEX.md")
        with open(idx, encoding="utf-8") as fh:
            txt = fh.read()
        with open(idx, "w", encoding="utf-8") as fh:
            fh.write(txt.replace("| todo |", "| done |"))
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("INDEX drift", out)

    def test_done_symbol_anchor_requires_regex(self):
        write(f"{self.docs}/tasks/T-016.md", """
            ## T-016: Weak symbol anchor
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `symbol:src/auth.ts`
            - **Date done**: 2025-01-01
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("symbol anchor requires <path>:<regex>", out)

    def test_empty_anchor_targets_are_blockers_on_done_tasks(self):
        write(f"{self.docs}/tasks/T-017.md", """
            ## T-017: Empty file anchor
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `file:`
            - **Date done**: 2025-01-01
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("file anchor requires a path", out)

    def test_done_git_pinned_anchor_is_well_formed(self):
        write(f"{self.docs}/tasks/T-018.md", """
            ## T-018: Pinned evidence
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `git:abc1234:grep:"name": "treenail" in cli/package.json`
            - **Date done**: 2025-01-01
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 0, f"git: pin must be well-formed, got:\n{out}")
        self.assertNotIn("malformed Evidence anchor", out)

    def test_done_git_anchor_bad_sha_is_blocker(self):
        write(f"{self.docs}/tasks/T-019.md", """
            ## T-019: Pin without a sha
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `git:not-a-sha:file:cli/package.json`
            - **Date done**: 2025-01-01
        """)
        run("reindex.py", self.docs, "tasks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("hex commit sha", out)

    def test_fix_risk_missing_decision_is_blocker(self):
        write(f"{self.docs}/risks/R-003.md", """
            ## R-003: Fixed by missing decision
            - **Severity**: high
            - **Likelihood**: high
            - **Disposition**: fix
            - **Date**: 2025-01-01
            - **Description**: x.
            - **Disposition rationale**: y.
            - **Action**: Superseded by D-999.
            - **Related decisions**: D-001
        """)
        run("reindex.py", self.docs, "risks")
        rc, out, _ = run("audit.py", self.docs)
        self.assertEqual(rc, 1)
        self.assertIn("missing decision(s) D-999", out)

    def test_brownfield_tasks_do_not_mean_decompose_ran(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/decisions/D-001.md", """
            ## D-001: Existing implementation
            - **Status**: accepted
            - **Date**: 2025-01-01
            - **Context**: x.
            - **Decision**: y.
            - **Rationale**: z.
        """)
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: Brownfield observed implementation
            - **Status**: done
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `file:README.md`
            - **Date done**: 2025-01-02
            - **Notes**: brownfield-observed.
        """)
        write(f"{docs}/risks/R-001.md", """
            ## R-001: Guard not decomposed yet
            - **Severity**: high
            - **Likelihood**: medium
            - **Disposition**: mitigate
            - **Date**: 2025-01-01
            - **Description**: x.
            - **Disposition rationale**: y.
            - **Action**: Add a guard during decomposition.
            - **Related decisions**: D-001
        """)
        run("reindex.py", docs)
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 0)
        self.assertIn("not yet decomposed", out)


class TestAuditCrossChecks(unittest.TestCase):
    """#6/#7 — header↔filename, duplicate-across-dirs, retro INDEX drift,
    and ranged ID-gap output."""

    def _dec(self, path, header, extra=""):
        write(path, f"""
            ## {header}
            - **Status**: accepted
            - **Date**: 2025-01-01
            - **Context**: x
            - **Decision**: y
            - **Rationale**: z
            {extra}
        """)

    def test_header_filename_mismatch_is_blocker(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        self._dec(f"{docs}/decisions/D-007.md", "D-003: wrong id in header")
        run("reindex.py", docs, "decisions")
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 1)
        self.assertIn("does not match filename", out)

    def test_non_padded_filename_is_blocker(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        self._dec(f"{docs}/decisions/D-1.md", "D-001: padded header")
        run("reindex.py", docs, "decisions")
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 1)
        self.assertIn("filename must be zero-padded", out)

    def test_duplicate_id_across_dirs_is_blocker(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        self._dec(f"{docs}/decisions/D-001.md", "D-001: active copy")
        self._dec(f"{docs}/decisions/archive/D-001.md",
                  "D-001: archive copy", "- **Superseded by**: D-002")
        run("reindex.py", docs, "decisions")
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 1)
        self.assertIn("both active and archive", out)

    def test_retro_index_drift_is_blocker(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/retrospectives/2025-12-01.md", """
            ## Retrospective: 2025-12-01
            - **Cycle**: Q4
            - **Boundary-end**: 2025-12-01
            - **Date**: 2025-12-01
        """)
        write(f"{docs}/retrospectives/INDEX.md", "2025-99-99 | Wrong line\n")
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 1)
        self.assertIn("retrospectives/INDEX.md", out)

    def test_id_gap_is_one_ranged_info_line(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        self._dec(f"{docs}/decisions/D-001.md", "D-001: first")
        self._dec(f"{docs}/decisions/D-005.md", "D-005: fifth")
        run("reindex.py", docs, "decisions")
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 0)  # gaps are INFO, not blockers
        gap_lines = [ln for ln in out.splitlines() if "ID gap" in ln]
        self.assertEqual(len(gap_lines), 1, gap_lines)
        self.assertIn("D-002..D-004", gap_lines[0])

    def test_feature_promotion_missing_project_destination_is_blocker(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        feature = os.path.join(docs, "features", "billing")
        self._dec(
            f"{feature}/decisions/D-001.md",
            "D-001: feature decision",
            """
            - **Status**: promoted
            - **Date promoted**: 2025-02-01
            - **Promoted to**: project:D-999
            """,
        )
        run("reindex.py", feature, "decisions")
        rc, out, _ = run("audit.py", feature, "--project", docs)
        self.assertEqual(rc, 1)
        self.assertIn("destination decision does not exist", out)

    def test_feature_promotion_round_trip_clean(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        feature = os.path.join(docs, "features", "billing")
        self._dec(
            f"{feature}/decisions/D-001.md",
            "D-001: feature decision",
            """
            - **Status**: promoted
            - **Date promoted**: 2025-02-01
            - **Promoted to**: project:D-002
            """,
        )
        self._dec(
            f"{docs}/decisions/D-002.md",
            "D-002: project decision",
            "- **Promoted from**: feature:billing/D-001",
        )
        run("reindex.py", docs, "decisions")
        run("reindex.py", feature, "decisions")
        rc, out, _ = run("audit.py", feature, "--project", docs)
        self.assertEqual(rc, 0, out)


    def _risk(self, path, header, extra=""):
        write(path, f"""
            ## {header}
            - **Severity**: high
            - **Likelihood**: medium
            - **Disposition**: accept
            - **Date**: 2025-01-01
            - **Description**: x
            - **Disposition rationale**: y
            {extra}
        """)

    def _promoted_risk_pair(self, dest_related):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        feature = os.path.join(docs, "features", "billing")
        self._dec(f"{feature}/decisions/D-003.md", "D-003: feature choice")
        self._dec(f"{docs}/decisions/D-003.md", "D-003: unrelated project choice")
        self._risk(f"{feature}/risks/R-001.md", "R-001: feature risk", """
            - **Action**: none
            - **Related decisions**: D-003
            - **Promoted to**: project:R-001
            """)
        self._risk(f"{docs}/risks/R-001.md", "R-001: promoted risk", f"""
            - **Action**: none
            - **Related decisions**: {dest_related}
            - **Promoted from**: feature:billing/R-001
            """)
        run("reindex.py", docs)
        run("reindex.py", feature)
        return docs, feature

    def test_promoted_risk_with_verbatim_bare_link_warns(self):
        docs, feature = self._promoted_risk_pair("D-003")
        rc, out, _ = run("audit.py", feature, "--project", docs)
        self.assertIn("copied from R-001", out)

    def test_promoted_risk_with_qualified_link_is_clean(self):
        docs, feature = self._promoted_risk_pair("feature:billing/D-003")
        rc, out, _ = run("audit.py", feature, "--project", docs)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("copied from", out)

    def test_risk_without_related_decisions_is_info_not_warn(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        self._risk(f"{docs}/risks/R-001.md", "R-001: standalone risk",
                   "- **Action**: none")
        run("reindex.py", docs)
        rc, out, _ = run("audit.py", docs)
        self.assertEqual(rc, 0, out)
        info = out.split("== INFO ==")[-1]
        self.assertIn("no 'Related decisions'", info)
        self.assertNotIn("== WARN ==", out)


class TestCompactSelect(unittest.TestCase):
    def test_no_boundary_returns_1_and_skips(self):
        tmp = tempfile.mkdtemp()
        docs = build_clean_scope(tmp)
        # Remove the retrospective so there is no Boundary-end frontier.
        os.remove(os.path.join(docs, "retrospectives/2025-12-01.md"))
        rc, out, _ = run("compact-select.py", docs)
        self.assertEqual(rc, 1)
        self.assertIn("NO BOUNDARY", out)

    def test_dropped_task_is_compact_eligible(self):
        # #3 regression: with a frontier past its drop date, the dropped
        # task is COMPACT, not SKIP.
        tmp = tempfile.mkdtemp()
        docs = build_clean_scope(tmp)
        rc, out, _ = run("compact-select.py", docs)
        self.assertEqual(rc, 0)
        self.assertIn("COMPACT  T-012", out)
        self.assertNotIn("SKIP     T-012", out)

    def test_superseded_decision_uses_terminal_date_not_acceptance_date(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/decisions/archive/D-001.md", """
            ## D-001: Old choice
            - **Status**: superseded
            - **Date**: 2025-01-01
            - **Date superseded**: 2025-07-01
            - **Superseded by**: D-002
            - **Summary**:
        """)
        write(f"{docs}/retrospectives/2025-06-01.md", """
            ## Retrospective: 2025-06-01
            - **Cycle**: H1
            - **Boundary-end**: 2025-06-01
            - **Date**: 2025-06-01
        """)
        rc, out, _ = run("compact-select.py", docs)
        self.assertEqual(rc, 0)
        self.assertIn("hold     D-001  (terminal 2025-07-01 > boundary)", out)
        self.assertNotIn("COMPACT  D-001", out)

    def test_superseded_decision_without_terminal_date_skips(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/decisions/archive/D-001.md", """
            ## D-001: Old choice
            - **Status**: superseded
            - **Date**: 2025-01-01
            - **Superseded by**: D-002
        """)
        write(f"{docs}/retrospectives/2025-06-01.md", """
            ## Retrospective: 2025-06-01
            - **Cycle**: H1
            - **Boundary-end**: 2025-06-01
            - **Date**: 2025-06-01
        """)
        rc, out, _ = run("compact-select.py", docs)
        self.assertEqual(rc, 0)
        self.assertIn("SKIP     D-001", out)


class TestArchiveCycleReap(unittest.TestCase):
    def test_dry_run_does_not_move_records(self):
        tmp = tempfile.mkdtemp()
        docs = build_clean_scope(tmp)
        rc, out, _ = run("archive_cycle.py", docs, "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("REAP  decisions/D-003", out)
        self.assertTrue(os.path.exists(f"{docs}/decisions/D-003.md"))

    def test_reap_moves_terminal_records_and_reindexes(self):
        tmp = tempfile.mkdtemp()
        docs = build_clean_scope(tmp)
        rc, out, _ = run("archive_cycle.py", docs)
        self.assertEqual(rc, 0, out)
        self.assertFalse(os.path.exists(f"{docs}/decisions/D-003.md"))
        self.assertTrue(os.path.exists(f"{docs}/decisions/archive/D-003.md"))
        self.assertFalse(os.path.exists(f"{docs}/tasks/T-010.md"))
        self.assertTrue(os.path.exists(f"{docs}/tasks/archive/T-010.md"))
        with open(f"{docs}/decisions/INDEX.md", encoding="utf-8") as fh:
            self.assertNotIn("D-003", fh.read())
        with open(f"{docs}/decisions/archive/INDEX.md", encoding="utf-8") as fh:
            self.assertIn("D-003 | superseded", fh.read())

    def test_confirmed_fix_risk_gets_date_resolved_and_reaps(self):
        tmp = tempfile.mkdtemp()
        docs = build_clean_scope(tmp)
        write(f"{docs}/risks/R-003.md", """
            ## R-003: Superseded guard
            - **Severity**: high
            - **Likelihood**: high
            - **Disposition**: fix
            - **Date**: 2025-09-01
            - **Description**: x.
            - **Disposition rationale**: y.
            - **Action**: Superseded by D-004.
            - **Related decisions**: D-003
        """)
        run("reindex.py", docs, "risks")
        rc, out, _ = run(
            "archive_cycle.py", docs, "--confirm-risk", "R-003",
            "--today", "2025-12-02"
        )
        self.assertEqual(rc, 0, out)
        self.assertFalse(os.path.exists(f"{docs}/risks/R-003.md"))
        with open(f"{docs}/risks/archive/R-003.md", encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("- **Date resolved**: 2025-12-02", body)
        with open(f"{docs}/risks/archive/INDEX.md", encoding="utf-8") as fh:
            self.assertIn("R-003 | fix | high |", fh.read())


class TestMintId(unittest.TestCase):
    def mint(self, dirpath, prefix):
        rc, out, err = run("mint_id.py", dirpath, prefix)
        self.assertEqual(rc, 0, err)
        return out.split("\t")[0].strip()

    def test_sequential_claims_increment(self):
        tmp = tempfile.mkdtemp()
        d = os.path.join(tmp, "decisions")
        a = self.mint(d, "D")
        b = self.mint(d, "D")
        self.assertEqual(a, "D-001")
        self.assertEqual(b, "D-002")  # the claimed file is counted next time

    def test_max_spans_active_and_archive(self):
        tmp = tempfile.mkdtemp()
        d = os.path.join(tmp, "decisions")
        os.makedirs(os.path.join(d, "archive"), exist_ok=True)
        # highest ID lives in archive — the next mint must clear it.
        open(os.path.join(d, "archive", "D-007.md"), "w").close()
        open(os.path.join(d, "D-003.md"), "w").close()
        self.assertEqual(self.mint(d, "D"), "D-008")


class TestCompactionPreservesProjectionFields(unittest.TestCase):
    """A compacted record must keep the fields its INDEX line projects
    (Size for tasks, Severity for risks), or reindex flags it malformed."""

    def test_compacted_task_keeps_size(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/tasks/archive/T-001.md", """
            ## T-001: Rotate refresh token
            - **Status**: done
            - **Size**: M
            - **Date done**: 2025-09-04
            - **Date archived**: 2026-01-01
            - **Implements**: D-019
            - **Evidence**: `symbol:src/auth/refresh.ts:rotateRefreshToken`
            - **Summary**: Shipped token rotation.
        """)
        rc, out, _ = run("reindex.py", docs, "tasks")
        self.assertEqual(rc, 0, f"compacted task flagged malformed:\n{out}")
        with open(f"{docs}/tasks/archive/INDEX.md", encoding="utf-8") as fh:
            self.assertIn("T-001 | done | M |", fh.read())

    def test_compacted_risk_keeps_severity(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/risks/archive/R-001.md", """
            ## R-001: Refresh tokens leaked
            - **Severity**: high
            - **Likelihood**: medium
            - **Disposition**: accept
            - **Date**: 2025-08-23
            - **Date archived**: 2026-01-01
            - **Action**: none
            - **Summary**: Residual accepted after rotation shipped.
        """)
        rc, out, _ = run("reindex.py", docs, "risks")
        self.assertEqual(rc, 0, f"compacted risk flagged malformed:\n{out}")
        with open(f"{docs}/risks/archive/INDEX.md", encoding="utf-8") as fh:
            self.assertIn("R-001 | accept | high |", fh.read())


class TestReconcile(unittest.TestCase):
    """The implementation view + Evidence-anchor drift detection (#2/#4)."""

    def _root(self):
        root = tempfile.mkdtemp()
        write(os.path.join(root, "src/auth/refresh.ts"),
              "export function rotateRefreshToken() { return 1; }\n")
        return root, os.path.join(root, "docs")

    def _dec(self, docs, did, title):
        write(f"{docs}/decisions/{did}.md", f"""
            ## {did}: {title}
            - **Status**: accepted
            - **Date**: 2025-01-01
            - **Context**: x
            - **Decision**: y
            - **Rationale**: z
        """)

    def test_todo_plus_dropped_is_not_started(self):
        # #4 regression: a decision with one todo + one dropped task is
        # not_started (nothing is in progress), NOT in_progress.
        root, docs = self._root()
        self._dec(docs, "D-001", "mixed coverage")
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: live work
            - **Status**: todo
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
        """)
        write(f"{docs}/tasks/archive/T-002.md", """
            ## T-002: abandoned work
            - **Status**: dropped
            - **Size**: S
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Date dropped**: 2025-02-01
            - **Notes**: abandoned.
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("D-001: not_started", out)
        self.assertNotIn("D-001: in_progress", out)
        self.assertEqual(rc, 0)  # no done task ⇒ no drift

    def test_verified_implemented_exit_0(self):
        root, docs = self._root()
        self._dec(docs, "D-001", "rotation")
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: rotate
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**:
              - `symbol:src/auth/refresh.ts:rotateRefreshToken`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("D-001: implemented  (verified)", out)
        self.assertEqual(rc, 0)

    def test_drift_exit_1(self):
        root, docs = self._root()
        self._dec(docs, "D-001", "gone")
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: detector
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**:
              - `file:src/auth/does-not-exist.ts`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("UNVERIFIED: drift", out)
        self.assertIn("IMPLEMENTATION DRIFT: T-001", out)
        self.assertEqual(rc, 1)

    def test_malformed_symbol_anchor_is_not_verified(self):
        root, docs = self._root()
        self._dec(docs, "D-001", "weak symbol")
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: weak
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `symbol:src/auth/refresh.ts`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("UNVERIFIED: drift", out)
        self.assertIn("IMPLEMENTATION DRIFT: T-001", out)
        self.assertEqual(rc, 1)

    def _pinned_root(self):
        """A tmp git repo where the committed evidence file is then removed
        from the working tree — D-025's 'abolished fact' shape: the anchor
        must resolve at the pinned commit, never in the tree."""
        root, docs = self._root()

        def git(*args):
            subprocess.run(["git", "-C", root, "-c", "user.email=t@test",
                            "-c", "user.name=t", "-c", "commit.gpgsign=false",
                            *args], check=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

        git("init", "-q")
        git("add", "src/auth/refresh.ts")
        git("commit", "-q", "-m", "evidence")
        p = subprocess.run(["git", "-C", root, "rev-parse", "--short",
                            "HEAD"], capture_output=True, encoding="utf-8")
        sha = p.stdout.strip()
        os.remove(os.path.join(root, "src/auth/refresh.ts"))
        return root, docs, sha

    def test_pinned_anchor_resolves_at_commit_not_tree(self):
        root, docs, sha = self._pinned_root()
        self._dec(docs, "D-001", "abolished fact")
        write(f"{docs}/tasks/T-001.md", f"""
            ## T-001: pinned
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**:
              - `git:{sha}:grep:rotateRefreshToken in src/auth`
              - `git:{sha}:file:src/auth/refresh.ts`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("D-001: implemented  (verified)", out)
        self.assertEqual(rc, 0)

    def test_dangling_pinned_anchor_is_drift(self):
        root, docs, sha = self._pinned_root()
        self._dec(docs, "D-001", "bad pin")
        write(f"{docs}/tasks/T-001.md", f"""
            ## T-001: dangling pin
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**: `git:{sha}:file:src/auth/never-existed.ts`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("UNVERIFIED: drift", out)
        self.assertIn("IMPLEMENTATION DRIFT: T-001", out)
        self.assertEqual(rc, 1)

    def test_grep_anchor_scoped_to_dir(self):
        # "grep:<regex> in <dir>" resolves when the dir is a path prefix.
        root, docs = self._root()
        self._dec(docs, "D-001", "rotation")
        write(f"{docs}/tasks/T-001.md", """
            ## T-001: rotate
            - **Status**: done
            - **Size**: M
            - **Implements**: D-001
            - **Acceptance**: x.
            - **Evidence**:
              - `grep:rotateRefreshToken in src/auth`
            - **Date done**: 2025-02-01
        """)
        run("reindex.py", docs)
        rc, out, _ = run("reconcile.py", docs, "--root", root)
        self.assertIn("(verified)", out)
        self.assertEqual(rc, 0)


class TestBootstrap(unittest.TestCase):
    def test_fresh_feature_scope_bootstraps_project_root(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        feature = os.path.join(docs, "features", "billing")
        rc, out, _ = run("bootstrap.py", feature)
        self.assertEqual(rc, 0, out)
        for rel in ("CONVENTIONS-SPEC.md", "CONVENTIONS-EXAMPLES.md"):
            self.assertTrue(os.path.isfile(os.path.join(docs, rel)), rel)
        with open(os.path.join(docs, ".treenail-version"), encoding="utf-8") as fh:
            self.assertEqual(fh.read().strip(), "1")
        for art in ("decisions", "risks", "tasks"):
            self.assertTrue(os.path.isfile(os.path.join(feature, art, "INDEX.md")))
        self.assertFalse(os.path.exists(os.path.join(feature, "CONVENTIONS-SPEC.md")))

    def test_idempotent_and_never_clobbers(self):
        tmp = tempfile.mkdtemp()
        docs = os.path.join(tmp, "docs")
        write(f"{docs}/decisions/INDEX.md", "D-001 | accepted | Keep me\n")
        write(f"{docs}/CONVENTIONS-SPEC.md", "locally edited\n")
        run("bootstrap.py", docs, "decisions")
        rc, out, _ = run("bootstrap.py", docs, "decisions")
        self.assertEqual(rc, 0)
        self.assertIn("already set up", out)
        with open(f"{docs}/decisions/INDEX.md", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "D-001 | accepted | Keep me\n")
        with open(f"{docs}/CONVENTIONS-SPEC.md", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "locally edited\n")

    def test_unknown_artifact_is_usage_error(self):
        rc, _, err = run("bootstrap.py", tempfile.mkdtemp(), "widgets")
        self.assertEqual(rc, 2)
        self.assertIn("unknown artifact", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
