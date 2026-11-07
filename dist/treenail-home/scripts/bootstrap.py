#!/usr/bin/env python3
"""bootstrap.py — idempotent conventions bootstrap for a docs scope.

Every record-writing skill starts the same way on a fresh project: make
sure the conventions spec and examples are adopted at the docs root, the
spec version is stamped, and the scope's INDEX files exist. This script
is the one implementation of that step, so skills call it in one line
instead of each restating it in prose.

Usage:
    bootstrap.py <scope-dir> [artifact ...]

  <scope-dir>  docs root for the scope — `docs` or `docs/features/<name>`.
               The spec, examples, and version marker always land at the
               *project* docs root (a feature scope resolves to its parent).
  artifact     which `<artifact>/INDEX.md` files to ensure exist in the
               scope (default: decisions risks tasks). `retrospectives`
               is also accepted.

Never overwrites: an existing spec, examples file, version marker, or
INDEX is left byte-for-byte untouched. Prints one line per file created
(or `bootstrap: already set up`), exit 0. Exit 2 on usage error.
"""

import os
import re
import sys

ARTIFACTS = ("decisions", "risks", "tasks", "retrospectives")
DEFAULT_ARTIFACTS = ("decisions", "risks", "tasks")
MARKER = ".treenail-version"

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)  # spec + examples sit beside scripts/
ASSETS = (
    ("conventions-spec.md", "CONVENTIONS-SPEC.md"),
    ("conventions-examples.md", "CONVENTIONS-EXAMPLES.md"),
)


def project_docs(scope):
    norm = os.path.normpath(scope)
    parent = os.path.dirname(norm)
    if os.path.basename(parent) == "features":
        return os.path.dirname(parent)
    return norm


def spec_version(spec_text):
    m = re.search(r"^Spec-version:\s*(\S+)", spec_text, re.MULTILINE)
    return m.group(1) if m else None


def create(path, text, created):
    """Write `text` to `path` only if it does not exist (no-clobber)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    created.append(path)


def main(argv):
    args = argv[1:]
    if not args or args[0].startswith("-"):
        print("usage: bootstrap.py <scope-dir> [artifact ...]", file=sys.stderr)
        return 2
    scope, artifacts = args[0], args[1:] or list(DEFAULT_ARTIFACTS)
    bad = [a for a in artifacts if a not in ARTIFACTS]
    if bad:
        print(f"bootstrap.py: unknown artifact(s) {', '.join(bad)} "
              f"(have: {', '.join(ARTIFACTS)})", file=sys.stderr)
        return 2

    docs = project_docs(scope)
    created = []
    spec_text = None
    for src_name, dst_name in ASSETS:
        with open(os.path.join(SHARED, src_name), encoding="utf-8") as fh:
            text = fh.read()
        if src_name == "conventions-spec.md":
            spec_text = text
        create(os.path.join(docs, dst_name), text, created)

    version = spec_version(spec_text or "")
    if version:
        create(os.path.join(docs, MARKER), version + "\n", created)

    for artifact in artifacts:
        create(os.path.join(scope, artifact, "INDEX.md"), "", created)

    for path in created:
        print(f"created {path}")
    if not created:
        print("bootstrap: already set up")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    from skill_version import check_skill_version
    sys.exit(main(check_skill_version(sys.argv)))
