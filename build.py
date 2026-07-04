#!/usr/bin/env python3
"""build.py — compile the canonical skills/ source into per-provider dists.

One canonical source (Claude-style SKILL.md, authored agent-neutrally per
D-005) is compiled by a per-provider adapter into a complete, installable
tree under dist/<provider>/ (D-004). Adding an agent means adding an
adapter, never another maintained copy.

Usage:
    build.py [provider ...]     build the named providers (default: all)
    build.py --check [provider ...]
                                build to a temp dir and diff against the
                                committed dist/; exit 1 if out of sync

Output is deterministic: two builds over the same source are
byte-identical, so CI can verify dist/ is in sync with source (D-012).
"""

import filecmp
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(ROOT, "skills")
DIST_DIR = os.path.join(ROOT, "dist")

# The shared runtime lives in an agent-neutral ~/.treenail, overridable via
# TREENAIL_HOME (D-006). The build rewrites every shared-asset reference in
# the canonical sources — which historically point into
# ~/.claude/skills/_shared — to the ~/.treenail layout. Order matters: the
# most specific prefixes first, then the bare catch-all.
TREENAIL_HOME_REWRITES = (
    ("~/.claude/skills/_shared/scripts/", "~/.treenail/scripts/"),
    ("~/.claude/skills/_shared/", "~/.treenail/"),
    ("~/.claude/skills/_templates/", "~/.treenail/templates/"),
    ("../_shared/scripts/", "~/.treenail/scripts/"),
    ("../_shared/", "~/.treenail/"),
    ("_shared/scripts/", "~/.treenail/scripts/"),
    ("_shared/conventions-spec.md", "~/.treenail/conventions-spec.md"),
    ("_shared/conventions-examples.md", "~/.treenail/conventions-examples.md"),
    # template placement prose: with scripts in ~/.treenail, the old
    # "sibling of _shared" constraint reduces to "in the skills dir"
    ("a sibling of `_shared`", "in your agent's skills directory"),
    ("a SIBLING of _shared:", "your agent's skills directory:"),
)

TREENAIL_HOME_NOTE = (
    "> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail "
    "runtime. If the `TREENAIL_HOME` environment variable is set, read every "
    "`~/.treenail/...` path as `$TREENAIL_HOME/...` instead.\n\n"
)

# Per-provider preamble injected into every built skill body (T-026,
# D-005, R-004). Content comes from the T-025 degradation spike
# (docs/spike-agent-degradation.md): the interview protocol survives on
# both providers, but there is no option-picker UI, and Evidence anchor
# formatting drifted without an explicit rule.
INTERVIEW_NOTE = (
    "when a step calls for interviewing the user, ask each question in "
    "plain prose — state your recommended answer, ask if it works, and "
    "wait for the reply; there is no option-picker UI. "
    "When writing multiple Evidence anchors, comma-separate them and "
    "backtick each one."
)

PROVIDER_NOTES = {
    "opencode": (
        "> Provider note (opencode): " + INTERVIEW_NOTE + " Steps that "
        "write records shell out to `~/.treenail` scripts and need file-write "
        "permission; in non-interactive runs approval must be granted up "
        "front.\n\n"
    ),
    "codex": (
        "> Provider note (Codex CLI): " + INTERVIEW_NOTE + "\n\n"
    ),
}


def rewrite_shared_refs(text):
    for old, new in TREENAIL_HOME_REWRITES:
        text = text.replace(old, new)
    return text

# Support trees copied alongside the skills: the shared runtime and the
# fill-in templates. Placement is the adapter's call.
SUPPORT_DIRS = ("_shared", "_templates")

# Source files that are neither a skill nor a support dir but ship with
# the pack (the pipeline guide).
EXTRA_FILES = ("guide.md",)

# Never copied into any dist.
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".gitkeep")


