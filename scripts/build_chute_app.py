#!/usr/bin/env python3
"""Build the offline chute app: bake the live roster + triage order into the template.

Soli Deo Gloria.

app/chute_template.html + flock_database.json (+ health_events.jsonl) -> app/chute.html,
a single self-contained file for the phone: no server, no network, no third-party code.
Regenerate whenever the DB changes; the app header shows its data build date so a stale
copy is visible, never silent (no-false-green).

Slice 1 of the flock PWA (MCS-34). When Atlas /flock exists (plan Phase 2/5), this same
UI gains a sync path; until then Export emits validated work_flock.py lines.
"""
import datetime
import importlib.util
import json
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, _here / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


da = _load("da", "deworm_advisor.py")
ft = _load("ft", "flock_triage.py")

REPO = _here.parent
DB = REPO / "data" / "flock_database.json"
EVENTS = REPO / "data" / "health_events.jsonl"
TEMPLATE = REPO / "app" / "chute_template.html"
OUT = REPO / "app" / "chute.html"


def build_roster():
    db = json.load(open(DB))
    sheep = db.get("sheep", [])
    events = []
    if EVENTS.exists():
        events = [json.loads(l) for l in EVENTS.read_text().splitlines() if l.strip()]
    unparseable = [0]
    fam, fec = da.latest_signals(sheep, events, unparseable)

    today = datetime.date.today()
    roster = []
    for s in sheep:
        if s.get("status") != "alive":
            continue
        aid = s["id"]
        score, s_date = fam.get(aid, (None, None))
        epg, _ = fec.get(aid, (None, None))
        series = ft.famacha_series(s, events, aid)
        trend_worse = len(series) >= 2 and series[-1][1] > series[-2][1]
        days_since = (today - s_date).days if s_date else None
        rank, _parts = ft.score_animal(
            score=score, s_date=s_date, epg=epg, trend_worse=trend_worse,
            days_since=days_since, cohort_loss_14d=False, pen_missing=not s.get("pen"),
            today=today, fec_high=1000, stale_days=14)
        roster.append({
            "id": aid,
            "name": s.get("name") or aid,
            "tag": s.get("tag") or "",
            "pen": s.get("pen") or "",
            "score": score,
            "score_date": str(s_date) if s_date else "",
            "rank": rank,
        })
    roster.sort(key=lambda a: (-a["rank"], a["id"]))
    return roster


def main():
    roster = build_roster()
    t = TEMPLATE.read_text()
    marker_a = "/*__FLOCK_DATA__*/[]/*__END__*/"
    marker_b = '/*__BUILT__*/""/*__END2__*/'
    assert marker_a in t and marker_b in t, "template markers missing"
    t = t.replace(marker_a, json.dumps(roster, separators=(",", ":")))
    t = t.replace(marker_b, json.dumps(datetime.date.today().isoformat()))
    OUT.write_text(t)
    print(f"wrote {OUT} — {len(roster)} living animals baked in "
          f"({sum(1 for a in roster if a['score'])} with a FAMACHA on record)")


if __name__ == "__main__":
    main()
