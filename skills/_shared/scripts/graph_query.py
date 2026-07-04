#!/usr/bin/env python3
"""graph_query.py — advisory semantic recall over the Graphiti projection.

Used by the retrieval skills (challenge-me, red-team-me, promote) to ask
"what prior decisions/risks are semantically related to this?", including
ACROSS scopes — the question the deterministic explicit-link graph cannot
answer. It is strictly advisory: results are candidates for the skill (and
the user) to consider, never authority. If the graph is unavailable it
prints nothing and exits 0, so the calling skill simply proceeds without
prior-art suggestions.

Usage:
    graph_query.py <project-scope-dir> "<query text>" [-k N] [--scope MODE]

  <project-scope-dir>  the PROJECT docs root (`docs`), even when querying
                       on behalf of a feature — cross-scope recall is the
                       point.
  "<query text>"       free text: a decision title, a risk description, a
                       design question.
  -k N                 max results (default 8).
  --scope MODE         which group_ids to search:
                         all      project + every feature (default)
                         project  project only
                         feature:<name>   one feature only

Output: one line per hit — the related record's fact, with the source IDs
it mentions, so the skill can pull the specific `<ID>.md` if it wants the
full body. Never modifies anything.

Exit codes: 0 always (advisory). 2 only on usage error.
"""

import asyncio
import os
import re
import sys

import graph_common as gc


def parse_args(argv):
    pos, k, scope_mode = [], 8, "all"
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "-k":
            k = int(argv[i + 1]); i += 2; continue
        if a == "--scope":
            scope_mode = argv[i + 1]; i += 2; continue
        pos.append(a); i += 1
    return pos, k, scope_mode


def group_ids(project_scope, scope_mode):
    if scope_mode == "all":
        return gc.all_group_ids(project_scope)
    if scope_mode == "project":
        return ["project"]
    return [scope_mode]  # an explicit "feature:<name>"


ID_RE = re.compile(r"\b[DRT]-\d+\b")


async def run_search(query, gids, k):
    client = gc.get_client()  # may raise GraphUnavailable
    # Graphiti's hybrid search (semantic + BM25 + graph) over edges/facts.
    results = await client.search(query, group_ids=gids, num_results=k)
    return results


def advise_if_configured(reason):
    """R-026: a configured-but-unreachable Graphiti must not be
    indistinguishable from an unconfigured one. If the user opted into a
    backend via env, emit one stderr line so a broken setup is diagnosable;
    otherwise stay fully silent so absence remains safe (D-013). Goes to
    stderr so stdout (the prior-art results) stays clean and parseable.
    """
    if gc.graphiti_configured():
        print(f"graph_query.py: Graphiti configured but unreachable: "
              f"{reason}; proceeding without prior-art", file=sys.stderr)


def main(argv):
    pos, k, scope_mode = parse_args(argv)
    if len(pos) < 2:
        print('usage: graph_query.py <project-scope-dir> "<query>" '
              '[-k N] [--scope MODE]', file=sys.stderr)
        return 2
    project_scope, query = pos[0], pos[1]
    if not os.path.isdir(project_scope):
        print(f"graph_query.py: no such scope dir: {project_scope}",
              file=sys.stderr)
        return 2
    gids = group_ids(project_scope, scope_mode)

    try:
        results = asyncio.run(run_search(query, gids, k))
    except gc.GraphUnavailable as e:
        # Advisory: stay silent when unconfigured so the calling skill
        # proceeds cleanly; warn once when the user configured a backend
        # that isn't reachable (R-026).
        advise_if_configured(e)
        return 0
    except Exception as e:
        advise_if_configured(e)
        return 0

    if not results:
        print("(no related prior records found)")
        return 0

    print(f"prior art for: {query!r}  (scope={scope_mode}, top {k})")
    for r in results:
        fact = getattr(r, "fact", None) or str(r)
        ids = ",".join(sorted(set(ID_RE.findall(fact)))) or "—"
        print(f"  [{ids}] {fact}")
    return 0


if __name__ == "__main__":
    # Report output is machine-parsed, so emit deterministic UTF-8
    # regardless of console code page — Windows cp1252 or a POSIX C
    # locale must never crash on report typography (—, ≤, →) (R-010).
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    from skill_version import check_skill_version
    from spec_version import check_spec_version, scope_from_argv
    argv = check_skill_version(sys.argv)
    check_spec_version(scope_from_argv(argv))
    sys.exit(main(argv))
