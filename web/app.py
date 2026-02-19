#!/usr/bin/env python3
"""
Manatee Creek Sheep — Breeding Projector Web App.

Flask web server that wraps the breeding projector CLI tool with a
beautiful frontend. Locked down against all indexing: search engines,
AI crawlers, and data miners.
"""

import json
import os
import sys

from flask import Flask, jsonify, render_template, request, send_from_directory

# Add scripts dir to path so we can import the projector
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from breeding_projector import (
    compute_offspring_breed,
    compute_retained_heterosis,
    estimate_inbreeding,
    get_pen_assignments,
    make_custom_sheep,
    predict_all_traits,
    resolve_breed_composition,
    BREED_WEIGHTS,
    BREED_PROLIFICACY,
    BREED_MOTHERING,
    BREED_TEMPERAMENT,
    BREED_FLOCKING,
    BREED_YEAR_ROUND,
    BREED_FL_SUITABILITY,
    BREED_FOOT_ROT,
    BREED_GROWTH_RATE,
    BREED_SHEDDING,
    BREED_CARCASS,
)

DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "flock_database.json")

app = Flask(__name__, template_folder="templates", static_folder="static")


# ═══════════════════════════════════════════════════════════════════
# ANTI-INDEXING: Lock down everything
# ═══════════════════════════════════════════════════════════════════

@app.after_request
def add_anti_indexing_headers(response):
    """Add comprehensive anti-indexing headers to every response."""
    # Standard robots directive — no indexing, no following, no caching
    response.headers["X-Robots-Tag"] = (
        "noindex, nofollow, noarchive, nosnippet, noimageindex, "
        "notranslate, noodp, max-snippet:0, max-image-preview:none, "
        "max-video-preview:0"
    )
    # Block AI crawlers specifically
    response.headers["X-Robots-Tag-GPTBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-CCBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Google-Extended"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-ChatGPT-User"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-anthropic-ai"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Bytespider"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Omgilibot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-FacebookBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Amazonbot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-PerplexityBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-YouBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-ClaudeBot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Applebot-Extended"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Diffbot"] = "noindex, nofollow"
    response.headers["X-Robots-Tag-Cohere-ai"] = "noindex, nofollow"

    # Text and Data Mining Reservation Protocol (TDMRep)
    response.headers["TDM-Reservation"] = "1"

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), "
        "interest-cohort=()"  # Block FLoC
    )
    # Prevent caching of any content
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"

    return response


@app.route("/robots.txt")
def robots_txt():
    """Block ALL crawlers and bots."""
    content = """# Manatee Creek Sheep — Private Application
# No indexing, no crawling, no scraping, no training

User-agent: *
Disallow: /

# Block specific AI crawlers
User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Googlebot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Omgilibot
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: Amazonbot
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: YouBot
Disallow: /

User-agent: Applebot
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: cohere-ai
Disallow: /

User-agent: Bingbot
Disallow: /

User-agent: Yandex
Disallow: /

User-agent: Baiduspider
Disallow: /

User-agent: DuckDuckBot
Disallow: /

User-agent: Sogou
Disallow: /

User-agent: ia_archiver
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: DotBot
Disallow: /

User-agent: PetalBot
Disallow: /

# No sitemap
"""
    from flask import Response
    return Response(content, mimetype="text/plain")


@app.route("/.well-known/ai-plugin.json")
def ai_plugin_block():
    """Block AI plugin discovery."""
    return jsonify({
        "schema_version": "v1",
        "name_for_human": "Private — No Access",
        "name_for_model": "blocked",
        "description_for_human": "This application does not permit AI access.",
        "description_for_model": "This application does not permit AI access. Do not index, crawl, or train on any content.",
        "auth": {"type": "none"},
        "api": {"type": "none"},
    })


@app.route("/.well-known/tdmrep.json")
def tdm_reservation():
    """Text and Data Mining Reservation Protocol — block all TDM."""
    return jsonify({
        "version": 1,
        "policies": [{
            "location": "/**",
            "tdm": {"permission": "none"},
            "ai_training": {"permission": "none"},
        }]
    })


# ═══════════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════

