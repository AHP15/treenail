#!/usr/bin/env python3
"""test_skill_lint.py — consistency lint over the skill pack's prose.

The pipeline's records stay consistent because each fact has one owner
and everything else is a projection of it. The skill pack itself follows
the same rule: grammars and enums are owned by the scripts, the schema by
the conventions spec, and each SKILL.md owns only its procedure. These
tests turn "don't restate a fact in two places" into a failing check, so
the spec, the scripts, and the skill text cannot quietly drift apart.

Run with the rest of the suite:
    python3 -m unittest discover -s _shared/scripts/tests
"""

import os
import re
import sys
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.dirname(SCRIPTS)
SKILLS = os.path.dirname(SHARED)
sys.path.insert(0, SCRIPTS)

import anchors  # noqa: E402
import audit  # noqa: E402

SPEC_PATH = os.path.join(SHARED, "conventions-spec.md")
ANCHOR_PREFIXES = ("file:", "grep:", "symbol:", "test:", "git:")
SCRIPT_REF_RE = re.compile(r"_shared/scripts/([\w-]+\.py)")
# "spec § TASKS", "spec § ID reservation", "spec § INDEX projection".
SPEC_REF_RE = re.compile(r"spec § ((?:ID|INDEX) [a-z]+|[A-Z]{2,}\b)")
# A parenthesized citation of internal planning records, e.g. "(D-028)" or
# "(T-022, R-012)". Those IDs belong to this repo's own docs/, not to the
# user projects the skills and spec ship into.
INTERNAL_CITATION_RE = re.compile(r"\((?:[DRT]-\d{3}(?:,\s*)?)+\)")
KEBAB_TOKEN_RE = re.compile(r"`([a-z]+(?:-[a-z]+)+)`")
# Backticked kebab-case tokens that are legitimately not skill names.
NON_SKILL_KEBAB = {"graphiti-core"}
SCRIPT_CALL_WRITES = ("mint_id.py", "reindex.py", "bootstrap.py",
                      "archive_cycle.py", "graph_sync.py")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def skill_dirs():
    return sorted(
        d for d in os.listdir(SKILLS)
        if not d.startswith("_")
        and os.path.isfile(os.path.join(SKILLS, d, "SKILL.md"))
    )


def skills():
    return [(d, read(os.path.join(SKILLS, d, "SKILL.md"))) for d in skill_dirs()]


def spec_section(spec, heading):
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)",
                  spec, re.MULTILINE | re.DOTALL)
    assert m, f"spec has no '## {heading}' section"
    return m.group(1)


def spec_enum(section, field):
    m = re.search(r"^- \*\*" + re.escape(field) + r"\*\*: (.+)$",
                  section, re.MULTILINE)
    assert m, f"spec section has no '{field}' field"
    return set(re.findall(r"`([^`]+)`", m.group(1)))


class TestSpecMatchesScripts(unittest.TestCase):
    """Enums and grammars are owned by code; the spec must agree."""

    def setUp(self):
        self.spec = read(SPEC_PATH)

    def test_decision_status(self):
        sec = spec_section(self.spec, "DECISIONS")
        self.assertEqual(spec_enum(sec, "Status"), audit.DEC_STATUS)

    def test_risk_enums(self):
        sec = spec_section(self.spec, "RISKS")
        self.assertEqual(spec_enum(sec, "Disposition"), audit.RISK_DISP)
        self.assertEqual(spec_enum(sec, "Severity"), audit.SEVERITY)
        self.assertEqual(spec_enum(sec, "Likelihood"), audit.LIKELIHOOD)

    def test_task_enums(self):
        sec = spec_section(self.spec, "TASKS")
        self.assertEqual(spec_enum(sec, "Status"), audit.TASK_STATUS)
        self.assertEqual(spec_enum(sec, "Size"), audit.SIZES)

    def test_anchor_forms(self):
        sec = spec_section(self.spec, "TASKS")
        forms = set(re.findall(r"^  - `(\w+:)", sec, re.MULTILINE))
        self.assertEqual(forms, set(ANCHOR_PREFIXES))
        for prefix in ANCHOR_PREFIXES:
            self.assertRegex(prefix, anchors.ANCHOR_PREFIX_RE)


class TestSkillText(unittest.TestCase):
    """Each SKILL.md owns its procedure only, and references what exists."""

    def test_frontmatter_name_matches_dir(self):
        for name, text in skills():
            m = re.match(r"^---\nname: (\S+)\n", text)
            self.assertTrue(m, f"{name}: missing frontmatter name")
            self.assertEqual(m.group(1), name)

    def test_template_sections(self):
        for name, text in skills():
            for marker in ("**Reads:**", "**Writes:**", "## Never", "## Next"):
                self.assertIn(marker, text, f"{name}: missing {marker}")
            self.assertRegex(text, r"(?m)^## (Steps|Phase )",
                             f"{name}: missing ## Steps")

    def test_no_restated_anchor_grammar(self):
        """Listing the anchor forms in a skill is how `git:` went missing
        from four places. Skills cite spec § TASKS instead."""
        for name, text in skills():
            for line in text.splitlines():
                hits = {p for p in ANCHOR_PREFIXES if f"`{p}" in line}
                self.assertLess(len(hits), 3,
                                f"{name}: restates the anchor grammar: {line.strip()}")

    def test_no_by_hand_fallbacks(self):
        """Python 3 is required (D-009); a prose re-implementation of a
        script is a second, drifting implementation."""
        for name, text in skills():
            self.assertNotRegex(text, r"(?i)python3?`? is unavailable|by hand",
                                f"{name}: describes a by-hand fallback")

    def test_script_references_exist(self):
        texts = skills() + [("conventions-spec", read(SPEC_PATH))]
        for name, text in texts:
            for script in SCRIPT_REF_RE.findall(text):
                self.assertTrue(os.path.isfile(os.path.join(SCRIPTS, script)),
                                f"{name}: references missing script {script}")

    def test_spec_section_references_exist(self):
        headings = re.findall(r"(?m)^## (.+)$", read(SPEC_PATH))
        for name, text in skills():
            for ref in SPEC_REF_RE.findall(text):
                self.assertTrue(
                    any(h.lower().startswith(ref.lower()) for h in headings),
                    f"{name}: 'spec § {ref}' matches no spec section")

    def test_skill_references_exist(self):
        known = set(skill_dirs())
        for name, text in skills():
            body = text.split("\n---\n", 1)[-1]  # skip frontmatter
            for tok in KEBAB_TOKEN_RE.findall(body):
                if tok in NON_SKILL_KEBAB:
                    continue
                self.assertIn(tok, known, f"{name}: names unknown skill `{tok}`")

    def test_read_only_skills_run_no_writing_script(self):
        for name, text in skills():
            if "**Writes:** nothing" not in text:
                continue
            for script in SCRIPT_CALL_WRITES:
                self.assertNotRegex(text, r"python3 \S*" + re.escape(script),
                                 f"{name}: declares Writes: nothing but runs {script}")

    def test_no_internal_planning_citations(self):
        texts = skills() + [("conventions-spec", read(SPEC_PATH))]
        for name, text in texts:
            hits = INTERNAL_CITATION_RE.findall(text)
            self.assertEqual(hits, [], f"{name}: cites internal planning IDs {hits}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
