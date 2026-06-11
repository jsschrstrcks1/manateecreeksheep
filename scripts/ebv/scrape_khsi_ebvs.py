#!/usr/bin/env python3
"""KHSI EBV scraper — public, no login required.

Discovery 2026-06-11: EBV data on digitalovine.com is publicly visible
once the EBVs tab is clicked. WebFetch couldn't run the JS, but a real
browser (Playwright) renders the table fine. The site's TLS cert is
not in the default trust store, so we set ignore_https_errors.

Usage:
    # Scrape one or many regs:
    python3 scripts/ebv/scrape_khsi_ebvs.py 87730 146843 52391

    # Scrape every animal in the cached pedigree dump:
    python3 scripts/ebv/scrape_khsi_ebvs.py --from-pedigree-dump

    # Integrate scraped EBVs into the flock database:
    python3 scripts/ebv/scrape_khsi_ebvs.py --integrate

Outputs:
    data/ebv/ebvs_scraped/<reg>.json    — parsed EBV table per animal

Re-runs skip already-cached results. --force to override.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
except ImportError:
    print("ERROR: pip install playwright && playwright install chromium",
          file=sys.stderr)
    sys.exit(1)

BASE = "https://katahdin.digitalovine.com"
OUT_DIR = Path("data/ebv/ebvs_scraped")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIT_ORDER = ["BWT","MBWT","WWT","MWWT","PWWT","YWT","HWT",
               "PFAT","PEMD","WFEC","PFEC","PSC","NLB","NLW"]
TRAIT_GROUPS = {
    "weight_traits": ["BWT","MBWT","WWT","MWWT","PWWT","YWT","HWT"],
    "carcass_traits": ["PFAT","PEMD"],
    "parasite_resistance": ["WFEC","PFEC"],
    "reproduction": ["PSC","NLB","NLW"],
}


def url_for(reg: str) -> str:
    return (f"{BASE}/modules.php?op=modload&name=_animal&file=_animal"
            f"&animal_registration={reg}")


def looks_like_num(tok: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok))


def looks_like_acc(tok: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}", tok)) and 0 <= int(tok) <= 100


def looks_like_rank(tok: str) -> bool:
    return tok in ("-", "<5") or bool(re.fullmatch(r"\d{1,3}", tok))


def parse_ebv_text(text: str) -> dict:
    """Parse the publicly-rendered EBV table text into structured form.

    The text contains a header (Weight Traits / Carcass / Fecal Egg /
    Reproduction / US Hair), trait code row (BWT MBWT WWT...), then
    Subject/Sire/Dam rows with interleaved VAL ±SE ACC RANK groups.
    """
    out = {"blocks": [], "snapshot_date": None}

    # Snapshot date — typically YYYYMMDD shown above NSIP Results
    m = re.search(r"\b(20\d{6})\b", text)
    if m:
        d = m.group(1)
        out["snapshot_date"] = f"{d[:4]}-{d[4:6]}-{d[6:]}"

    # Split the page into "Subject (Active Sire)" / "Sire" / "Dam" sections.
    # Each section header line includes Prog and (optional) Flocks counts.
    lines = [l.strip() for l in text.split("\n")]

    # Find positions of role markers
    roles = []
    for i, l in enumerate(lines):
        if re.match(r"^Subject\b", l, re.I):
            roles.append((i, "subject"))
        elif re.match(r"^Sire\b", l, re.I):
            roles.append((i, "sire"))
        elif re.match(r"^Dam\b", l, re.I):
            roles.append((i, "dam"))

    for idx, (start, role) in enumerate(roles):
        end = roles[idx + 1][0] if idx + 1 < len(roles) else len(lines)
        chunk = " ".join(lines[start:end])
        # Pull Prog / Flocks
        prog = None
        flocks = None
        m = re.search(r"Prog[:\s]+(\d+)", chunk, re.I)
        if m: prog = int(m.group(1))
        m = re.search(r"Flocks?[:\s]+(\d+)", chunk, re.I)
        if m: flocks = int(m.group(1))

        # Strip everything up through "VAL +/- ACC RANK" or similar
        m = re.search(r"VAL[^A-Za-z]*?ACC[^A-Za-z]*?RANK", chunk, re.I)
        if not m:
            continue
        values_part = chunk[m.end():].strip()
        tokens = re.split(r"\s+", values_part)

        # Walk the tokens: per trait read VAL (numeric), optional ±SE, ACC, RANK
        traits = {}
        pos = 0
        for code in TRAIT_ORDER:
            if pos >= len(tokens):
                break
            val = se = acc = rank = None
            # Skip blank markers
            while pos < len(tokens) and tokens[pos] in ("", "-", "—"):
                if tokens[pos] == "-" and pos + 1 < len(tokens) and tokens[pos + 1] not in ("VAL", "+/-", "ACC", "RANK"):
                    # could be a lone "-" representing blank rank later; back off
                    break
                pos += 1
            if pos < len(tokens) and looks_like_num(tokens[pos]):
                val = float(tokens[pos]); pos += 1
            # Detect SE: small positive decimal before an ACC integer (1-100)
            if (pos + 1 < len(tokens) and looks_like_num(tokens[pos])
                    and looks_like_acc(tokens[pos + 1])):
                try:
                    tv = float(tokens[pos])
                    if 0 < tv < 10:
                        se = tv; pos += 1
                except ValueError:
                    pass
            if pos < len(tokens) and looks_like_acc(tokens[pos]):
                acc = int(tokens[pos]); pos += 1
            if pos < len(tokens) and looks_like_rank(tokens[pos]):
                t = tokens[pos]
                rank = t if t in ("-", "<5") else int(t)
                pos += 1
            if any(v is not None for v in (val, se, acc, rank)):
                traits[code] = {"val": val, "se": se, "acc": acc, "rank": rank}

        # US Hair index = next numeric + next rank-like
        us_hair = None
        while pos < len(tokens):
            t = tokens[pos]
            if looks_like_num(t):
                us_hair = {"val": float(t), "rank": None}
                pos += 1
                if pos < len(tokens) and looks_like_rank(tokens[pos]):
                    rt = tokens[pos]
                    us_hair["rank"] = rt if rt in ("-", "<5") else int(rt)
                    pos += 1
                break
            pos += 1

        block = {
            "role": role,
            "progeny_evaluated": prog,
            "flocks_represented": flocks,
            "raw_traits": traits,
        }
        for grp, codes in TRAIT_GROUPS.items():
            block[grp] = {c: traits[c] for c in codes if c in traits}
        if us_hair:
            block["us_hair_composite_index"] = us_hair
        out["blocks"].append(block)

    return out


def scrape_one(page, reg: str, click_timeout: int = 12000,
               wfec_timeout: int = 20000) -> dict | None:
    """Navigate to one animal's page, click EBVs tab, return parsed data."""
    try:
        page.goto(url_for(reg), wait_until="networkidle", timeout=30000)
    except Exception as e:
        return {"error": f"nav: {e}"}
    try:
        page.click("text=EBVs", timeout=click_timeout)
    except Exception as e:
        # Some animals genuinely lack EBV data — the EBVs tab is absent or
        # disabled. Record this so we don't retry forever.
        return {"error": f"tab-click: {e}"}
    try:
        page.wait_for_selector("text=WFEC", timeout=wfec_timeout)
    except PWTimeoutError:
        return {"error": "EBV table did not render (animal has no NSIP data)"}
    body_text = page.evaluate("() => document.body.innerText")
    parsed = parse_ebv_text(body_text)
    parsed["reg"] = reg
    parsed["scraped_at"] = int(time.time())
    return parsed


