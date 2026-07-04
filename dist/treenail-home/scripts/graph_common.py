#!/usr/bin/env python3
"""graph_common.py — shared helpers for the optional Graphiti projection.

The planning pipeline's source of truth is the per-record `<ID>.md` files
plus git history. The Graphiti graph is a **derived, advisory index** —
like INDEX.md, but semantic. It is one-way (files → graph), never
authoritative, and every consumer MUST degrade gracefully when it is
unavailable, so the deterministic pipeline keeps working with no graph at
all.

This module centralizes three things the sync and query scripts share:
  - connecting to Graphiti from env (raising GraphUnavailable, never
    crashing, when it isn't configured);
  - mapping a scope dir to a stable Graphiti `group_id`;
  - projecting one parsed record into a deterministic episode body.

It deliberately does NOT depend on a running graph at import time, so the
`--dry-run` paths of the callers work with no `graphiti-core` installed.

Env it reads (all optional; absence => GraphUnavailable):
  GRAPHITI_BACKEND   "neo4j" (default) | "falkordb"
  NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD     for the neo4j backend
  FALKORDB_URI                                 for the falkordb backend
  OPENAI_API_KEY (or whatever your Graphiti LLM/embedder needs)
"""

import hashlib
import os
import re

import reindex  # same dir; reuses parse_record / PREFIX / ids_in


class GraphUnavailable(Exception):
    """Raised when Graphiti is not installed or not configured. Callers
    catch this and no-op (advisory index), never propagate it as a hard
    failure of the pipeline."""


# ---------------------------------------------------------------------------
# scope -> group_id
# ---------------------------------------------------------------------------

def group_id_for(scope_dir):
    """Stable Graphiti group_id for a docs scope.

    `docs`                       -> "project"
    `docs/features/oauth-login`  -> "feature:oauth-login"

    group_ids partition the graph so a query can target one scope, or pass
    several to deliberately search across scopes (the "have we decided this
    before, anywhere?" query the hook skills want).
    """
    norm = scope_dir.replace(os.sep, "/").rstrip("/")
    m = re.search(r"/features/([^/]+)/?$", norm)
    if m:
        return f"feature:{m.group(1)}"
    return "project"


def all_group_ids(project_scope):
    """Every group_id under a project: "project" plus one per feature dir.
    Used by the hook skills for cross-scope recall."""
    out = ["project"]
    feat_root = os.path.join(project_scope, "features")
    if os.path.isdir(feat_root):
        for name in sorted(os.listdir(feat_root)):
            if os.path.isdir(os.path.join(feat_root, name)):
                out.append(f"feature:{name}")
    return out


# ---------------------------------------------------------------------------
# record -> episode projection (deterministic)
# ---------------------------------------------------------------------------

ARTIFACT_KIND = {"decisions": "decision", "risks": "risk", "tasks": "task"}

# Which field carries the record's authoritative time, for Graphiti's
# bi-temporal reference_time. Falls back to None (caller uses now()).
REF_DATE_FIELD = {
    "decisions": ["Date superseded", "Date deprecated", "Date promoted", "Date"],
    "risks": ["Date resolved", "Date"],
    "tasks": ["Date done", "Date dropped"],
}

LINK_FIELDS = [
    "Supersedes", "Superseded by", "Promoted to", "Promoted from",
    "Implements", "Mitigates", "Depends on", "Related decisions", "Action",
]

BODY_FIELDS = {
    "decisions": ["Status", "Date", "Date superseded", "Date deprecated",
                  "Date promoted", "Context", "Decision", "Rationale"],
    "risks": ["Severity", "Likelihood", "Disposition", "Date",
              "Date resolved", "Description", "Disposition rationale"],
    "tasks": ["Status", "Size", "Acceptance", "Date done", "Date dropped", "Notes"],
}


def reference_date(artifact, fields):
    iso = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for name in REF_DATE_FIELD[artifact]:
        v = (fields.get(name) or "").strip()
        if iso.match(v):
            return v
    return None


def episode_body(artifact, rid, title, fields, group_id):
    """A compact, deterministic text projection of a record for Graphiti.

    It is plain text (good for the embedder) but leads with the record's
    unique ID token and all explicit link IDs, so Graphiti anchors its
    extracted entities/edges to the IDs we already maintain rather than
    inventing its own. Two runs over the same record produce identical
    text -> a stable content hash -> idempotent sync.
    """
    kind = ARTIFACT_KIND[artifact]
    lines = [f"[{rid}] {title}", f"scope: {group_id} | type: {kind}"]
    for name in BODY_FIELDS[artifact]:
        v = (fields.get(name) or "").strip()
        if v:
            lines.append(f"{name}: {v}")
    links = []
    for name in LINK_FIELDS:
        v = (fields.get(name) or "").strip()
        if v:
            links.append(f"{name}={v}")
    if links:
        lines.append("links: " + " ; ".join(links))
    return "\n".join(lines)


def content_hash(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def iter_records(scope_dir, artifact):
    """Yield (rid, title, fields, is_active) for active + archived records
    of one artifact, reusing reindex's authoritative parser."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope_dir, artifact)
    for active, d in ((True, base), (False, os.path.join(base, "archive"))):
        for path in reindex.record_files(d, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid is None:
                continue
            yield rid, title, fields, active


# ---------------------------------------------------------------------------
# Graphiti client (lazy; raises GraphUnavailable instead of crashing)
# ---------------------------------------------------------------------------

def get_client():
    """Return a connected Graphiti client, or raise GraphUnavailable.

    Kept import-lazy so scripts that only need projection/dry-run don't
    require graphiti-core to be installed.
    """
    try:
        from graphiti_core import Graphiti
    except Exception as e:  # not installed
        raise GraphUnavailable(f"graphiti-core not importable: {e}")

    backend = os.environ.get("GRAPHITI_BACKEND", "neo4j").lower()
    try:
        if backend == "falkordb":
            uri = os.environ["FALKORDB_URI"]
            return Graphiti(uri)
        # default: neo4j
        uri = os.environ["NEO4J_URI"]
        user = os.environ["NEO4J_USER"]
        pwd = os.environ["NEO4J_PASSWORD"]
        return Graphiti(uri, user, pwd)
    except KeyError as e:
        raise GraphUnavailable(f"missing env for {backend} backend: {e}")
    except Exception as e:
        raise GraphUnavailable(f"could not construct Graphiti client: {e}")
