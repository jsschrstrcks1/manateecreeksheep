#!/usr/bin/env python3
"""Scrape KHSI digitalovine.com identification + pedigree for ancestor records.

EBV tables on digitalovine.com are loaded via authenticated JavaScript
(login + AJAX), so this script handles the **identification + pedigree**
portion only. EBV data must come via:
  - Manual paste of the EBV table text → parse_nsip_ebv_text.py
  - Or a Selenium/Playwright session (operator with auth)

Usage:
    # Single animal:
    python3 scripts/ebv/scrape_khsi.py 87730
    # Batch from file (one reg per line):
    python3 scripts/ebv/scrape_khsi.py --file data/ebv/registration_numbers.txt
    # Specific lamb's full ancestry (will iterate through known parents):
    python3 scripts/ebv/scrape_khsi.py --ancestors-of centralia-lamb-2026

Each fetched record is written to data/ebv/khsi_cache/<reg>.json
and (if the operator confirms) integrated into data/flock_database.json.

Notes:
  - This script is designed to be re-runnable; cached pages are not re-fetched.
  - We DO NOT auto-write to flock_database.json. The integration is a
    separate manual step (use --integrate to perform it).
  - Errors are logged but do not stop the batch.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
import urllib.request
import re

BASE = "https://katahdin.digitalovine.com/modules.php"
CACHE = Path("data/ebv/khsi_cache")
CACHE.mkdir(parents=True, exist_ok=True)


def url_for(reg: str) -> str:
    params = {"op": "modload", "name": "_animal", "file": "_animal",
              "animal_registration": reg}
    return f"{BASE}?{urlencode(params)}"


def fetch(reg: str, force: bool = False) -> str | None:
    """Fetch the animal detail page HTML. Returns HTML text or None on error."""
    cache_file = CACHE / f"{reg}.html"
    if cache_file.exists() and not force:
        return cache_file.read_text()
    try:
        req = urllib.request.Request(
            url_for(reg),
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) "
                                   "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                                   "Version/16.0 Safari/605.1.15"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        cache_file.write_text(html)
        return html
    except Exception as e:
        print(f"  ERROR fetching {reg}: {e}", file=sys.stderr)
        return None


def parse_identification(html: str) -> dict:
    """Parse identification/other-details from the public detail page."""
    out = {"khsi_registration": None, "name": None, "flock_name_number": None,
           "sex": None, "nsip_id": None,
           "sire_reg": None, "sire_name": None,
           "dam_reg": None, "dam_name": None,
           "coi_percent": None, "breeder": None, "owner": None,
           "service_type": None, "date_of_birth": None,
           "purebred_katahdin": False}

    # Common patterns: <td style="..." nowrap><label>:</td><td>value</td>
    # Most fields use this exact structure with optional &nbsp; padding.
    def find_field(label, html):
        # Labels look like: &nbsp;Label:&nbsp;&nbsp;</td><td>VALUE</td>
        # but Flock Name/Number lacks the wrapping </td><td> — it's
        # &nbsp;Label:&nbsp;&nbsp; followed by </td>...<td>VALUE</td>
        pat = re.compile(
            rf"&nbsp;{re.escape(label)}&nbsp;(?:&nbsp;)?</td>\s*<td[^>]*>(.*?)</td>",
            re.I | re.S,
        )
        m = pat.search(html)
        if m:
            v = re.sub(r"<[^>]+>", "", m.group(1))
            v = re.sub(r"&nbsp;|\s+", " ", v).strip()
            return v or None
        # Try a more permissive match: label followed by any whitespace then next <td>
        pat2 = re.compile(
            rf"{re.escape(label)}.{{0,40}}?</td>\s*<td[^>]*>(.*?)</td>",
            re.I | re.S,
        )
        m = pat2.search(html)
        if m:
            v = re.sub(r"<[^>]+>", "", m.group(1))
            v = re.sub(r"&nbsp;|\s+", " ", v).strip()
            return v or None
        return None

    out["sex"] = find_field("Sex:", html)
    out["name"] = find_field("Name:", html)
    out["flock_name_number"] = find_field("Flock Name/Number:", html)
    out["khsi_registration"] = find_field("Registration:", html)
    out["nsip_id"] = find_field("NSIP ID:", html)
    out["coi_percent_str"] = find_field("COI:", html)
    if out["coi_percent_str"]:
        try:
            out["coi_percent"] = float(out["coi_percent_str"].rstrip("%").strip())
        except (ValueError, AttributeError):
            pass
    out["breeder"] = find_field("Breeder:", html)
    out["owner"] = find_field("Owner:", html)
    out["service_type"] = find_field("Service Type:", html)
    out["date_of_birth"] = find_field("Date of Birth:", html)

    # Sire and Dam — registration numbers are inside JavaScript onclick handlers
    m = re.search(r"Sire:&nbsp;&nbsp;<a[^>]*animal_registration\.value='(\d+)'.*?</a>\s*&nbsp;\s*</td>\s*<td>([^<]+)</td>", html, re.I | re.S)
    if m:
        out["sire_reg"] = m.group(1).strip()
        out["sire_name"] = m.group(2).replace("&nbsp;", " ").strip()
    m = re.search(r"Dam:&nbsp;&nbsp;<a[^>]*animal_registration\.value='(\d+)'.*?</a>\s*&nbsp;\s*</td>\s*<td>([^<]+)</td>", html, re.I | re.S)
    if m:
        out["dam_reg"] = m.group(1).strip()
        out["dam_name"] = m.group(2).replace("&nbsp;", " ").strip()

    # Purebred Katahdin flag
    out["purebred_katahdin"] = bool(re.search(r"Purebred\s+Katahdin", html, re.I))

    return out


def walk_ancestry(start_reg: str, max_depth: int = 5, delay: float = 0.5) -> dict:
    """Walk back through sire/dam links up to max_depth generations.

    Returns {reg: identification_dict}. Caches everything.
    """
    visited = {}
    queue = [(start_reg, 0)]
    while queue:
        reg, depth = queue.pop(0)
        if reg in visited or depth > max_depth:
            continue
        print(f"  fetching {reg} (depth {depth})...")
        html = fetch(reg)
        if not html:
            visited[reg] = {"error": "fetch failed"}
            continue
        ident = parse_identification(html)
        visited[reg] = ident
        time.sleep(delay)
        if ident.get("sire_reg"):
            queue.append((ident["sire_reg"], depth + 1))
        if ident.get("dam_reg"):
            queue.append((ident["dam_reg"], depth + 1))
    return visited


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("registrations", nargs="*", help="One or more KHSI registration numbers")
    ap.add_argument("--file", help="File with one registration per line")
    ap.add_argument("--ancestors-of", help="Walk pedigree of this starting reg",
                    metavar="REG")
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--delay", type=float, default=0.5,
                    help="Seconds between HTTP requests")
    args = ap.parse_args()

    regs = list(args.registrations)
    if args.file:
        regs.extend(line.strip() for line in Path(args.file).read_text().splitlines() if line.strip())

    all_records = {}

    if args.ancestors_of:
        print(f"Walking ancestry from reg {args.ancestors_of} (depth <= {args.max_depth})")
        records = walk_ancestry(args.ancestors_of, args.max_depth, args.delay)
        all_records.update(records)

    for reg in regs:
        print(f"  fetching {reg}...")
        html = fetch(reg)
        if not html:
            all_records[reg] = {"error": "fetch failed"}
            continue
        ident = parse_identification(html)
        all_records[reg] = ident
        time.sleep(args.delay)

    out = Path("data/ebv/khsi_pedigree_dump.json")
    with open(out, "w") as f:
        json.dump({"records": all_records, "count": len(all_records)}, f, indent=2)
    print(f"\nWrote {out} ({len(all_records)} records)")

    # Print summary
    print("\n=== Records with sire/dam found ===")
    for reg, rec in all_records.items():
        if rec.get("error"):
            print(f"  {reg}: ERROR — {rec['error']}")
            continue
        nm = rec.get("name") or "?"
        flk = rec.get("flock_name_number") or "?"
        sire = f"{rec.get('sire_reg','?')} {rec.get('sire_name','')}"
        dam = f"{rec.get('dam_reg','?')} {rec.get('dam_name','')}"
        print(f"  {reg} ({flk}) {nm:25} sire={sire:25} dam={dam}")


if __name__ == "__main__":
    main()
