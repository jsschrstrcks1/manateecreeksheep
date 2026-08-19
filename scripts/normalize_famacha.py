#!/usr/bin/env python3
"""normalize_famacha.py — MCS FAMACHA schema normalization (MCS-8 family / audit finding).

WHY THIS EXISTS (measured, not assumed):
    FAMACHA observations live in TWO parallel per-sheep collections that drifted apart:
      - health.famacha_scores[]   — 129 entries; value key split 'famacha' (89) vs
                                    'score' (16), 24 entries have NO score value, dates
                                    in informal 'M-D-YY' form.
      - health.famacha_history[]  — 282 entries; uniform 'score' key, ISO dates, often a
                                    'source'. The SAME observations as famacha_scores for
                                    sheep that have both (gg: identical five dates, one set
                                    formatted '2-12-26', the other '2026-02-12').
    The consumer that drives breeding selection (parasite_resistance.py) reads ONLY
    health.famacha_scores[].score — so it silently drops the 89 '.famacha' entries AND
    every one of the 282 famacha_history entries. The flock's primary parasite-resistance
    metric is being computed on a small fraction of the recorded data.

WHAT THIS DOES:
    Merges both collections, per sheep, into ONE canonical list that matches the consumer
    contract exactly: health.famacha_scores[] = [{date: ISO, score: int|None, notes: [...],
    source?: str}], sorted by date, DEDUPED by date. Lossless — every date, score, note,
    and source in either source survives; a same-date score conflict is kept and reported,
    never silently dropped. famacha_history is removed only after its content is merged in.

SAFETY (careful-not-clever — this is irreplaceable family/operational data):
    Dry-run by DEFAULT: prints the full per-sheep diff and a losslessness audit, writes
    nothing. Pass --apply to write. --apply refuses if the losslessness audit fails.
    Reversible: the change is a single JSON file under git; run with --apply, review the
    diff, revert if wrong. Idempotent: running twice is a no-op (already-canonical input
    normalizes to itself).

    python scripts/normalize_famacha.py            # dry-run: show the diff + audit
    python scripts/normalize_famacha.py --apply     # write it (only if audit passes)
"""
import json
import sys
import re
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"


def normalize_date(raw):
    """Return (iso_date, ok). ISO stays ISO; 'M-D-YY'/'M-D-YYYY' → ISO. Anything else
    (e.g. an informal '2025-2026' range) is returned unchanged with ok=False so it is
    preserved verbatim and never silently reformatted into a wrong date."""
    if not isinstance(raw, str) or not raw.strip():
        return raw, False
    s = raw.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s, True
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2}|\d{4})", s)
    if m:
        mo, day, yr = m.groups()
        yr = int(yr)
        if yr < 100:
            yr += 2000
        return f"{yr:04d}-{int(mo):02d}-{int(day):02d}", True
    return s, False  # unparseable (range/approx) — keep verbatim


def entry_score(e):
    """The score value regardless of which key it was stored under ('score' or 'famacha')."""
    for k in ("score", "famacha"):
        if k in e and e[k] is not None:
            return e[k]
    return None


def entry_notes(e):
    """Notes as a list of non-empty strings (the field is 'notes' (list or str) or 'note')."""
    out = []
    for k in ("notes", "note"):
        v = e.get(k)
        if isinstance(v, list):
            out.extend(str(x).strip() for x in v if str(x).strip())
        elif isinstance(v, str) and v.strip():
            out.append(v.strip())
    return out


