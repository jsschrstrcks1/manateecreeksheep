#!/usr/bin/env python3
"""Parse a copied-pasted KHSI NSIP EBV table into structured form.

EBV tables on digitalovine.com are JS-rendered behind a login, so they
can't be auto-scraped. The operator copies them and pastes into a text
file (one animal at a time), and this script parses + integrates into
the database.

Expected paste format (whitespace-separated, blank cells are OK):

    Subject (Active Sire)  Prog: 58  Flocks: 5
    VAL +/- ACC RANK
    0.177 0.17 85 30
    -0.294 _ 88 <5
    ...

OR the full multi-line dump (the format the user has been pasting),
where the header row is "BWT MBWT WWT MWWT PWWT YWT HWT PFAT PEMD WFEC
PFEC PSC NLB NLW" and the value rows interleave VAL/±/ACC/RANK groups.

Usage:
    python3 scripts/ebv/parse_nsip_paste.py \
        --reg 87730 \
        --snapshot 2025-09-22 \
        --paste path/to/paste.txt

Writes the parsed structure under the named animal's sheep record in
data/flock_database.json under the `nsip_ebvs` field. Backs up the
existing record's nsip_ebvs (if any) as `nsip_ebvs_prior`.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


TRAIT_ORDER = ["BWT","MBWT","WWT","MWWT","PWWT","YWT","HWT",
               "PFAT","PEMD","WFEC","PFEC","PSC","NLB","NLW"]

TRAIT_GROUPS = {
    "weight_traits": ["BWT","MBWT","WWT","MWWT","PWWT","YWT","HWT"],
    "carcass_traits": ["PFAT","PEMD"],
    "parasite_resistance": ["WFEC","PFEC"],
    "reproduction": ["PSC","NLB","NLW"],
}


def looks_like_value(tok: str) -> bool:
    """A token that's a possible numeric VAL or +/- or US Hair index."""
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok))


def looks_like_acc(tok: str) -> bool:
    """ACC values are 2- or 3-digit integers 0-100."""
    return bool(re.fullmatch(r"\d{1,3}", tok)) and 0 <= int(tok) <= 100


def looks_like_rank(tok: str) -> bool:
    """RANK is integer percentile, "<5", or "-" (no rank)."""
    return tok in ("-", "<5") or bool(re.fullmatch(r"\d{1,3}", tok))


def split_rows(text: str) -> list[str]:
    """Split paste into logical rows. Tries newlines first; falls back to
    splitting on Subject/Sire/Dam keywords."""
    # Normalize whitespace + collapse multi-space
    lines = [l.strip() for l in text.replace("\t", " ").split("\n") if l.strip()]
    return lines


def parse_animal_block(lines: list[str], start_idx: int) -> tuple[dict, int]:
    """Parse one Subject/Sire/Dam block starting at line `start_idx`.

    Returns (parsed_dict, next_start_index).
    """
    # Find "Prog: N" and "Flocks: N" if present in the first line
    header = lines[start_idx]
    role = "subject"
    if header.lower().startswith("sire"):
        role = "sire"
    elif header.lower().startswith("dam"):
        role = "dam"

    prog = flocks = None
    m = re.search(r"Prog[:\s]+(\d+)", header, re.I)
    if m: prog = int(m.group(1))
    m = re.search(r"Flocks?[:\s]+(\d+)", header, re.I)
    if m: flocks = int(m.group(1))

    # Collect tokens from subsequent lines until the next role keyword
    # or end of input.
    tokens = []
    i = start_idx + 1
    while i < len(lines):
        l = lines[i]
        low = l.lower().lstrip()
        if low.startswith("subject") or low.startswith("sire") or low.startswith("dam"):
            break
        # Skip the VAL/ACC/RANK header
        if re.match(r"^(VAL|ACC|RANK|\+/-|\s)+$", l, re.I):
            i += 1
            continue
        tokens.extend(re.split(r"\s+", l))
        i += 1

    # The tokens contain interleaved VAL / ±SE / ACC / RANK for 14 traits
    # + a final US Hair index. We try to walk them by:
    #   per trait: read VAL (numeric or blank), optional ±SE (numeric),
    #              ACC (1-100 integer), RANK (<5 / integer / "-").
    traits = {}
    pos = 0
    for code in TRAIT_ORDER:
        # blank cell → skip
        # We need a heuristic to detect when a cell is blank. For now,
        # try a "best-fit" approach: peek ahead and validate.
        if pos >= len(tokens):
            break
        # Skip explicit blank-cell markers
        while pos < len(tokens) and tokens[pos] in ("_", "—", ""):
            pos += 1
            continue
        val = se = acc = rank = None
        # Try VAL
        if pos < len(tokens) and looks_like_value(tokens[pos]):
            val = float(tokens[pos]); pos += 1
        # Try ±SE if next token looks like SE (small decimal usually < 5)
        if pos < len(tokens) and looks_like_value(tokens[pos]) and looks_like_acc(tokens[pos+1] if pos+1 < len(tokens) else ""):
            # Heuristic: SE is between val and ACC (which is 1-100 integer)
            # Only treat as SE if it's positive (SE is always non-negative)
            try:
                tval = float(tokens[pos])
                if 0 < tval < 10:
                    se = tval; pos += 1
            except ValueError:
                pass
        # ACC
        if pos < len(tokens) and looks_like_acc(tokens[pos]):
            acc = int(tokens[pos]); pos += 1
        # RANK
        if pos < len(tokens) and looks_like_rank(tokens[pos]):
            t = tokens[pos]
            rank = t if t in ("-", "<5") else int(t)
            pos += 1

        if val is not None or acc is not None or rank is not None:
            traits[code] = {"val": val, "se": se, "acc": acc, "rank": rank}

    # US Hair Composite Index = whatever's left
    us_hair_val = None
    us_hair_rank = None
    while pos < len(tokens):
        t = tokens[pos]
        if looks_like_value(t) and us_hair_val is None:
            us_hair_val = float(t)
        elif looks_like_rank(t) and us_hair_val is not None:
            us_hair_rank = t if t in ("-", "<5") else int(t)
            break
        pos += 1

    block = {"role": role, "progeny_evaluated": prog, "flocks_represented": flocks,
             "raw_traits": traits}
    # Group into NSIP categories
    for grp, codes in TRAIT_GROUPS.items():
        block[grp] = {c: traits[c] for c in codes if c in traits}
    if us_hair_val is not None:
        block["us_hair_composite_index"] = {"val": us_hair_val, "rank": us_hair_rank}
    return block, i


