#!/usr/bin/env python3
"""Scrape KHSI/digitalovine.com EBV tables using a logged-in browser session.

The public HTML doesn't include EBV data — those are AJAX-loaded after
the operator clicks the EBVs tab in a logged-in session. This script uses
Playwright to drive a real Chromium, log in, click each animal's EBVs
tab, wait for the data to render, then read the DOM.

USAGE (two-step pattern):

  Step 1 — one-time login (saves session state):
    python3 scripts/ebv/scrape_khsi_ebvs.py login

  Step 2 — scrape EBVs for one or more animals:
    python3 scripts/ebv/scrape_khsi_ebvs.py scrape 87730 146843 52391
    # or pull from the pedigree dump:
    python3 scripts/ebv/scrape_khsi_ebvs.py scrape --from-pedigree-dump

The session is stored in data/ebv/khsi_session.json; re-run login if
the session expires. Username/password are NEVER stored — only the
post-login cookie/state.

Output:
  data/ebv/ebvs_scraped/<reg>.json  — one JSON file per animal
  Optionally --integrate to push the results into flock_database.json
"""
from __future__ import annotations
import argparse
import getpass
import json
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium",
          file=sys.stderr)
    sys.exit(1)

BASE = "https://katahdin.digitalovine.com"
SESSION_FILE = Path("data/ebv/khsi_session.json")
OUT_DIR = Path("data/ebv/ebvs_scraped")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)


def url_for(reg: str) -> str:
    return (f"{BASE}/modules.php?op=modload&name=_animal&file=_animal"
            f"&animal_registration={reg}")


def cmd_login(args):
    """Open a browser, let operator log in interactively, save the session."""
    print("Opening browser. Log in manually, then close the browser window.")
    print("(If you're already logged in or session-saved, just close it.)")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(BASE)
        # Wait until user closes the page or browser
        try:
            while not page.is_closed():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        ctx.storage_state(path=str(SESSION_FILE))
        browser.close()
    print(f"Session saved to {SESSION_FILE}")


def extract_ebvs_from_page(page) -> dict:
    """After navigating to an animal's page and clicking EBVs tab, return the
    parsed EBV table as structured JSON."""
    # Click the EBVs tab
    try:
        page.click("text=EBVs", timeout=8000)
    except Exception as e:
        print(f"  WARN: could not click EBVs tab: {e}", file=sys.stderr)
        return {}

    # Wait for the EBV content to render (AJAX). The data tables typically
    # contain trait codes BWT, WFEC etc.
    try:
        page.wait_for_selector("text=WFEC", timeout=15000)
    except Exception:
        print("  WARN: EBV table did not render (no WFEC text seen)", file=sys.stderr)
        return {}

    # Pull the EBV table HTML out of the DOM. The format on digitalovine.com:
    # table rows for Subject / Sire / Dam, with columns interleaving
    # VAL / ±SE / ACC / RANK per trait.
    raw_text = page.evaluate("""() => {
        // Find a node containing "WFEC" then walk up to the nearest table or
        // table-like container.
        const walk = (node) => {
            while (node && node.tagName !== 'TABLE' && node.tagName !== 'BODY') {
                node = node.parentElement;
            }
            return node;
        };
        // Heuristic: find all <td> containing trait codes
        const candidates = [];
        document.querySelectorAll('td, span, div').forEach(el => {
            if (el.textContent.trim() === 'WFEC') candidates.push(walk(el));
        });
        if (!candidates.length) return null;
        // Take the smallest (deepest) ancestor table
        const tbl = candidates[0];
        return tbl ? tbl.outerHTML : null;
    }""")

    if not raw_text:
        return {"error": "no EBV table found in DOM"}

    return {"raw_html": raw_text, "ts": int(time.time())}


def cmd_scrape(args):
    """Scrape EBVs for one or more animals."""
    if not SESSION_FILE.exists():
        print("ERROR: no session saved. Run `login` first.", file=sys.stderr)
        sys.exit(1)

    regs = list(args.regs)
    if args.from_pedigree_dump:
        dump_path = Path("data/ebv/khsi_pedigree_dump.json")
        if dump_path.exists():
            dump = json.loads(dump_path.read_text())
            regs.extend(dump.get("records", {}).keys())
    regs = sorted(set(regs))
    if not regs:
        print("No registration numbers given.", file=sys.stderr)
        sys.exit(1)

    print(f"Scraping EBVs for {len(regs)} animal(s)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        ctx = browser.new_context(storage_state=str(SESSION_FILE))
        page = ctx.new_page()

        for i, reg in enumerate(regs, 1):
            out_path = OUT_DIR / f"{reg}.json"
            if out_path.exists() and not args.force:
                print(f"  [{i}/{len(regs)}] {reg}: cached, skipping")
                continue
            print(f"  [{i}/{len(regs)}] {reg}: fetching...")
            try:
                page.goto(url_for(reg), wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"    nav error: {e}", file=sys.stderr)
                continue
            ebvs = extract_ebvs_from_page(page)
            if ebvs:
                out_path.write_text(json.dumps({"reg": reg, **ebvs}, indent=2))
                print(f"    -> wrote {out_path}")
            else:
                print("    no EBVs extracted")
            time.sleep(args.delay)

        browser.close()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_login = sub.add_parser("login", help="Open browser for interactive login")
    p_login.set_defaults(func=cmd_login)

    p_scrape = sub.add_parser("scrape", help="Scrape EBVs after login")
    p_scrape.add_argument("regs", nargs="*",
                          help="Registration numbers to scrape")
    p_scrape.add_argument("--from-pedigree-dump", action="store_true",
                          help="Pull regs from data/ebv/khsi_pedigree_dump.json")
    p_scrape.add_argument("--headless", action="store_true",
                          help="Run headless (default: shows browser)")
    p_scrape.add_argument("--force", action="store_true",
                          help="Re-scrape even if cached")
    p_scrape.add_argument("--delay", type=float, default=1.5,
                          help="Seconds between requests (default 1.5)")
    p_scrape.set_defaults(func=cmd_scrape)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
