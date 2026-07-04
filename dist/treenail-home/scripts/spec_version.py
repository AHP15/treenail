"""spec_version.py — per-project spec-version marker + guard (T-022, D-010, R-012).

Per-project conventions are frozen at adoption (D-010): a project's records
were written against the spec version it adopted. Without a version marker, the
record-parsing scripts would have to stay backward-compatible with every past
schema forever, or — worse — silently misparse a project written against a
*newer* spec than this runtime knows. The adoption bootstrap stamps the spec
version into `<docs>/.treenail-version`; the scripts read it and refuse loudly
on a version this runtime does not support, rather than guessing.

An absent marker means a pre-marker (or not-yet-stamped) project: the scripts
proceed on a best-effort basis, exactly as before, so nothing that already
works breaks. The guard only fires when a marker is present and unknown.
"""
import os
import sys

# The record schema this runtime speaks. Bump on any breaking spec change and
# add the old value's migration story; every value we can still parse stays in
# SUPPORTED.
SPEC_VERSION = "1"
SUPPORTED = {"1"}
MARKER = ".treenail-version"


def scope_from_argv(argv):
    """The scope dir a record-parsing script was invoked on: its first
    positional argument (scripts take `<scope-dir>` first). None if absent."""
    for a in argv[1:]:
        if not a.startswith("-"):
            return a
    return None


def _marker_path(scope_dir):
    """Locate the marker for a scope. It lives at the docs root, so a feature
    scope (docs/features/<name>) resolves to the project's docs/.treenail-version."""
    candidates = [os.path.join(scope_dir, MARKER)]
    if os.path.basename(os.path.dirname(os.path.abspath(scope_dir))) == "features":
        candidates.append(os.path.join(scope_dir, "..", "..", MARKER))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def check_spec_version(scope_dir):
    """Refuse loudly if the scope carries a spec-version marker this runtime
    does not support. No-op when scope_dir is None or unmarked."""
    if not scope_dir:
        return
    marker = _marker_path(scope_dir)
    if marker is None:
        return
    with open(marker, encoding="utf-8") as fh:
        found = fh.read().strip()
    if found not in SUPPORTED:
        sys.stderr.write(
            f"Treenail spec version {found!r} in {marker} is not supported by "
            f"this runtime (supports: {', '.join(sorted(SUPPORTED))}). Refusing "
            f"to parse records rather than guess the schema — run "
            f"`npx treenail update`, or migrate the project's docs/ to a "
            f"supported spec version.\n")
        sys.exit(4)
