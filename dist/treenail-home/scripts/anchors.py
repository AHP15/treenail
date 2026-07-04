#!/usr/bin/env python3
"""Shared Evidence-anchor parsing for planning pipeline scripts.

The conventions define four machine-resolvable anchor forms:

  file:<path>
  grep:<regex>[ in <pathglob>]
  symbol:<path>:<regex>
  test:<id-or-path>

plus a history pin over any of them (D-025: an anchor whose evidenced
fact was abolished from the working tree is pinned to the last commit
where it resolved, never rewritten):

  git:<short-sha>:<anchor>

`audit.py` uses this module to validate shape; `reconcile.py` uses the
same parse result before resolving anchors against the working tree —
or, for `git:` pins, against the named commit. Keep the grammar here so
the structural and reality checks cannot silently diverge.
"""

import re

ANCHOR_PREFIX_RE = re.compile(r"^(file:|grep:|symbol:|test:|git:)")

GIT_SHA_RE = re.compile(r"^[0-9a-f]{4,40}$", re.IGNORECASE)


def extract_anchor_texts(value):
    """Return authored anchor strings from an Evidence field.

    Preferred Evidence uses one backtick-delimited code span per anchor.
    For a non-empty field with no code spans, return the raw field text so
    callers can report it as malformed instead of treating it as absent.
    """
    anchors = re.findall(r"`([^`]+)`", value or "")
    if (value or "").strip() and not anchors:
        anchors = [(value or "").strip()]
    return anchors


def parse_anchor(anchor):
    """Return (kind, parts, error) for one anchor string.

    `parts` is a dict whose keys depend on `kind`; `error` is None when
    the anchor is well-formed. The function validates shape only, not
    whether the referenced file/pattern exists.
    """
    text = (anchor or "").strip()
    if not text:
        return None, {}, "empty anchor"

    if text.startswith("git:"):
        rest = text[4:]
        sha, sep, inner = rest.partition(":")
        sha, inner = sha.strip(), inner.strip()
        if not sep or not inner:
            return "git", {"sha": sha}, \
                "git anchor requires git:<short-sha>:<anchor>"
        if not GIT_SHA_RE.match(sha):
            return "git", {"sha": sha}, \
                "git anchor requires a hex commit sha (4-40 chars)"
        if inner.startswith("git:"):
            return "git", {"sha": sha}, "git anchors do not nest"
        kind, parts, err = parse_anchor(inner)
        if err:
            return "git", {"sha": sha}, f"pinned anchor: {err}"
        return "git", {"sha": sha, "kind": kind, "parts": parts,
                       "anchor": inner}, None

    if text.startswith("file:"):
        path = text[5:].strip()
        if not path:
            return "file", {"path": path}, "file anchor requires a path"
        return "file", {"path": path}, None

    if text.startswith("grep:"):
        body = text[5:].strip()
        if not body:
            return "grep", {}, "grep anchor requires a regex"
        m = re.search(r"\s+in\s+(\S+)\s*$", body)
        if m:
            pattern = body[:m.start()].strip()
            scope = m.group(1).strip()
            if not pattern:
                return "grep", {"scope": scope}, "grep anchor requires a regex"
            if not scope:
                return "grep", {"pattern": pattern}, "grep scope is empty"
            return "grep", {"pattern": pattern, "scope": scope}, None
        return "grep", {"pattern": body, "scope": None}, None

    if text.startswith("symbol:"):
        rest = text[7:].strip()
        path, sep, pattern = rest.partition(":")
        path, pattern = path.strip(), pattern.strip()
        if not sep:
            return "symbol", {"path": path}, "symbol anchor requires <path>:<regex>"
        if not path:
            return "symbol", {"pattern": pattern}, "symbol anchor requires a path"
        if not pattern:
            return "symbol", {"path": path}, "symbol anchor requires a regex"
        return "symbol", {"path": path, "pattern": pattern}, None

    if text.startswith("test:"):
        target = text[5:].strip()
        if not target:
            return "test", {"target": target}, "test anchor requires an id or path"
        return "test", {"target": target}, None

    return None, {}, \
        "anchor must start with file:, grep:, symbol:, test:, or git:"
