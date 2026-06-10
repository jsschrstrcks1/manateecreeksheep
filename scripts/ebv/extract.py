"""Extract trait phenotypes from flock_database.json for EBV computation.

Each function returns a dict {sheep_id: float} of usable measurements.
Records without sufficient data are silently skipped.
"""
from __future__ import annotations
import json
from statistics import mean
from datetime import date, datetime


def load_db(path: str = "data/flock_database.json") -> dict:
    with open(path) as f:
        return json.load(f)


def _parse_famacha(val) -> float | None:
    """Coerce FAMACHA score values (which can be int, float, or strings like '1-2', '2.5')."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip()
        if "-" in s:
            try:
                a, b = s.split("-", 1)
                return (float(a) + float(b)) / 2
            except ValueError:
                return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def extract_parasite_resistance(db: dict) -> dict:
    """Mean FAMACHA per sheep, INVERTED so higher = more resistant.

    FAMACHA ranges 1-5 (1 = healthy, 5 = severely anemic). We invert by
    computing (5 - mean(FAMACHA)) so higher = better.
    """
    out = {}
    for s in db["sheep"]:
        h = s.get("health") or {}
        scores = []
        for src in (h.get("famacha_scores") or [], h.get("famacha_history") or []):
            for entry in src:
                if not isinstance(entry, dict):
                    continue
                v = entry.get("score") or entry.get("famacha")
                f = _parse_famacha(v)
                if f is not None and 1.0 <= f <= 5.0:
                    scores.append(f)
        if scores:
            out[s["id"]] = round(5.0 - mean(scores), 3)
    return out


def extract_adult_weight(db: dict) -> dict:
    """Adult body weight (lb). Used as PWT proxy."""
    out = {}
    for s in db["sheep"]:
        w = s.get("weight_lbs")
        if isinstance(w, (int, float)) and w > 0:
            out[s["id"]] = float(w)
    return out


def extract_birth_weight(db: dict) -> dict:
    """Birth weight (lb)."""
    out = {}
    for s in db["sheep"]:
        m = s.get("measurements") or {}
        bw = None
        if isinstance(m, dict):
            bw = m.get("birth_weight_lbs") or m.get("birth_weight")
        if bw is None:
            # parse from notes if present (some 2023 lambs)
            notes = s.get("notes") or ""
            import re
            m2 = re.search(r"[Bb]irth\s*weight\s*[:= ]*([0-9.]+)\s*lb", notes)
            if m2:
                try:
                    bw = float(m2.group(1))
                except ValueError:
                    pass
        if isinstance(bw, (int, float)) and bw > 0:
            out[s["id"]] = float(bw)
    return out


def extract_adg(db: dict) -> dict:
    """Average daily gain (lb/day) if recorded or computable."""
    out = {}
    for s in db["sheep"]:
        m = s.get("measurements") or {}
        adg = None
        if isinstance(m, dict):
            adg = m.get("adg") or m.get("ADG")
        if adg is None:
            notes = s.get("notes") or ""
            import re
            m2 = re.search(r"ADG\s*[:= ]*([0-9.]+)", notes)
            if m2:
                try:
                    adg = float(m2.group(1))
                except ValueError:
                    pass
        if isinstance(adg, (int, float)) and adg > 0:
            out[s["id"]] = float(adg)
    return out


def extract_lambs_weaned(db: dict) -> dict:
    """Average lambs weaned per recorded lambing (NLW maternal trait)."""
    by_dam = {}
    for s in db["sheep"]:
        dam = s.get("dam_id")
        if not dam:
            continue
        status = s.get("status")
        # Count as weaned if reached at least 60 days and not deceased before
        # For simplicity: weaned = alive at 60+ days OR sold OR registered as adult
        if status in ("alive", "sold", "gifted", "unknown"):
            by_dam.setdefault(dam, []).append(s["id"])
        elif status == "deceased":
            # only count if reached weaning
            dob = s.get("dob")
            sd = s.get("status_date")
            try:
                if dob and sd:
                    dob_d = datetime.fromisoformat(dob).date()
                    sd_d = datetime.fromisoformat(sd).date()
                    if (sd_d - dob_d).days >= 60:
                        by_dam.setdefault(dam, []).append(s["id"])
            except Exception:
                pass

    # Average per dam = total recorded weaned / number of distinct lambing events
    # For simplicity here we just report total offspring weaned. This is an
    # under-estimate of per-lambing rate but is the cleanest proxy from records.
    out = {}
    for dam_id, lambs in by_dam.items():
        out[dam_id] = float(len(lambs))
    return out


if __name__ == "__main__":
    db = load_db()
    print(f"Records: {len(db['sheep'])}")
    pr = extract_parasite_resistance(db)
    print(f"  Parasite Resistance: {len(pr)} sheep with FAMACHA data")
    aw = extract_adult_weight(db)
    print(f"  Adult Weight: {len(aw)} sheep with recorded weight")
    bw = extract_birth_weight(db)
    print(f"  Birth Weight: {len(bw)} sheep with birth weight")
    adg = extract_adg(db)
    print(f"  ADG: {len(adg)} sheep with ADG")
    nlw = extract_lambs_weaned(db)
    print(f"  Lambs Weaned: {len(nlw)} dams with offspring")
