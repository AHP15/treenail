#!/usr/bin/env python3
"""mint_id.py — atomically claim the next per-record ID for an artifact.

Implements the "ID reservation protocol" from CONVENTIONS-SPEC.md:
the filesystem (active + archive dirs), not the INDEX, is the arbiter,
so concurrent minters in different sessions/branches cannot collide.

Usage:   mint_id.py <artifact-dir> <PREFIX>
Example: mint_id.py docs/decisions D
         mint_id.py docs/features/oauth-login/risks R

On success prints the claimed ID and its path, tab-separated, e.g.:
  D-007	docs/decisions/D-007.md
and creates the file as an EMPTY claim. The caller then writes the
body and appends the INDEX line (or runs reindex.py). If the process
dies after the claim but before the body is written, the empty file
is a harmless malformed record that audit-artifacts flags and reindex
reports — it never causes an ID collision.

Exit codes: 0 ok; 2 usage error; 3 could not claim within bound.
"""

import os
import re
import sys


def main(argv):
    if len(argv) != 3:
        print("usage: mint_id.py <artifact-dir> <PREFIX>", file=sys.stderr)
        return 2

    dirpath, prefix = os.path.expanduser(argv[1]), argv[2]
    archive = os.path.join(dirpath, "archive")
    os.makedirs(archive, exist_ok=True)

    # Compute the candidate: max numeric ID across BOTH active and archive,
    # because IDs are unique within scope across both. INDEX is never read
    # here — it may lag the files.
    pat = re.compile(r"^" + re.escape(prefix) + r"-(\d+)\.md$")
    max_id = 0
    for d in (dirpath, archive):
        for name in os.listdir(d):
            m = pat.match(name)
            if m:
                max_id = max(max_id, int(m.group(1)))

    candidate = max_id + 1
    limit = 1000

    for _ in range(limit):
        rid = "%s-%03d" % (prefix, candidate)
        path = os.path.join(dirpath, rid + ".md")
        # Atomic, no-clobber claim: O_CREAT|O_EXCL fails if the path
        # already exists on all supported OSes; that failure means a
        # concurrent minter won this number, so increment and retry.
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            candidate += 1
            continue
        os.close(fd)
        print("%s\t%s" % (rid, path))
        return 0

    print("mint_id.py: could not claim an ID within %d attempts" % limit,
          file=sys.stderr)
    return 3


if __name__ == "__main__":
    # Report output is machine-parsed, so emit deterministic UTF-8
    # regardless of console code page — Windows cp1252 or a POSIX C
    # locale must never crash on report typography (—, ≤, →) (R-010).
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv))
