#!/usr/bin/env python3
"""Guard the MCS upgrade ledger (mcs-ledger-check-parity) — the repo-local twin of
open-claw-stuff's concept-ledger-check.

Soli Deo Gloria.

Checks docs/UPGRADE-LEDGER.md:
  1. MCS ids are UNIQUE (a duplicate id makes every citation ambiguous — OCS earned
     fifteen of these before its checker existed).
  2. Every row's status cell carries a sanctioned state: candidate / tracked /
     implemented / decided-no (per docs/UPGRADE-LEDGER-STANDARD.md §3).
  3. `tracked` pointers name a real HLS task — checked against the household catalog
     when it is reachable. THREE STATES, never two: OK / MISMATCH / UNAVAILABLE.
     When the catalog cannot be read (standalone clone), the pointer phase reports
     UNAVAILABLE loudly and does not block — "nothing found" from a check that never
     looked is the false-CALM this household keeps paying for. Id uniqueness and
     status sanity are local facts and always bind.

--next-id prints the next free MCS id from THIS FILE ONLY, and says so — it cannot
see unmerged branches (the UL allocator's lesson); detection at merge time via check 1
remains the real guarantee.

Exit 0 clean · 1 findings · 2 usage.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LEDGER = REPO_ROOT / "docs" / "UPGRADE-LEDGER.md"
CATALOG_CANDIDATES = [
    REPO_ROOT.parent / "open-claw-stuff" / ".household-library" / "catalog.jsonl",
]

VALID_STATES = ("candidate", "tracked", "implemented", "decided-no")
ROW_RE = re.compile(r"^\| (MCS-\d+) \|(.+)\|\s*$")


def parse_rows(text):
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        m = ROW_RE.match(line)
        if m:
            cells = [c.strip() for c in line.split("|")]
            rows.append({"id": m.group(1), "line": n, "status": cells[-2] if len(cells) >= 2 else ""})
    return rows


def catalog_task_ids():
    for p in CATALOG_CANDIDATES:
        if p.exists():
            ids = set()
            for line in p.read_text().splitlines():
                if line.strip():
                    try:
                        ids.add(json.loads(line).get("task_id"))
                    except json.JSONDecodeError:
                        pass
            return ids, str(p)
    return None, None


def main():
    if not LEDGER.exists():
        print("ledger-check: docs/UPGRADE-LEDGER.md MISSING — the 9th ledger is gone again "
              "(it vanished once via a stranded branch; that is why this checker exists).")
        return 1
    text = LEDGER.read_text()
    rows = parse_rows(text)
    findings = []

    if "--next-id" in sys.argv:
        nxt = max((int(r["id"].split("-")[1]) for r in rows), default=0) + 1
        print(f"MCS-{nxt}  (from THIS FILE only — cannot see unmerged branches; "
              f"duplicate detection at merge time is the real guarantee)")
        return 0

    seen = {}
    for r in rows:
        if r["id"] in seen:
            findings.append(f"DUPLICATE id {r['id']} (lines {seen[r['id']]} and {r['line']})")
        seen[r["id"]] = r["line"]

    for r in rows:
        if not any(s in r["status"] for s in VALID_STATES):
            findings.append(f"{r['id']} (line {r['line']}): status cell has no sanctioned state "
                            f"{VALID_STATES}: {r['status'][:80]!r}")

    tracked = re.findall(r"`tracked` → `([a-z0-9-]+)`", text)
    ids, src = catalog_task_ids()
    if ids is None:
        print(f"ledger-check: pointer phase UNAVAILABLE — household catalog not reachable "
              f"from this clone ({len(tracked)} tracked pointers UNVERIFIED, not verified-clean).")
    else:
        for t in tracked:
            if t not in ids:
                findings.append(f"tracked pointer `{t}` names no task in the catalog ({src})")

    if findings:
        print(f"ledger-check: {len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"ledger-check: clean — {len(rows)} rows, ids unique, states sane"
          + (f", {len(tracked)} tracked pointers verified against catalog" if ids is not None else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
