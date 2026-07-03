#!/usr/bin/env python3
"""graph_sync.py — project planning records into the optional Graphiti graph.

ONE-WAY projection: records (the source of truth) -> Graphiti (a derived,
advisory semantic index). Never reads the graph back into a record. The
graph can be wiped and rebuilt from the files at any time, exactly like
INDEX.md — that is what keeps Graphiti's LLM-based extraction from ever
threatening the deterministic pipeline.

Incremental by default: a per-scope state file `<scope>/.graph-sync.json`
maps each record ID to the content hash last sent, so only changed records
are re-sent (each `add_episode` costs LLM tokens, so this matters). Pass
--rebuild to ignore the state and re-send everything.

Usage:
    graph_sync.py <scope-dir> [--rebuild] [--dry-run]

  <scope-dir>  docs root for the scope (e.g. `docs` or
               `docs/features/<feature>`). Its group_id is derived from
               the path: `docs` -> "project", a feature dir ->
               "feature:<name>".
  --rebuild    ignore the sync-state file; re-send every record.
  --dry-run    parse and project records and print what WOULD be sent, but
               do not connect to or write the graph. Works with no
               graphiti-core installed — use it to validate the
               record->episode mapping offline.

Exit codes:
  0  success (including a clean no-op, and including the advisory-skip
     when the graph is unavailable and this was not a --dry-run)
  2  usage error

Note: the graph being unavailable is NOT an error — sync is advisory. It
prints a notice and exits 0 so a session/hook that calls it never breaks.
"""

import asyncio
import json
import os
import sys

import graph_common as gc


def load_state(scope):
    path = os.path.join(scope, ".graph-sync.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}


def save_state(scope, state):
    path = os.path.join(scope, ".graph-sync.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=0, sort_keys=True)
        fh.write("\n")


def plan(scope, rebuild):
    """Return (to_send, state) where to_send is a list of episode dicts for
    records whose body changed since last sync (or all, if rebuild)."""
    group_id = gc.group_id_for(scope)
    prior = {} if rebuild else load_state(scope)
    state = dict(prior)
    to_send = []
    for artifact in ("decisions", "risks", "tasks"):
        for rid, title, fields, _active in gc.iter_records(scope, artifact):
            body = gc.episode_body(artifact, rid, title, fields, group_id)
            h = gc.content_hash(body)
            key = f"{group_id}:{rid}"
            if prior.get(key) == h:
                continue  # unchanged since last sync
            to_send.append({
                "key": key,
                "name": key,
                "artifact": artifact,
                "rid": rid,
                "body": body,
                "ref_date": gc.reference_date(artifact, fields),
                "source_description": f"planning-artifact:{artifact}",
                "group_id": group_id,
                "hash": h,
            })
            state[key] = h
    return to_send, state, group_id


async def send(client, to_send):
    from datetime import datetime, timezone
    from graphiti_core.nodes import EpisodeType
    # Idempotent: creates Neo4j indices/constraints on first run, no-op after.
    await client.build_indices_and_constraints()
    for ep in to_send:
        ref = datetime.now(timezone.utc)
        if ep["ref_date"]:
            ref = datetime.fromisoformat(ep["ref_date"]).replace(
                tzinfo=timezone.utc)
        await client.add_episode(
            name=ep["name"],
            episode_body=ep["body"],
            source=EpisodeType.text,
            source_description=ep["source_description"],
            reference_time=ref,
            group_id=ep["group_id"],
        )


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print("usage: graph_sync.py <scope-dir> [--rebuild] [--dry-run]",
              file=sys.stderr)
        return 2
    scope = os.path.expanduser(args[0])
    if not os.path.isdir(scope):
        print(f"graph_sync.py: no such scope dir: {scope}", file=sys.stderr)
        return 2
    rebuild = "--rebuild" in flags
    dry = "--dry-run" in flags

    to_send, state, group_id = plan(scope, rebuild)

    print(f"graph-sync {scope}  (group_id={group_id}, "
          f"{'rebuild' if rebuild else 'incremental'})")
    if not to_send:
        print("  up to date — nothing changed since last sync")
        return 0
    for ep in to_send:
        print(f"  {'WOULD send' if dry else 'send'}  {ep['rid']:7} "
              f"[{ep['artifact']}]  ref={ep['ref_date'] or 'now'}")

    if dry:
        print(f"\n--dry-run: {len(to_send)} episode(s) projected, none sent.")
        return 0

    try:
        client = gc.get_client()
    except gc.GraphUnavailable as e:
        print(f"\n  graph unavailable ({e}); sync skipped (advisory index). "
              f"State file NOT advanced — records will sync once the graph "
              f"is configured.")
        return 0

    try:
        asyncio.run(send(client, to_send))
    except Exception as e:
        print(f"\n  graph write failed ({e}); state NOT advanced.",
              file=sys.stderr)
        return 0
    save_state(scope, state)
    print(f"\n  sent {len(to_send)} episode(s); state advanced.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