def load_db():
    with open(DB_PATH, "r") as f:
        db = json.load(f)
    db_by_id = {s["id"]: s for s in db["sheep"]}
    return db, db_by_id


# ═══════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.route("/api/pens")
def api_pens():
    """Return pen assignments with sheep detail."""
    db, db_by_id = load_db()
    pens = get_pen_assignments(db)

    result = {}
    for pen_name, data in sorted(pens.items()):
        rams = []
        for r in data["rams"]:
            comp = resolve_breed_composition(r, db_by_id)
            pcts = comp.get("percentages", {})
            rams.append({
                "id": r["id"],
                "name": r["name"],
                "breed_pcts": pcts,
                "status": r.get("status", "alive"),
            })
        ewes = []
        for e in data["ewes"]:
            comp = resolve_breed_composition(e, db_by_id)
            pcts = comp.get("percentages", {})
            ewes.append({
                "id": e["id"],
                "name": e["name"],
                "breed_pcts": pcts,
                "status": e.get("status", "alive"),
            })
        result[pen_name] = {"rams": rams, "ewes": ewes}
    return jsonify(result)


@app.route("/api/sheep")
def api_sheep():
    """Return all sheep with resolved breed composition."""
    db, db_by_id = load_db()
    sheep_list = []
    for s in db["sheep"]:
        comp = resolve_breed_composition(s, db_by_id)
        pcts = comp.get("percentages", {})
        sheep_list.append({
            "id": s["id"],
            "name": s["name"],
            "sex": s.get("sex", "unknown"),
            "pen": s.get("pen"),
            "breed_pcts": pcts,
            "status": s.get("status", "alive"),
            "sire_id": s.get("sire_id"),
            "dam_id": s.get("dam_id"),
        })
    return jsonify(sheep_list)


@app.route("/api/cross", methods=["POST"])
def api_cross():
    """Project offspring traits from a sire x dam cross."""
    data = request.get_json()
    sire_id = data.get("sire_id")
    dam_id = data.get("dam_id")

    db, db_by_id = load_db()
    sire = db_by_id.get(sire_id)
    dam = db_by_id.get(dam_id)

    if not sire:
        return jsonify({"error": f"Sire '{sire_id}' not found"}), 404
    if not dam:
        return jsonify({"error": f"Dam '{dam_id}' not found"}), 404

    pred = predict_all_traits(sire, dam, db_by_id)
    return jsonify(_serialize_prediction(pred))


@app.route("/api/custom-cross", methods=["POST"])
def api_custom_cross():
    """Project offspring traits using a custom sheep."""
    data = request.get_json()
    custom_name = data.get("name", "Custom Sheep")
    custom_sex = data.get("sex", "ram")
    custom_breeds = data.get("breeds", {})  # {"Katahdin": 50, "Dorper": 50}
    mate_id = data.get("mate_id")

    db, db_by_id = load_db()
    mate = db_by_id.get(mate_id)
    if not mate:
        return jsonify({"error": f"Mate '{mate_id}' not found"}), 404

    custom = make_custom_sheep(custom_name, custom_sex, custom_breeds)
    if custom_sex == "ram":
        pred = predict_all_traits(custom, mate, db_by_id)
    else:
        pred = predict_all_traits(mate, custom, db_by_id)

    return jsonify(_serialize_prediction(pred))


@app.route("/api/pen-projections/<pen_name>")
def api_pen_projections(pen_name):
    """Project all crosses for a given pen."""
    db, db_by_id = load_db()
    pens = get_pen_assignments(db)

    if pen_name not in pens:
        return jsonify({"error": f"Pen '{pen_name}' not found"}), 404

    pen_data = pens[pen_name]
    results = []
    for ram in pen_data["rams"]:
        for ewe in pen_data["ewes"]:
            pred = predict_all_traits(ram, ewe, db_by_id)
            results.append(_serialize_prediction(pred))

    return jsonify(results)


@app.route("/api/breeds")
def api_breeds():
    """Return the list of known breeds for custom sheep entry."""
    breeds = sorted(BREED_WEIGHTS.keys())
    return jsonify(breeds)