def cmd_scrape(args):
    regs = list(args.regs)
    if args.from_pedigree_dump:
        dump = Path("data/ebv/khsi_pedigree_dump.json")
        if dump.exists():
            d = json.loads(dump.read_text())
            regs.extend(d.get("records", {}).keys())
    regs = sorted(set(regs))
    if not regs:
        print("No regs given.", file=sys.stderr)
        sys.exit(1)
    print(f"Scraping {len(regs)} animals...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                    args=["--ignore-certificate-errors"])
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        n_ok = n_err = 0
        for i, reg in enumerate(regs, 1):
            out = OUT_DIR / f"{reg}.json"
            if out.exists() and not args.force:
                print(f"  [{i}/{len(regs)}] {reg}: cached")
                continue
            print(f"  [{i}/{len(regs)}] {reg}: scraping...", end=" ")
            res = scrape_one(page, reg)
            if res and not res.get("error"):
                out.write_text(json.dumps(res, indent=2))
                print(f"OK ({len(res.get('blocks', []))} blocks)")
                n_ok += 1
            else:
                err = res.get("error") if res else "unknown"
                print(f"FAIL: {err}")
                n_err += 1
                # Save error stub so we don't retry every time
                out.write_text(json.dumps({"reg": reg, "error": err, "scraped_at": int(time.time())}, indent=2))
            time.sleep(args.delay)
        browser.close()
        print(f"\nDone. OK: {n_ok}, errors: {n_err}")


def cmd_integrate(args):
    """Push scraped EBVs into the flock database's nsip_ebvs fields."""
    with open("data/flock_database.json") as f:
        db = json.load(f)
    sheep_by_reg = {}
    for s in db["sheep"]:
        reg = s.get("registration", {}).get("reg_number") if isinstance(s.get("registration"), dict) else None
        if reg:
            sheep_by_reg[str(reg)] = s
        # Also index by tag, in case the registration field isn't populated
        for t in (s.get("tag"), s.get("mc_tag")):
            if t and isinstance(t, str) and t.isdigit():
                sheep_by_reg.setdefault(t, s)

    n_matched = 0
    n_unmatched = 0
    for fp in sorted(OUT_DIR.glob("*.json")):
        reg = fp.stem
        data = json.loads(fp.read_text())
        if data.get("error"):
            continue
        # Get subject block
        subj = next((b for b in data.get("blocks", []) if b.get("role") == "subject"), None)
        if not subj:
            continue
        sheep = sheep_by_reg.get(reg)
        if not sheep:
            n_unmatched += 1
            continue
        ebvs_struct = {
            "snapshot_date": data.get("snapshot_date"),
            "progeny_evaluated": subj.get("progeny_evaluated"),
            "flocks_represented": subj.get("flocks_represented"),
            "weight_traits": subj.get("weight_traits", {}),
            "carcass_traits": subj.get("carcass_traits", {}),
            "parasite_resistance": subj.get("parasite_resistance", {}),
            "reproduction": subj.get("reproduction", {}),
            "us_hair_composite_index": subj.get("us_hair_composite_index"),
            "source": "Auto-scraped from digitalovine.com 2026-06-11",
        }
        if "nsip_ebvs" in sheep:
            sheep["nsip_ebvs_prior"] = sheep["nsip_ebvs"]
        sheep["nsip_ebvs"] = ebvs_struct
        n_matched += 1
    with open("data/flock_database.json", "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Integrated {n_matched} EBV records into flock_database.json")
    print(f"Unmatched (no sheep record for reg): {n_unmatched}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regs", nargs="*")
    ap.add_argument("--from-pedigree-dump", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--delay", type=float, default=0.8)
    ap.add_argument("--integrate", action="store_true",
                    help="Integrate scraped EBVs into flock_database.json")
    args = ap.parse_args()

    if args.integrate and not args.regs and not args.from_pedigree_dump:
        cmd_integrate(args)
        return

    cmd_scrape(args)
    if args.integrate:
        cmd_integrate(args)


if __name__ == "__main__":
    main()
