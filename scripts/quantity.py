#!/usr/bin/env python3
"""quantity.py — one quantity shape for every measurement (MCS-12).

Weights, doses, feed amounts, egg counts, girth/length all live in this flock as free text —
"Nuflor 4.5mL", "108.2 lbs", "Iron 0.25mL", "400 epg". Each consumer re-parses in its own way.
This is the single shape they should share:

    {value, unit, measure, label, canonical_value, canonical_unit}

  - value/unit: as written ("4.5", "mL")
  - measure: the physical dimension ("volume", "mass", "length", "temperature", "egg_count", "count")
  - label: optional human tag ("dose", "body weight")
  - canonical_value/unit: value converted to the measure's canonical unit (mL, kg, cm, ...), so two
    quantities in the same measure compare directly. Temperature is affine (°F/°C), so it is PARSED
    but not force-converted here — canonical_* mirror the input and the caller converts intentionally.

Pure, dependency-free, and lossless (the original value/unit are always retained). This module
authors no measurement data; it only gives one shape and honest unit math.

    python3 scripts/quantity.py --parse "Nuflor 4.5mL"     # parse one quantity
    python3 scripts/quantity.py --doses                     # extract structured doses from treatments
    python3 scripts/quantity.py --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# unit -> (measure, canonical_unit, factor_to_canonical). Canonical per measure: volume=mL,
# mass=kg, length=cm, temperature=self (affine), egg_count=epg, count=count.
UNITS = {
    "ml": ("volume", "mL", 1.0), "cc": ("volume", "mL", 1.0),
    "l": ("volume", "mL", 1000.0), "liter": ("volume", "mL", 1000.0), "litre": ("volume", "mL", 1000.0),
    "kg": ("mass", "kg", 1.0), "g": ("mass", "kg", 0.001), "gram": ("mass", "kg", 0.001),
    "lb": ("mass", "kg", 0.45359237), "lbs": ("mass", "kg", 0.45359237), "pound": ("mass", "kg", 0.45359237),
    "oz": ("mass", "kg", 0.0283495),
    "cm": ("length", "cm", 1.0), "mm": ("length", "cm", 0.1), "m": ("length", "cm", 100.0),
    "in": ("length", "cm", 2.54), "inch": ("length", "cm", 2.54), "inches": ("length", "cm", 2.54),
    "f": ("temperature", "F", 1.0), "c": ("temperature", "C", 1.0),
    "epg": ("egg_count", "epg", 1.0),
}
# canonical unit per measure, for callers that want it without a sample unit
CANONICAL = {"volume": "mL", "mass": "kg", "length": "cm", "temperature": "F", "egg_count": "epg", "count": "count"}

# a number then an optional unit token (mL, lbs, °F, epg, cc). Degree sign optional on temps.
# The number alternation MUST accept a leading-decimal form (".5", "-.25") — the flock records
# doses that way (e.g. "Iron .5mL"), and requiring an integer part parsed ".5mL" as 5mL, a 10x
# dose error in the one module whose job is honest unit math.
_Q = re.compile(r"(-?(?:\d+(?:\.\d+)?|\.\d+))\s*°?\s*([a-zA-Z]+)?")


def make_quantity(value, unit=None, label=None):
    """Build the canonical quantity shape from a numeric value + optional unit. Unknown unit ->
    measure 'count', unit preserved verbatim, canonical_* mirror the input (lossless)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    u = (unit or "").strip()
    key = u.lower().lstrip("°")
    if key in UNITS:
        measure, canon_unit, factor = UNITS[key]
        if measure == "temperature":
            canon_value, canon_unit = v, (u.upper().lstrip("°") or canon_unit)
        else:
            canon_value = v * factor
    else:
        measure, canon_unit, canon_value = ("count" if not u else "count"), (u or "count"), v
    return {"value": v, "unit": u or None, "measure": measure, "label": label,
            "canonical_value": round(canon_value, 6), "canonical_unit": canon_unit}


def parse_quantity(text, label=None):
    """Parse the FIRST quantity in a string. None if no number present."""
    m = _Q.search(str(text or ""))
    if not m:
        return None
    return make_quantity(m.group(1), m.group(2), label)


def extract_quantities(text, label=None):
    """Every quantity in a string (a combo like 'Nuflor 4.5mL 105.2°F' yields two)."""
    out = []
    for m in _Q.finditer(str(text or "")):
        q = make_quantity(m.group(1), m.group(2), label)
        # a bare number with no unit and no decimal is often a tag/id, not a measurement; keep it
        # only when it carried a unit — avoids turning "Pen 2" or a tag number into a quantity.
        if q and q["unit"]:
            out.append(q)
    return out


def to_unit(qty, target_unit):
    """Convert a quantity to another unit IN THE SAME MEASURE. Returns a new value (float) or None
    if the target unit is unknown or a different measure. Temperature is affine and handled here."""
    if not qty:
        return None
    tkey = str(target_unit).lower().lstrip("°")
    if tkey not in UNITS:
        return None
    tmeasure, _, tfactor = UNITS[tkey]
    if tmeasure != qty["measure"]:
        return None
    if tmeasure == "temperature":
        # convert input to Celsius base then to target
        src = (qty["unit"] or "F").upper().lstrip("°")
        c = (qty["value"] - 32) * 5 / 9 if src == "F" else qty["value"]
        return round(c * 9 / 5 + 32, 4) if tkey == "f" else round(c, 4)
    # canonical_value is in the measure's canonical unit; convert canonical -> target
    return round(qty["canonical_value"] / tfactor, 6)


def _dose_label(treatment_str):
    return "dose"


def extract_doses(db):
    """Structured doses pulled from treatment free text — the immediate, real-data use of the
    quantity shape. Read-only; each carries the source string."""
    out = []
    for s in db.get("sheep", []):
        for t in (s.get("health", {}).get("treatments") or []):
            if not isinstance(t, dict):
                continue
            qs = [q for q in extract_quantities(t.get("treatment"), label="dose")
                  if q["measure"] in ("volume", "mass")]
            for q in qs:
                out.append({"sheep_id": s["id"], "date": t.get("date"), "source": t.get("treatment"),
                            "quantity": q})
    return out


def main():
    ap = argparse.ArgumentParser(description="Quantity shape (MCS-12): parse/convert/extract")
    ap.add_argument("--parse", metavar="TEXT", default=None)
    ap.add_argument("--doses", action="store_true", help="extract structured doses from treatments")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.parse is not None:
        q = parse_quantity(args.parse, label="parsed")
        if args.json:
            print(json.dumps(q, indent=2)); return 0
        if q is None:
            print("no quantity found"); return 1
        print(f"  value={q['value']:g} unit={q['unit']} measure={q['measure']} "
              f"canonical={q['canonical_value']:g}{q['canonical_unit']}")
        return 0

    if args.doses:
        db = json.loads(DB_PATH.read_text())
        doses = extract_doses(db)
        if args.json:
            print(json.dumps(doses, indent=2)); return 0
        print(f"Structured doses extracted from treatment free text — {len(doses)}\n")
        for d in doses:
            q = d["quantity"]
            print(f"  {d['sheep_id']:24} {str(d['date'] or '—'):12} {q['value']:6g}{q['unit'] or '':4} "
                  f"({q['measure']}, ={q['canonical_value']:g}{q['canonical_unit']})  {d['source'][:40]!r}")
        print("\n  Read-only. One shape {value,unit,measure,label,canonical_*}; lossless (original kept).")
        return 0

    print("usage: --parse TEXT | --doses  (see --help)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
