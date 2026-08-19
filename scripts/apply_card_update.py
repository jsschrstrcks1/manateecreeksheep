#!/usr/bin/env python3
"""Apply a single notebook card's data to flock_database.json.

Usage:
    python3 scripts/apply_card_update.py <sheep_id> <img> [--pen PEN] \\
        [--fam DATE:SCORE:NOTES] [--vax DATE:VACCINE] [--tx DATE:TREATMENT:NOTES] \\
        [--note TEXT]

Dates are ISO (2026-02-13). Score can be int, '1-2', or 'u' (unknown).
Multiple --fam, --vax, --tx accepted. Dedupes by (date, source).
"""
import argparse, json, sys
from pathlib import Path

DB = Path(__file__).parent.parent / 'data' / 'flock_database.json'

# pen is an append-only movement log; route --pen through record_move so the move is
# dated and preserved instead of overwriting the past (MCS-9, scripts/pen_state.py).
import importlib.util as _il
_ps_spec = _il.spec_from_file_location("pen_state", str(Path(__file__).parent / "pen_state.py"))
pen_state = _il.module_from_spec(_ps_spec)
_ps_spec.loader.exec_module(pen_state)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheep_id')
    ap.add_argument('img', help='e.g. IMG_0607')
    ap.add_argument('--pen', default=None)
    ap.add_argument('--pen-date', default=None, help='ISO date of the pen move (optional)')
    ap.add_argument('--fam', action='append', default=[], help='DATE:SCORE:NOTES')
    ap.add_argument('--vax', action='append', default=[], help='DATE:VACCINE')
    ap.add_argument('--tx',  action='append', default=[], help='DATE:TREATMENT:NOTES')
    ap.add_argument('--note', action='append', default=[])
    ap.add_argument('--status', default=None)
    ap.add_argument('--tag', default=None)
    ap.add_argument('--sex', default=None)
    args = ap.parse_args()

    d = json.loads(DB.read_text())
    target = None
    for s in d['sheep']:
        if s['id'] == args.sheep_id:
            target = s
            break
    if target is None:
        print(f'ERROR: sheep_id {args.sheep_id} not found', file=sys.stderr); sys.exit(1)

    if args.pen:
        pen_state.seed_from_scalar(target)  # ensure a log exists before the first move
        pen_state.record_move(target, args.pen, date=args.pen_date, source=f"notebook card {args.img}")
    if args.status: target['status'] = args.status
    if args.tag: target['tag'] = args.tag
    if args.sex: target['sex'] = args.sex

    h = target.setdefault('health', {})
    if not isinstance(h, dict):
        h = target['health'] = {}
    fh = h.setdefault('famacha_history', [])
    vx = h.setdefault('vaccinations', [])
    tx = h.setdefault('treatments', [])
    nt = h.setdefault('notes', [])

    def already(lst, keys):
        for e in lst:
            if all(e.get(k) == v for k, v in keys.items()):
                return True
        return False

    for spec in args.fam:
        parts = spec.split(':', 2)
        date, score, notes = (parts + ['', ''])[:3]
        score_val = score if score == '' else (int(score) if score.isdigit() else score)
        entry = {'date': date, 'score': score_val, 'notes': notes, 'source': args.img}
        if not already(fh, {'date': date, 'source': args.img}):
            fh.append(entry)

    for spec in args.vax:
        date, vac = spec.split(':', 1)
        if not already(vx, {'date': date, 'vaccine': vac, 'source': args.img}):
            vx.append({'date': date, 'vaccine': vac, 'source': args.img})

    for spec in args.tx:
        parts = spec.split(':', 2)
        date, t, notes = (parts + ['', ''])[:3]
        if not already(tx, {'date': date, 'treatment': t, 'source': args.img}):
            tx.append({'date': date, 'treatment': t, 'notes': notes, 'source': args.img})

    for note in args.note:
        nt.append({'source': args.img, 'note': note})

    DB.write_text(json.dumps(d, indent=2))
    print(f"ok {args.sheep_id}: pen={target.get('pen')} fam+{len(args.fam)} vax+{len(args.vax)} tx+{len(args.tx)} note+{len(args.note)}")

if __name__ == '__main__':
    main()
