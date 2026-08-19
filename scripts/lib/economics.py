"""Per-animal economics (MCS-13) + marginal sell-weight math (MCS-24). Pure, no I/O.

Soli Deo Gloria.

MCS-13 schema (ADDITIVE; empty today — figures are OWNER facts, asked in the
questionnaire, never reconstructed from memory):
    sheep["economics"] = {
      "acquisition": {"cost": num|0-for-born-here, "date": .., "source": ..},
      "costs":  [{"date":.., "amount":.., "what":.., "source":..}],
      "proceeds":[{"date":.., "amount":.., "what": "auction|private|...", "source":..}]}

MCS-24: the sell-now-or-feed-on question as arithmetic. EVERY input is required —
price, ADG, and feed cost are market/farm facts; a defaulted number here is a
fabricated business recommendation.
"""


def animal_ledger(sheep):
    """(total_cost, total_proceeds, net, complete): complete=False when no economics
    recorded at all — the report says 'no figures recorded', never $0 profit."""
    e = sheep.get("economics")
    if not e:
        return None, None, None, False
    cost = 0.0
    acq = e.get("acquisition") or {}
    if isinstance(acq.get("cost"), (int, float)):
        cost += acq["cost"]
    for c in e.get("costs") or []:
        if isinstance(c.get("amount"), (int, float)):
            cost += c["amount"]
    proceeds = sum(p["amount"] for p in e.get("proceeds") or []
                   if isinstance(p.get("amount"), (int, float)))
    return round(cost, 2), round(proceeds, 2), round(proceeds - cost, 2), True


def validate_economics(db):
    issues = []
    for s in db.get("sheep", []):
        e = s.get("economics")
        if e is None:
            continue
        for section in ("costs", "proceeds"):
            for i, row in enumerate(e.get(section) or []):
                if not isinstance(row.get("amount"), (int, float)):
                    issues.append(f"ERROR [{s['id']}]: economics.{section}[{i}] amount "
                                  f"{row.get('amount')!r} is not a number")
                if not row.get("source"):
                    issues.append(f"ERROR [{s['id']}]: economics.{section}[{i}] has no source")
    return issues


def hold_vs_sell(price_now_per_head, feed_cost_per_day, days,
                 price_later_per_head=None):
    """Marginal economics of holding `days` more, PER HEAD — operator correction
    2026-08-19: "Lambs are not sold by lb weight here." The first version modeled a
    price-per-lb market with a weight slide (the Extension-spreadsheet shape); in a
    per-head market weight only matters through what a buyer offers, which is the
    operator's judgment, not a formula. So the honest calculator is: holding costs
    feed; sell later only if the later per-head offer beats now + feed.

    Returns dict with feed_cost, marginal — POSITIVE marginal favors holding. Price
    later defaults to price now ONLY explicitly (caller passes None -> same price,
    stated in the output), because forecasting a price would be invention."""
    for v in (price_now_per_head, feed_cost_per_day, days):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(f"all inputs must be numbers (got {v!r}) — a defaulted "
                             f"input here is a fabricated business recommendation")
    p_later = price_later_per_head if price_later_per_head is not None else price_now_per_head
    if not isinstance(p_later, (int, float)) or isinstance(p_later, bool):
        raise ValueError(f"price_later_per_head must be a number or None, got {p_later!r}")
    feed = feed_cost_per_day * days
    return {"value_now": round(price_now_per_head, 2),
            "value_later": round(p_later, 2), "feed_cost": round(feed, 2),
            "marginal": round(p_later - feed - price_now_per_head, 2),
            "break_even_price_later": round(price_now_per_head + feed, 2),
            "price_later_assumed_equal": price_later_per_head is None,
            "market": "per-head (operator 2026-08-19: lambs are not sold by lb here)"}
