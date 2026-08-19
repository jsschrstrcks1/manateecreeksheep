#!/usr/bin/env python3
"""fat_tail.py — fat-tail phenotype score + fat-tailed lineage tracking (MCS-20).

Some of this flock carries fat-tailed-breed ancestry — Awassi (9 animals), Tunis (FM is 50%
Tunis), Karakul — where fat stored in the tail/rump is a real, heritable phenotype worth tracking:
it is a fat reserve for hard seasons, but also a carcass and management trait a buyer may price.
Today one animal has a structured fat_tail_observation and three more mention it in prose. This
adds the structured phenotype and cross-references it against the genetic EXPECTATION from breed
composition, so expected-vs-observed disagreements surface instead of hiding.

PHENOTYPE SCORE — a 0-3 convention (this tool's stated scale, tunable):
    0 = thin/normal tail (no fat depot)
    1 = slight fat-tail
    2 = moderate fat-tail
    3 = pronounced fat-tail / fat-rump
Expectation comes from ancestry: an animal with substantial fat-tailed-breed percentage is
EXPECTED to show some fat-tail; a high-Awassi animal with no observation is a collection gap, and
a pronounced fat-tail in an animal with no such ancestry is a note worth a second look.

SHAPE — append-only fat_tail_scores[] (MCS-9 shape): {date, score, observation, observer, notes}.
The pre-existing singular fat_tail_observation dict is read as a legacy observation (not discarded).

    python3 scripts/fat_tail.py                 # lineage view: expected (genetic) vs observed
    python3 scripts/fat_tail.py --json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# Fat-tailed / fat-rumped breeds. Match is case-insensitive substring against breed_composition
# percentage keys. Thin-tailed hair breeds (Katahdin, Dorper, St Croix, Barbados) are absent here
# on purpose — only breeds that carry the fat-tail phenotype belong.
FAT_TAILED_BREEDS = {"awassi": "fat-tailed", "tunis": "fat-tailed", "karakul": "fat-tailed",
                     "damara": "fat-tailed", "blackhead persian": "fat-rumped"}

SCORE_MIN, SCORE_MAX = 0, 3
EXPECT_HIGH = 50    # >=50% fat-tailed ancestry -> strong expectation
EXPECT_SOME = 12    # >=12% -> some expectation (an eighth)
_KEYS = {"date", "score", "observation", "observer", "notes"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def fat_tailed_ancestry(sheep):
    """Total fat-tailed-breed percentage from breed_composition, and the breeds contributing.
    Returns (pct:float, breeds:list). Non-numeric/None percentages are skipped, never summed."""
    bc = sheep.get("breed_composition")
    pct = bc.get("percentages") if isinstance(bc, dict) else None
    total = 0.0
    breeds = []
    if isinstance(pct, dict):
        for k, v in pct.items():
            kl = str(k).lower()
            for breed in FAT_TAILED_BREEDS:
                if breed in kl and isinstance(v, (int, float)) and not isinstance(v, bool):
                    total += float(v)
                    breeds.append(f"{k} {v:g}%")
    return total, breeds


def expectation(pct):
    if pct >= EXPECT_HIGH:
        return "high"
    if pct >= EXPECT_SOME:
        return "some"
    if pct > 0:
        return "trace"
    return "none"


def _observations(sheep):
    """All fat-tail observations for an animal: structured fat_tail_scores[] plus the legacy
    singular fat_tail_observation dict, newest first. Each {date, score?, observation}."""
    obs = []
    for e in (sheep.get("fat_tail_scores") or []):
        if isinstance(e, dict):
            obs.append({"date": e.get("date"), "score": e.get("score"),
                        "observation": e.get("observation")})
    legacy = sheep.get("fat_tail_observation")
    if isinstance(legacy, dict):
        obs.append({"date": legacy.get("date"), "score": None,
                    "observation": legacy.get("observation"), "legacy": True})
    obs.sort(key=lambda o: (_iso(o["date"]) or datetime.min.date()), reverse=True)
    return obs


def record_fat_tail_score(sheep, date, score, observation=None, observer=None, notes=None):
    """Append a fat-tail phenotype score (pure addition, append-only)."""
    ev = {"date": date, "score": score, "observation": observation, "observer": observer, "notes": notes}
    ev = {k: v for k, v in ev.items() if v is not None}
    sheep.setdefault("fat_tail_scores", []).append(ev)
    return ev


def validate_fat_tail(sheep):
    issues = []
    for i, e in enumerate(sheep.get("fat_tail_scores") or []):
        where = f"{sheep.get('id')}#fat_tail_scores[{i}]"
        if not isinstance(e, dict):
            issues.append(f"{where}: not an object"); continue
        extra = set(e) - _KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        if _iso(e.get("date")) is None:
            issues.append(f"{where}: missing/unparseable date {e.get('date')!r}")
        sc = e.get("score")
        if not isinstance(sc, (int, float)) or isinstance(sc, bool) or not (SCORE_MIN <= sc <= SCORE_MAX):
            issues.append(f"{where}: score {sc!r} out of range {SCORE_MIN}-{SCORE_MAX}")
    return issues


def lineage_view(db):
    """Every animal with fat-tailed ancestry OR a fat-tail observation: expected level (genetic)
    vs observed (phenotype), with a flag for the disagreements worth a look."""
    rows = []
    for s in db.get("sheep", []):
        pct, breeds = fat_tailed_ancestry(s)
        obs = _observations(s)
        if pct <= 0 and not obs:
            continue
        exp = expectation(pct)
        latest = obs[0] if obs else None
        flag = None
        if exp in ("high", "some") and not obs:
            flag = "expected fat-tail, no observation on record"
        elif obs and pct <= 0:
            flag = "fat-tail observed with no fat-tailed ancestry on file — verify breed comp"
        rows.append({
            "id": s["id"], "name": s.get("name"), "status": s.get("status"),
            "ancestry_pct": round(pct, 1), "ancestry_breeds": breeds, "expectation": exp,
            "observations": len(obs),
            "latest_score": (latest or {}).get("score"),
            "latest_obs": (latest or {}).get("observation"),
            "flag": flag,
        })
    rows.sort(key=lambda r: -r["ancestry_pct"])
    return rows


def main():
    ap = argparse.ArgumentParser(description="Fat-tail phenotype + lineage (read-only surfaces)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    rows = lineage_view(db)
    issues = []
    for s in db["sheep"]:
        issues += validate_fat_tail(s)

    if args.json:
        print(json.dumps({"lineage": rows, "validation_issues": issues}, indent=2)); return 0

    observed = [r for r in rows if r["observations"]]
    gaps = [r for r in rows if r["flag"] and "no observation" in r["flag"]]
    print(f"Fat-tail lineage — {len(rows)} animals with fat-tailed ancestry or an observation; "
          f"{len(observed)} observed, {len(gaps)} expected-but-unobserved\n")
    print(f"  {'animal':26} {'anc%':>5} {'expect':7} {'obs':>3} {'score':>5}  breeds / flag")
    for r in rows:
        sc = "" if r["latest_score"] is None else str(r["latest_score"])
        tail = "; ".join(r["ancestry_breeds"]) or ""
        if r["flag"]:
            tail = (tail + "  <- " + r["flag"]).strip()
        print(f"  {(r['name'] or r['id'])[:26]:26} {r['ancestry_pct']:5.0f} {r['expectation']:7} "
              f"{r['observations']:3} {sc:>5}  {tail[:60]}")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only. Score 0-3 (higher = more pronounced fat-tail). Expectation is genetic"
          "\n  (breed composition); a gap is an animal owed an observation, never a scored 0."
          "\n  Append-only writer is record_fat_tail_score(). Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
