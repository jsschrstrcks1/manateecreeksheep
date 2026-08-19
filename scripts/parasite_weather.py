#!/usr/bin/env python3
"""Weather-aware parasite-risk signal (MCS-1): warm+wet tightens the recheck cadence.

Soli Deo Gloria.

Barber-pole (Haemonchus) pressure is heat- and moisture-driven; in Florida the honest
FAMACHA-recheck interval is a function of weather, not a flat calendar. This reads the
trailing days from Open-Meteo (no key, free tier) for the FARM'S OWN coordinates and
emits a season signal the advisor/triage already accept (--season warm-wet | normal).

REFUSES without data/farm_location.json ({"latitude": .., "longitude": .., "label": ..})
— running weather for a guessed point is fabricated risk data. Ask the operator once.
Any fetch failure prints UNAVAILABLE and exits 3 — never a silently-defaulted 'normal'
(a false-calm on the one signal that exists to tighten vigilance).

Heuristic (thresholds printed with every verdict, tunable):
  favorable day = mean of daily max/min >= 18 C  AND  trailing-3-day rain >= 2 mm
  warm-wet verdict = >= 7 favorable days in the trailing 14
Grounded in standard Haemonchus larval ecology (development from ~10 C, optimum in
the mid-20s C, moisture required for translation onto pasture); the numbers are a
starting calibration, expected to be tuned against this farm's FAMACHA history.
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).parent.parent
LOC_PATH = REPO / "data" / "farm_location.json"
OUT_PATH = REPO / "data" / "weather_signal.json"

TEMP_C_MIN = 18.0
RAIN_MM_3D = 2.0
FAVORABLE_DAYS_FOR_WARM_WET = 7
TRAILING_DAYS = 14


def main():
    if not LOC_PATH.exists():
        print("REFUSED: data/farm_location.json missing — weather for a guessed point is "
              "fabricated risk data. Create it once: "
              '{"latitude": <lat>, "longitude": <lon>, "label": "Manatee Creek"}')
        return 2
    loc = json.load(open(LOC_PATH))
    lat, lon = loc.get("latitude"), loc.get("longitude")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        print("REFUSED: farm_location.json needs numeric latitude/longitude")
        return 2

    qs = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": TRAILING_DAYS, "forecast_days": 1, "timezone": "auto",
    })
    try:
        with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{qs}",
                                    timeout=20) as r:
            data = json.load(r)
        daily = data["daily"]
        days = list(zip(daily["time"], daily["temperature_2m_max"],
                        daily["temperature_2m_min"], daily["precipitation_sum"]))[:TRAILING_DAYS]
        if len(days) < TRAILING_DAYS or any(x is None for _, a, b, c in days for x in (a, b, c)):
            raise ValueError(f"incomplete daily data ({len(days)} days)")
    except Exception as ex:
        print(f"UNAVAILABLE: weather fetch failed ({ex}) — NO season verdict emitted; "
              f"keep the advisor's own --season judgment. Never read this as 'normal'.")
        return 3

    favorable = []
    for i, (day, tmax, tmin, _rain) in enumerate(days):
        mean_t = (tmax + tmin) / 2
        rain3 = sum(r for _, _, _, r in days[max(0, i - 2):i + 1])
        if mean_t >= TEMP_C_MIN and rain3 >= RAIN_MM_3D:
            favorable.append(day)
    season = "warm-wet" if len(favorable) >= FAVORABLE_DAYS_FOR_WARM_WET else "normal"

    signal = {
        "generated": days[-1][0], "location": loc.get("label") or f"{lat},{lon}",
        "season": season, "favorable_days": len(favorable), "trailing_days": len(days),
        "thresholds": {"mean_temp_c_min": TEMP_C_MIN, "rain_mm_3day": RAIN_MM_3D,
                       "favorable_days_for_warm_wet": FAVORABLE_DAYS_FOR_WARM_WET},
        "basis": "Open-Meteo daily; Haemonchus larval ecology heuristic — tune against "
                 "this farm's FAMACHA history",
    }
    OUT_PATH.write_text(json.dumps(signal, indent=2) + "\n")
    print(f"{signal['location']}: {len(favorable)}/{len(days)} Haemonchus-favorable days "
          f"-> season={season} (thresholds: mean>={TEMP_C_MIN}C + 3d rain>={RAIN_MM_3D}mm; "
          f">= {FAVORABLE_DAYS_FOR_WARM_WET} favorable = warm-wet)")
    print(f"wrote {OUT_PATH} — use with: deworm_advisor.py --season {season} · "
          f"flock_triage.py --season {season}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
