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
    """Composite parasite-resistance phenotype, higher = more resistant.

    Combines two data sources, in priority order:

    1. FEC (fecal egg count) from any source — direct measurement.
       Lower FEC = better. We convert to inverted-log scale:
           PR_from_fec = -log10(max(1, mean_FEC))
       so 0 FEC ~ 0 (neutral), 100 -> -2, 1000 -> -3, etc., and we
       negate again so higher = better: PR_from_fec = 5 - log10.

    2. FAMACHA scores (1-5 scale, 1 = healthy). Inverted:
           PR_from_famacha = (5 - mean(FAMACHA))

    When both are present we average them (with weighting toward FEC,
    which is the more sensitive measurement).
    """
    import math

    out = {}
    for s in db["sheep"]:
        h = s.get("health") or {}
        # FAMACHA
        famacha_scores = []
        for src in (h.get("famacha_scores") or [], h.get("famacha_history") or []):
            for entry in src:
                if not isinstance(entry, dict):
                    continue
                v = entry.get("score") or entry.get("famacha")
                f = _parse_famacha(v)
                if f is not None and 1.0 <= f <= 5.0:
                    famacha_scores.append(f)
        # FEC
        fec_values = []
        for src in (h.get("fec_history") or [],):
            for entry in src:
                if not isinstance(entry, dict):
                    continue
                v = entry.get("fec") or entry.get("FEC")
                if isinstance(v, (int, float)) and v >= 0:
                    fec_values.append(float(v))
        # Also pull UF Ram Test direct values
        urt = s.get("uf_ram_test")
        if urt and isinstance(urt, dict):
            avg = urt.get("fec_average")
            if isinstance(avg, (int, float)):
                fec_values.append(float(avg))
            for r in urt.get("fec_readings", []):
                if isinstance(r, dict) and isinstance(r.get("fec"), (int, float)):
                    fec_values.append(float(r["fec"]))

        # Compute components
        components = []
        if fec_values:
            mean_fec = mean(fec_values)
            # Higher = better, with log10 scaling. 0 FEC -> 5 (excellent), 200 -> ~2.7, 1000 -> ~2.0
            pr_fec = 5.0 - math.log10(max(1.0, mean_fec))
            components.append(("FEC", pr_fec, 2.0))  # double-weighted
        if famacha_scores:
            pr_fam = 5.0 - mean(famacha_scores)
            components.append(("FAMACHA", pr_fam, 1.0))

        # UF Ram Test Tx=0 bonus: under standardized parasite-challenge
        # conditions, going through without treatment is far more
        # diagnostic than any single FAMACHA check. Add +1.0 if Tx=0
        # over a UF Ram Test run.
        urt_bonus = 0.0
        if urt and isinstance(urt, dict):
            tx = urt.get("treatments")
            if isinstance(tx, int) and tx == 0:
                urt_bonus = 1.0

        if components:
            weighted_sum = sum(v * w for _, v, w in components)
            total_w = sum(w for _, _, w in components)
            out[s["id"]] = round(weighted_sum / total_w + urt_bonus, 3)
    return out


def extract_mature_weight(db: dict) -> dict:
    """Adult/mature body weight (lb) — the SIZE axis (trait MWT).

    Separated from PWT 2026-06-12: adult weight measures frame/size, not
    growth rate. Feeding it into post-weaning weight made old heavy ewes
    rank as fast growers. Now it has its own trait.
    """
    out = {}
    for s in db["sheep"]:
        w = s.get("weight_lbs")
        if isinstance(w, (int, float)) and w > 0:
            out[s["id"]] = float(w)
    return out


def extract_post_weaning_weight(db: dict) -> dict:
    """TRUE post-weaning weight (lb), trait PWT.

    Only uses weights recorded at/near the post-weaning stage — explicit
    measurement fields. Adult weight_lbs is NOT used here (that's MWT).
    Most flock animals have no true PWWT, so they fall to no-data — which
    is honest; we don't weigh lambs at 120 days on-farm. NSIP-anchored
    animals still get true PWWT EBVs via the anchor file.
    """
    out = {}
    for s in db["sheep"]:
        m = s.get("measurements") or {}
        if not isinstance(m, dict):
            continue
        pwwt = (m.get("post_weaning_weight_lb") or m.get("pwwt_lb")
                or m.get("weight_120d_lb"))
        if isinstance(pwwt, (int, float)) and pwwt > 0:
            out[s["id"]] = float(pwwt)
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
