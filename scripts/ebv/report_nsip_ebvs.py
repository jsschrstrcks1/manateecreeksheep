#!/usr/bin/env python3
"""Report on NSIP EBVs captured for the flock.

Walks the data/ebv/ebvs_scraped/*.json files and produces a summary
markdown report grouped by trait, highlighting:
  - Animals with the strongest parasite resistance (lowest WFEC / PFEC)
  - Animals with the strongest growth (PWWT, YWT)
  - US Hair composite index leaders

Usage:
    python3 scripts/ebv/report_nsip_ebvs.py
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict


SCRAPED = Path("data/ebv/ebvs_scraped")
PEDIGREE = Path("data/ebv/khsi_pedigree_dump.json")
OUT = Path("data/ebv/nsip_summary.md")


def main():
    if not SCRAPED.exists():
        print("No scraped EBVs found.")
        return

    ped = {}
    if PEDIGREE.exists():
        ped = json.loads(PEDIGREE.read_text()).get("records", {})

    rows = []
    for fp in sorted(SCRAPED.glob("*.json")):
        d = json.loads(fp.read_text())
        if d.get("error"):
            continue
        reg = d["reg"]
        subj = next((b for b in d.get("blocks", []) if b.get("role") == "subject"), None)
        if not subj:
            continue
        ident = ped.get(reg, {})
        rows.append({
            "reg": reg,
            "name": ident.get("name") or "—",
            "flock": ident.get("flock_name_number") or "—",
            "sex": ident.get("sex") or "—",
            "prog": subj.get("progeny_evaluated"),
            "flocks": subj.get("flocks_represented"),
            "wfec": subj.get("parasite_resistance", {}).get("WFEC", {}).get("val"),
            "wfec_rank": subj.get("parasite_resistance", {}).get("WFEC", {}).get("rank"),
            "pfec": subj.get("parasite_resistance", {}).get("PFEC", {}).get("val"),
            "pwwt": subj.get("weight_traits", {}).get("PWWT", {}).get("val"),
            "ywt": subj.get("weight_traits", {}).get("YWT", {}).get("val"),
            "us_hair": (subj.get("us_hair_composite_index") or {}).get("val"),
            "us_hair_rank": (subj.get("us_hair_composite_index") or {}).get("rank"),
        })

    md = [f"# NSIP EBVs Captured ({len(rows)} animals)\n\n"]
    md.append(f"Scraped from digitalovine.com on 2026-06-11. Snapshot date typically 2025-09-22.\n\n")

    def rank_table(title, rows, sort_key, asc=True, top_n=15, formatter=None):
        md.append(f"## {title}\n\n")
        valid = [r for r in rows if r.get(sort_key) is not None]
        valid.sort(key=lambda r: r[sort_key], reverse=not asc)
        md.append("| Rank | Reg | Name | Flock | Sex | EBV | RANK | Prog |\n")
        md.append("|------|-----|------|-------|-----|-----|------|------|\n")
        for i, r in enumerate(valid[:top_n], 1):
            ebv = formatter(r) if formatter else f"{r[sort_key]:.3f}"
            md.append(f"| {i} | {r['reg']} | {r['name']} | {r['flock']} | {r['sex']} | {ebv} | {r.get('wfec_rank') if 'wfec' in sort_key else r.get('us_hair_rank') if 'us_hair' in sort_key else ''} | {r['prog'] or '?'} |\n")
        md.append("\n")

    rank_table("Strongest parasite resistance (lowest WFEC)", rows, "wfec", asc=True)
    rank_table("Strongest parasite resistance (lowest PFEC)", rows, "pfec", asc=True)
    rank_table("Heaviest growth (highest PWWT)", rows, "pwwt", asc=False)
    rank_table("Heaviest growth (highest YWT)", rows, "ywt", asc=False)
    rank_table("Highest US Hair Composite Index", rows, "us_hair", asc=False)

    OUT.write_text("".join(md))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