def parse_frontmatter(text):
    """Return (frontmatter-dict, body) for a SKILL.md. Minimal parser for
    the flat `key: value` frontmatter the skills use — not general YAML."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm, m.group(2)


class Skill:
    """One canonical skill: its directory name, parsed frontmatter, body,
    and the paths of any support files shipped inside the skill dir."""

    def __init__(self, name, src_dir):
        self.name = name
        self.src_dir = src_dir
        with open(os.path.join(src_dir, "SKILL.md"), encoding="utf-8") as fh:
            self.raw = fh.read()
        self.frontmatter, self.body = parse_frontmatter(self.raw)


def discover_skills():
    """Every directory under skills/ holding a SKILL.md, sorted by name.
    Support dirs (_shared, _templates) are handled separately."""
    skills = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        src = os.path.join(SKILLS_DIR, name)
        if name in SUPPORT_DIRS or not os.path.isdir(src):
            continue
        if os.path.isfile(os.path.join(src, "SKILL.md")):
            skills.append(Skill(name, src))
    return skills


# ---------------------------------------------------------------------------
# Adapters. Each maps (skills, support dirs, extras) → an installable tree.
# The build core guarantees a clean output dir and deterministic ordering;
# the adapter owns layout and any per-provider transforms.
# ---------------------------------------------------------------------------

def _copy_tree(src, dst):
    shutil.copytree(src, dst, ignore=IGNORE)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _filter_frontmatter(skill, allowed):
    """Frontmatter reduced to the keys the provider recognizes, preserving
    source order (None = keep all). Defensive: today the canonical
    frontmatter is exactly name+description, but a future Claude-only field
    must never leak into a stricter provider's parser."""
    kept = []
    m = re.match(r"^---\n(.*?)\n---\n", skill.raw, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            key = line.partition(":")[0].strip()
            if line.startswith((" ", "\t")) and kept:
                kept.append(line)          # continuation of a kept value
            elif allowed is None or key in allowed:
                kept.append(line)
    return "---\n" + "\n".join(kept) + "\n---\n"


def _emit_skill_dirs(out, skills, allowed, note=""):
    """Every provider tree is skill dirs only: shared assets live in
    ~/.treenail (D-006), so bodies are rewritten to reference it — never a
    colocated _shared — and carry the TREENAIL_HOME-override note. `note` is
    the provider's capability preamble (PROVIDER_NOTES), injected first
    so it frames everything after it."""
    for skill in skills:
        body = rewrite_shared_refs(skill.body)
        if "~/.treenail" in body:
            body = TREENAIL_HOME_NOTE + body.lstrip("\n")
        if note:
            body = note + body.lstrip("\n")
        _write(os.path.join(out, skill.name, "SKILL.md"),
               _filter_frontmatter(skill, allowed) + body)


def build_claude(out):
    """Claude Code: the canonical format IS Claude's — full frontmatter,
    body rewritten to the ~/.treenail runtime paths."""
    _emit_skill_dirs(out, discover_skills(), None)


def build_opencode(out):
    """opencode reads Claude-style agent skills from
    ~/.config/opencode/skills/<name>/SKILL.md, but recognizes only these
    frontmatter fields (and requires name to match the dir, which the
    canonical sources already do)."""
    allowed = {"name", "description", "license", "compatibility", "metadata"}
    _emit_skill_dirs(out, discover_skills(), allowed,
                     note=PROVIDER_NOTES["opencode"])


def build_codex(out):
    """Codex loads any directory carrying a SKILL.md under ~/.codex/skills/
    and matches on the description field; name+description is the shared
    agent-skills core, so emit exactly that."""
    allowed = {"name", "description"}
    _emit_skill_dirs(out, discover_skills(), allowed,
                     note=PROVIDER_NOTES["codex"])


# The plugin channel installs skill text through Claude's plugin system,
# bypassing the npx installer (R-007). The plugin therefore carries the
# whole shared runtime in runtime/ and a SessionStart hook provisions
# ~/.treenail from it: copy when missing, replace when the bundled version is
# newer. Skill bodies stay identical to dist/claude — they keep reading
# ~/.treenail, so CLI-managed and plugin-managed installs share one runtime.
BOOTSTRAP_SCRIPT = '''\
#!/usr/bin/env python3
"""Provision ~/.treenail (or $TREENAIL_HOME) from the runtime bundled in the Treenail
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
    home = os.environ.get("TREENAIL_HOME") or os.path.join(
        os.path.expanduser("~"), ".treenail")
    bundled = read_version(BUNDLED)
    if bundled is None:
        return 0  # damaged bundle; never touch an existing install
    installed = as_tuple(read_version(home))
    if installed is not None and installed >= as_tuple(bundled):
        return 0
    if os.path.lexists(home):
        shutil.rmtree(home, ignore_errors=False)
    shutil.copytree(BUNDLED, home)
    print(f"Treenail runtime {bundled} provisioned at {home}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

# Try the per-platform Python spellings (D-009); if none works, exit
# quietly — the scripted-step preflight and runtime-missing messaging
# (T-020/T-021) own that failure at the point of use.
BOOTSTRAP_CMD = " || ".join(
    f'{py} "${{CLAUDE_PLUGIN_ROOT}}/scripts/bootstrap_treenail_home.py" 2>/dev/null'
    for py in ("python3", "python", "py -3")
) + " || exit 0"


def build_claude_plugin(out):
    """Claude Code plugin (D-007): the dist/claude skill set plus the
    bundled shared runtime and a SessionStart bootstrap hook, laid out in
    Claude's plugin format. Installed from the marketplace manifest at the
    repo root (.claude-plugin/marketplace.json)."""
    _emit_skill_dirs(os.path.join(out, "skills"), discover_skills(), None)
    build_treenail_home(os.path.join(out, "runtime"))
    version = read_cli_version()
    _write(
        os.path.join(out, ".claude-plugin", "plugin.json"),
        json.dumps(
            {
                "name": "treenail",
                "description": (
                    "Treenail planning-skills pack: decision, risk, and task "
                    "pipeline skills for agent-driven planning."
                ),
                "version": version,
                "author": {"name": "abdessittir"},
                "homepage": "https://github.com/AHP15/treenail",
                "license": "MIT",
            },
            indent=2,
        ) + "\n",
    )
    _write(
        os.path.join(out, "hooks", "hooks.json"),
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {"hooks": [{"type": "command",
                                    "command": BOOTSTRAP_CMD}]}
                    ]
                }
            },
            indent=2,
        ) + "\n",
    )
    _write(os.path.join(out, "scripts", "bootstrap_treenail_home.py"),
           BOOTSTRAP_SCRIPT)


def read_cli_version():
    with open(os.path.join(ROOT, "cli", "package.json"),
              encoding="utf-8") as fh:
        return json.load(fh)["version"]


def build_treenail_home(out):
    """The shared runtime tree the installer provisions into ~/.treenail
    (D-006): scripts, templates, conventions spec/examples, guide, VERSION.
    Scripts are copied byte-for-byte (they are code); prose assets get the
    same reference rewrite as skill bodies."""
    shutil.copytree(os.path.join(SKILLS_DIR, "_shared", "scripts"),
                    os.path.join(out, "scripts"),
                    ignore=shutil.ignore_patterns(
                        "__pycache__", "*.pyc", ".DS_Store", ".gitkeep",
                        "tests"))  # tests run from the repo, not ~/.treenail
    src_templates = os.path.join(SKILLS_DIR, "_templates")
    for dirpath, dirnames, filenames in os.walk(src_templates):
        dirnames.sort()
        for name in sorted(filenames):
            if name in (".DS_Store", ".gitkeep"):
                continue
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, src_templates)
            with open(src, encoding="utf-8") as fh:
                _write(os.path.join(out, "templates", rel),
                       rewrite_shared_refs(fh.read()))
    for name in ("conventions-spec.md", "conventions-examples.md"):
        with open(os.path.join(SKILLS_DIR, "_shared", name),
                  encoding="utf-8") as fh:
            _write(os.path.join(out, name), rewrite_shared_refs(fh.read()))
    for extra in EXTRA_FILES:
        with open(os.path.join(SKILLS_DIR, extra), encoding="utf-8") as fh:
            _write(os.path.join(out, extra), rewrite_shared_refs(fh.read()))
    _write(os.path.join(out, "VERSION"), read_cli_version() + "\n")


ADAPTERS = {
    "claude": build_claude,
    "claude-plugin": build_claude_plugin,
    "opencode": build_opencode,
    "codex": build_codex,
    "treenail-home": build_treenail_home,
}


def build_provider(provider, dist_root):
    out = os.path.join(dist_root, provider)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    ADAPTERS[provider](out)


def tree_differs(a, b):
    """True if directory trees a and b differ anywhere (names or bytes)."""
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    return any(tree_differs(os.path.join(a, d), os.path.join(b, d))
               for d in cmp.common_dirs)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    check = "--check" in argv[1:]
    providers = args or sorted(ADAPTERS)
    for p in providers:
        if p not in ADAPTERS:
            print(f"build.py: unknown provider '{p}' "
                  f"(have: {', '.join(sorted(ADAPTERS))})", file=sys.stderr)
            return 2

    if check:
        rc = 0
        tmp = tempfile.mkdtemp(prefix="treenail-build-check-")
        try:
            for p in providers:
                build_provider(p, tmp)
                committed = os.path.join(DIST_DIR, p)
                if not os.path.isdir(committed) or \
                        tree_differs(os.path.join(tmp, p), committed):
                    print(f"OUT OF SYNC: dist/{p} does not match a fresh build")
                    rc = 1
                else:
                    print(f"ok: dist/{p} in sync")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return rc

    for p in providers:
        build_provider(p, DIST_DIR)
        if p == "treenail-home":
            print("built dist/treenail-home (shared runtime tree)")
        else:
            print(f"built dist/{p} ({len(discover_skills())} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
