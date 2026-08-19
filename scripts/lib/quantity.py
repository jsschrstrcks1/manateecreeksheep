"""One quantity shape for every measurement (MCS-12). Pure functions, no I/O.

Soli Deo Gloria.

farmOS concept (shape only, no code): a measurement is always
    {"measure": <what kind>, "value": <number>, "unit": <unit>, "label": <optional text>}
so weight, FAMACHA, FEC, BCS, and temperature all fit ONE structure — new measurements
need no schema change, and trends/alerts are written once against "quantities of measure
X" instead of per-field. Supports MCS-3 (composite reads several quantities) and MCS-8
(FAMACHA+FEC as two quantities on one pass).

Discipline: a quantity is DATA about one observation; it never carries interpretation
(no 'anemic', no 'underweight' — thresholds live in the consumers, tunable).
"""

# measure -> allowed units (first = canonical). Extend by ADDING a row — never retype
# an existing measure's data.
MEASURES = {
    "weight": ("lbs", "kg"),
    "famacha": ("score",),          # 1-5, FAMACHA card
    "fec": ("epg",),                # eggs per gram
    "bcs": ("score",),              # body condition 1-5
    "temperature": ("F", "C"),
    "count": ("head",),
    "milk": ("oz", "ml"),           # MCS-21 per-ewe milk records
    "coat_shed": ("score",),        # MCS-19: seasonal shed score 1-5, each summer
    "fat_tail": ("score",),         # MCS-20: fat-tail phenotype score 1-5
}


def make_quantity(measure, value, unit=None, label=None):
    """Build a valid quantity or raise ValueError. Unit defaults to the measure's canonical."""
    if measure not in MEASURES:
        raise ValueError(f"unknown measure '{measure}' — add it to MEASURES deliberately, "
                         f"never inline (known: {sorted(MEASURES)})")
    unit = unit or MEASURES[measure][0]
    if unit not in MEASURES[measure]:
        raise ValueError(f"unit '{unit}' not valid for measure '{measure}' "
                         f"(valid: {MEASURES[measure]})")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"quantity value must be a number, got {value!r}")
    if measure in ("famacha", "bcs", "coat_shed", "fat_tail") and value not in (1, 2, 3, 4, 5):
        raise ValueError(f"{measure} score must be 1-5, got {value!r}")
    if measure in ("fec", "weight", "milk", "count") and value < 0:
        raise ValueError(f"{measure} cannot be negative, got {value!r}")
    q = {"measure": measure, "value": value, "unit": unit}
    if label:
        q["label"] = label
    return q


def validate_quantity(q):
    """Return list of problems (empty = valid). Never raises — validator-friendly."""
    probs = []
    if not isinstance(q, dict):
        return [f"quantity is not an object: {q!r}"]
    try:
        make_quantity(q.get("measure"), q.get("value"), q.get("unit"), q.get("label"))
    except ValueError as ex:
        probs.append(str(ex))
    extra = set(q) - {"measure", "value", "unit", "label"}
    if extra:
        probs.append(f"unknown quantity keys: {sorted(extra)}")
    return probs


def event_quantities(event):
    """Every quantity an event carries — the explicit `quantity` field plus the legacy
    per-field encodings (score on famacha events, fec_epg anywhere), normalized to the
    one shape so consumers never dual-read."""
    out = []
    if isinstance(event.get("quantity"), dict):
        out.append(event["quantity"])
    if event.get("type") == "famacha" and isinstance(event.get("score"), (int, float)) \
            and not any(q["measure"] == "famacha" for q in out):
        out.append({"measure": "famacha", "value": event["score"], "unit": "score"})
    if isinstance(event.get("fec_epg"), (int, float)) \
            and not any(q["measure"] == "fec" for q in out):
        out.append({"measure": "fec", "value": event["fec_epg"], "unit": "epg"})
    return out


def quantity_series(events, animal_id, measure):
    """[(date_str, value)] for one animal and measure, in log order — the write-once
    trend feed (weights over time, FEC curve, FAMACHA history) every chart/alert reads."""
    series = []
    for e in events:
        if e.get("animal_id") != animal_id:
            continue
        for q in event_quantities(e):
            if q["measure"] == measure:
                series.append((e.get("date"), q["value"]))
    return series
