#!/usr/bin/env python3
"""Provision ~/.keel (or $KEEL_HOME) from the runtime bundled in the Keel
Claude Code plugin (T-019, R-007). Runs on SessionStart: no-op when the
installed runtime is present and at least as new as the bundle."""

import os
import shutil
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED = os.path.join(PLUGIN_ROOT, "runtime")


def read_version(tree):
    try:
        with open(os.path.join(tree, "VERSION"), encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return None


def as_tuple(version):
    try:
        return tuple(int(p) for p in version.split("."))
    except (AttributeError, ValueError):
        return None


def main():
    home = os.environ.get("KEEL_HOME") or os.path.join(
        os.path.expanduser("~"), ".keel")
    bundled = read_version(BUNDLED)
    if bundled is None:
        return 0  # damaged bundle; never touch an existing install
    installed = as_tuple(read_version(home))
    if installed is not None and installed >= as_tuple(bundled):
        return 0
    if os.path.lexists(home):
        shutil.rmtree(home, ignore_errors=False)
    shutil.copytree(BUNDLED, home)
    print(f"Keel runtime {bundled} provisioned at {home}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