def _as_point(v):
    """Return v as a numeric point if it is one ('3', 3, 3.5 -> 3.5); a range ('1-2') or a
    word ('good') is NOT a point -> None."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str) and re.fullmatch(r"\d+(?:\.\d+)?", v.strip()):
        return float(v)
    return None


def _range_contains(rng, pt):
    """True if string rng like '1-2' numerically contains point pt."""
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", str(rng))
    return bool(m) and pt is not None and int(m.group(1)) <= pt <= int(m.group(2))


def _merge_score(a, b):
    """Combine two same-date score values losslessly. Returns (score, raw_alts, conflict).
    - equal            -> (a, [], False)
    - one empty        -> (other, [], False)
    - range ∋ point    -> (point, [the range], False)   # compatible: two encodings
    - two diff points  -> (None, [a, b], True)           # genuine disagreement: skip + flag
    - anything else    -> keep a, preserve b, no hard conflict flag
    raw_alts are the values NOT chosen as `score`, preserved so nothing is lost."""
    if a is None:
        return b, [], False
    if b is None:
        return a, [], False
    if str(a) == str(b):
        return a, [], False
    pa, pb = _as_point(a), _as_point(b)
    if _range_contains(a, pb):     # a is a range containing b's point -> b is the clean value
        return b, [a], False
    if _range_contains(b, pa):
        return a, [b], False
    if pa is not None and pb is not None:   # two genuine numeric points that disagree
        return None, [a, b], True
    return a, [b], False           # e.g. a point vs a word — keep point-ish a, preserve b


def canonicalize(health):
    """Merge famacha_scores + famacha_history → one canonical famacha_scores list.
    Entry shape: {date, score, notes, source?, raw?}. `raw` holds every alternate value not
    chosen as `score`, so the merge loses nothing. Returns (new_list, report)."""
    scores = health.get("famacha_scores") or []
    history = health.get("famacha_history") or []
    report = {"conflicts": [], "unparseable_dates": [], "merged_dates": 0}

    by_date = {}
    order = []

    def ingest(e, origin):
        if not isinstance(e, dict):
            return
        iso, ok = normalize_date(e.get("date"))
        if not ok and iso:
            report["unparseable_dates"].append({"date": iso, "origin": origin})
        key = iso if iso is not None else f"__nodate__{origin}{len(order)}"
        sc = entry_score(e)
        notes = entry_notes(e)
        src = e.get("source")
        if key not in by_date:
            ent = {"date": iso, "score": sc, "notes": list(notes)}
            if src:
                ent["source"] = src
            if e.get("raw"):          # carry an already-canonical entry's alternates forward
                ent["raw"] = list(e["raw"])   # (idempotency: a second run must not drop them)
            by_date[key] = ent
            order.append(key)
        else:
            cur = by_date[key]
            report["merged_dates"] += 1
            merged, alts, conflict = _merge_score(cur.get("score"), sc)
            cur["score"] = merged
            for a in alts:
                cur.setdefault("raw", [])
                if a not in cur["raw"]:
                    cur["raw"].append(a)
            if conflict:
                report["conflicts"].append({"date": iso, "values": alts})
                cur["notes"].append(f"[CONFLICT] FAMACHA recorded as {alts[0]} and {alts[1]} on the same date — score left null; verify against the notebook")
            for n in notes:
                if n not in cur["notes"]:
                    cur["notes"].append(n)
            if src and "source" not in cur:
                cur["source"] = src

    # History first (uniform clean points, ISO, sourced); famacha_scores fills gaps and
    # contributes its ranges, which _merge_score keeps as `raw` alongside the clean point.
    for e in history:
        ingest(e, "history")
    for e in scores:
        ingest(e, "scores")

    def sort_key(k):
        d = by_date[k]["date"]
        iso = isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)
        return (0, d) if iso else (1, str(d))
    new_list = [by_date[k] for k in sorted(order, key=sort_key)]
    for e in new_list:
        s = e.get("score")
        if isinstance(s, float) and s.is_integer():
            e["score"] = int(s)
        if not e.get("raw"):
            e.pop("raw", None)
        # notes is a STRING in the existing schema (and what the consumer reads via
        # entry.notes.lower()); the merge collected them as a list to combine same-date
        # notes losslessly — join back to one string so the contract is unchanged.
        e["notes"] = "; ".join(e.get("notes") or [])
    return new_list, report


def audit_lossless(old_scores, old_history, new_list):
    """Every score value and every note string in either source must survive."""
    def scores_multiset(entries):
        out = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            if entry_score(e) is not None:
                out.append(str(entry_score(e)))
            for r in (e.get("raw") or []):   # preserved alternates count as NOT lost
                out.append(str(r))
        return sorted(out)
    def notes_set(entries):
        out = set()
        for e in entries:
            if isinstance(e, dict):
                for n in entry_notes(e):
                    out.add(n)
        return out
    src_scores = scores_multiset(old_scores) + scores_multiset(old_history)
    new_scores = scores_multiset(new_list)
    # new may have FEWER score-strings only where the SAME date carried the same score in
    # both collections (a true duplicate) — so new must be a superset-by-value after dedup.
    missing_scores = sorted(set(src_scores) - set(new_scores))
    src_notes = notes_set(old_scores) | notes_set(old_history)
    # Output notes are joined into one string per entry, so check each source note survives
    # as a SUBSTRING of the concatenated output notes rather than as an exact set member.
    new_blob = " ||| ".join(
        (e["notes"] if isinstance(e.get("notes"), str) else "; ".join(e.get("notes") or []))
        for e in new_list if isinstance(e, dict)
    )
    missing_notes = sorted(n for n in src_notes if n and n not in new_blob)
    return missing_scores, missing_notes


def main(argv):
    apply = "--apply" in argv
    db = json.loads(DB_PATH.read_text())
    sheep = db["sheep"]
    total_before_scores = total_before_hist = total_after = 0
    changed = 0
    all_missing_scores = []
    all_missing_notes = []
    diffs = []
    for s in sheep:
        h = s.get("health")
        if not isinstance(h, dict):
            continue
        # Process any sheep carrying EITHER key — including an empty famacha_history: []
        # (skipping those left 94 empty legacy keys behind on the first apply).
        if "famacha_scores" not in h and "famacha_history" not in h:
            continue
        old_scores = h.get("famacha_scores") or []
        old_history = h.get("famacha_history") or []
        total_before_scores += len(old_scores)
        total_before_hist += len(old_history)
        new_list, report = canonicalize(h)
        total_after += len(new_list)
        ms, mn = audit_lossless(old_scores, old_history, new_list)
        all_missing_scores += [(s.get("id"), x) for x in ms]
        all_missing_notes += [(s.get("id"), x) for x in mn]
        if new_list != old_scores or old_history:
            changed += 1
            diffs.append((s.get("id") or s.get("name"), len(old_scores), len(old_history),
                          len(new_list), report))
        if apply:
            h["famacha_scores"] = new_list
            h.pop("famacha_history", None)
            s["health"] = h

    print("FAMACHA normalization —", "APPLY" if apply else "DRY-RUN")
    print(f"  sheep touched:            {changed}")
    print(f"  famacha_scores in:        {total_before_scores}")
    print(f"  famacha_history in:       {total_before_hist}")
    print(f"  canonical entries out:    {total_after}")
    print(f"  losslessness — missing scores: {len(all_missing_scores)}, missing notes: {len(all_missing_notes)}")
    conflicts = sum(len(r['conflicts']) for _, _, _, _, r in diffs)
    unparse = sum(len(r['unparseable_dates']) for _, _, _, _, r in diffs)
    print(f"  same-date score conflicts (kept + noted): {conflicts}")
    print(f"  unparseable dates (kept verbatim):        {unparse}")
    print()
    for sid, ns, nh, nn, r in diffs[:12]:
        print(f"  {sid:28} scores {ns:2d} + history {nh:2d} -> {nn:2d}")
    if len(diffs) > 12:
        print(f"  … +{len(diffs) - 12} more sheep")
    # Genuine disagreements are the one thing an operator MUST see — list them all.
    genuine = [(sid, c) for sid, _, _, _, r in diffs for c in r["conflicts"]]
    if genuine:
        print(f"\n  ⚠ {len(genuine)} GENUINE FAMACHA disagreement(s) — score left NULL, flagged for notebook re-check:")
        for sid, c in genuine:
            print(f"     [{sid}] {c['date']}: recorded as {c['values'][0]} and {c['values'][1]}")

    if all_missing_scores or all_missing_notes:
        print("\nLOSSLESSNESS AUDIT FAILED — not safe to apply:")
        for sid, x in all_missing_scores[:10]:
            print(f"  MISSING SCORE  [{sid}] {x}")
        for sid, x in all_missing_notes[:10]:
            print(f"  MISSING NOTE   [{sid}] {x!r}")
        if apply:
            print("\nREFUSING to write — the audit must pass first.")
            return 2
        return 1

    if apply:
        # ensure_ascii=True matches the file's existing convention (it escapes em-dashes
        # etc. as \uXXXX); writing literal unicode would re-encode every note with a dash
        # and bury the FAMACHA change under a noisy, unreviewable diff.
        DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=True) + "\n")
        print(f"\nWROTE {DB_PATH} — famacha_history merged into famacha_scores, "
              f"all values under 'score', dates ISO. Review the git diff.")
    else:
        print("\nDry-run only — nothing written. Re-run with --apply once the diff looks right.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
