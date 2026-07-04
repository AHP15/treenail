"""skill_version.py — runtime version handshake (T-018, D-014, R-008).

Multi-channel installs can leave the skill text a user is reading at one
version and the ~/.treenail runtime at another (skew). The build stamps the
skill-pack version into each skill body (T-017); skills pass it to scripts as
`--skill-version X`. This helper strips that flag from argv and, when present,
compares it against ~/.treenail/VERSION — turning silent skew into one
actionable line instead of a confusing downstream failure.

Absent flag = no check (backward compatible): a direct invocation or an older
skill body simply skips the handshake. A missing/unreadable runtime VERSION is
the T-020 runtime-missing case, owned elsewhere; here it just means "cannot
compare", so we do not block.
"""
import os
import sys


def _runtime_home(env=os.environ):
    return env.get("TREENAIL_HOME") or os.path.join(
        os.path.expanduser("~"), ".treenail")


def _read_runtime_version():
    try:
        with open(os.path.join(_runtime_home(), "VERSION"),
                  encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return None


def check_skill_version(argv):
    """Return argv with any `--skill-version X` (or `--skill-version=X`)
    removed. If it was present and mismatches ~/.treenail/VERSION, print a
    one-line actionable error and exit non-zero."""
    out = [argv[0]] if argv else []
    skill_v = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--skill-version":
            if i + 1 < len(argv):
                skill_v = argv[i + 1]
                i += 2
                continue
            i += 1
            continue
        if a.startswith("--skill-version="):
            skill_v = a.split("=", 1)[1]
            i += 1
            continue
        out.append(a)
        i += 1

    if skill_v is not None:
        runtime_v = _read_runtime_version()
        if runtime_v is not None and skill_v != runtime_v:
            sys.stderr.write(
                f"skill text v{skill_v} / runtime v{runtime_v} — "
                f"run npx treenail update\n")
            sys.exit(3)
    return out