def parse_paste(text: str) -> list[dict]:
    """Parse a paste containing one or more animal blocks (Subject/Sire/Dam)."""
    lines = split_rows(text)
    blocks = []
    i = 0
    while i < len(lines):
        l = lines[i].lower().lstrip()
        if l.startswith("subject") or l.startswith("sire") or l.startswith("dam"):
            block, next_i = parse_animal_block(lines, i)
            blocks.append(block)
            i = next_i
        else:
            i += 1
    return blocks


def find_sheep(db: dict, reg: str) -> dict | None:
    """Find a sheep record by KHSI registration number, in any of:
    registration.reg_number, tag, or any alias containing the number."""
    for s in db["sheep"]:
        reg_str = str(reg)
        if s.get("registration", {}).get("reg_number") == reg_str:
            return s
        if s.get("tag") and str(s["tag"]) == reg_str:
            return s
        for a in s.get("aliases", []) or []:
            if reg_str in str(a):
                return s
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reg", required=True, help="KHSI registration number")
    ap.add_argument("--snapshot", required=True, help="NSIP snapshot date YYYY-MM-DD")
    ap.add_argument("--paste", required=True, help="Path to text file with pasted EBV table")
    ap.add_argument("--db", default="data/flock_database.json")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print parsed result without writing to DB")
    args = ap.parse_args()

    text = Path(args.paste).read_text()
    blocks = parse_paste(text)
    if not blocks:
        print("ERROR: No Subject/Sire/Dam blocks found in paste", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(blocks)} block(s):")
    for b in blocks:
        traits_with_data = [c for c, v in b.get("raw_traits", {}).items()
                             if v.get("val") is not None or v.get("acc") is not None]
        print(f"  {b['role']}: prog={b.get('progeny_evaluated')}, "
              f"flocks={b.get('flocks_represented')}, "
              f"traits with data: {', '.join(traits_with_data)}")

    if args.dry_run:
        print("\n--- Subject block (full) ---")
        print(json.dumps(blocks[0], indent=2))
        return

    # Integrate Subject into DB
    with open(args.db) as f:
        db = json.load(f)
    sheep = find_sheep(db, args.reg)
    if not sheep:
        print(f"ERROR: No sheep record found for reg {args.reg}", file=sys.stderr)
        print("Add the animal first (e.g., via scrape_khsi.py), then re-run.", file=sys.stderr)
        sys.exit(1)

    subject_block = next((b for b in blocks if b["role"] == "subject"), blocks[0])
    new_ebvs = {
        "snapshot_date": args.snapshot,
        "progeny_evaluated": subject_block.get("progeny_evaluated"),
        "flocks_represented": subject_block.get("flocks_represented"),
        **{k: v for k, v in subject_block.items() if k in TRAIT_GROUPS or k == "us_hair_composite_index"},
        "source": f"Owner-supplied NSIP detail screen paste, snapshot {args.snapshot}",
    }
    if "nsip_ebvs" in sheep:
        sheep["nsip_ebvs_prior"] = sheep["nsip_ebvs"]
    sheep["nsip_ebvs"] = new_ebvs
    print(f"\nUpdated sheep[{sheep['id']}].nsip_ebvs")

    with open(args.db, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