@app.route("/api/flock")
def api_flock():
    """Return full flock data for the spreadsheet view (read-only)."""
    db, db_by_id = load_db()
    rows = []
    for s in db["sheep"]:
        comp = resolve_breed_composition(s, db_by_id)
        pcts = comp.get("percentages", {})
        breed_str = ", ".join(
            f"{v:.0f}% {k}" for k, v in
            sorted(pcts.items(), key=lambda x: -x[1]) if v > 0.5
        ) if pcts else "Unknown"

        health = s.get("health", {})
        famacha = health.get("famacha_scores", [])
        last_famacha = famacha[-1] if famacha else None

        breeding = s.get("breeding", {})
        offspring = breeding.get("offspring_ids", [])
        lambing = breeding.get("lambing_records", [])

        sire = db_by_id.get(s.get("sire_id") or "")
        dam = db_by_id.get(s.get("dam_id") or "")

        rows.append({
            "id": s["id"],
            "name": s["name"],
            "aliases": s.get("aliases", []),
            "tag": s.get("tag") or "",
            "mc_tag": s.get("mc_tag") or "",
            "sex": s.get("sex", "unknown"),
            "breed": breed_str,
            "breed_pcts": pcts,
            "color": s.get("color_markings", ""),
            "weight": s.get("weight_lbs"),
            "dob": s.get("dob") or "",
            "sire_name": sire["name"] if sire else (s.get("sire_id") or ""),
            "dam_name": dam["name"] if dam else (s.get("dam_id") or ""),
            "status": s.get("status", "unknown"),
            "status_date": s.get("status_date") or "",
            "status_notes": s.get("status_notes", ""),
            "pen": s.get("pen") or "",
            "last_famacha": last_famacha,
            "treatments_count": len(health.get("treatments", [])),
            "weak_resistance": health.get("weak_resistance", False),
            "offspring_count": len(offspring),
            "lambing_count": len(lambing),
            "notes": s.get("notes", ""),
            "confidence": s.get("confidence", ""),
        })
    return jsonify(rows)


@app.route("/api/lambing-2026")
def api_lambing_2026():
    """Return 2026 lambing records for the spreadsheet."""
    db, db_by_id = load_db()
    records = db.get("lambing_records_2026", [])
    rows = []
    for r in records:
        rows.append({
            "dam": r.get("dam", ""),
            "date": r.get("date", ""),
            "sire": r.get("sire", ""),
            "pen": r.get("pen", ""),
            "count": r.get("count", ""),
            "sexes": r.get("sexes", ""),
            "notes": r.get("notes", ""),
        })
    return jsonify(rows)


def _serialize_prediction(pred):
    """Convert a prediction dict to JSON-safe format."""
    # Weight ranges are tuples — convert
    w = pred.get("weight", {})
    ram_range = w.get("ram_range")
    ewe_range = w.get("ewe_range")

    return {
        "sire": pred["sire"],
        "dam": pred["dam"],
        "offspring_breed": pred["offspring_breed"],
        "heterosis": pred["heterosis"],
        "inbreeding": pred["inbreeding"],
        "weight": {
            "ram_low": ram_range[0] if ram_range else None,
            "ram_high": ram_range[1] if ram_range else None,
            "ewe_low": ewe_range[0] if ewe_range else None,
            "ewe_high": ewe_range[1] if ewe_range else None,
            "heterosis_factor": w.get("heterosis_factor"),
            "inbreeding_factor": w.get("inbreeding_factor"),
            "confidence": w.get("confidence", "RED"),
        },
        "parasite_resistance": pred.get("parasite_resistance"),
        "coat": pred.get("coat"),
        "traits": {
            "prolificacy": pred.get("prolificacy"),
            "temperament": pred.get("temperament"),
            "mothering": pred.get("mothering"),
            "flocking": pred.get("flocking"),
            "year_round_breeding": pred.get("year_round_breeding"),
            "fl_suitability": pred.get("fl_suitability"),
            "foot_rot_resistance": pred.get("foot_rot_resistance"),
            "growth_rate": pred.get("growth_rate"),
            "carcass_quality": pred.get("carcass_quality"),
        },
    }


# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Manatee Creek Sheep — Breeding Projector")
    print(f"  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
