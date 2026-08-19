#!/usr/bin/env python3
"""Build the pen-census phone page: the owner's "you'll have to show me" (2026-08-19).

Soli Deo Gloria.

94 living animals have no recorded pen. Nobody answers that from a list of ids in a
markdown file — you answer it walking the pens with a phone. This bakes the no-pen
roster into app/census.html: one row per animal, eight canonical pen buttons (plus
Sold / Deceased / Skip for status corrections), progress in localStorage so a dropped
phone at animal 60 loses nothing, and an Export block that emits one line per decided
animal for paste-back. Answers are applied to the DB through validated commits — the
page never writes anything itself.

Same discipline as the chute app (MCS-6/33/34 slice): self-contained, no server, no
network, no third-party code; header shows the data build date so a stale copy is
visible, never silent.
"""
import datetime
import importlib.util
import json
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))

_spec = importlib.util.spec_from_file_location("ph", _here / "lib" / "pen_history.py")
ph = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ph)

REPO = _here.parent
DB = REPO / "data" / "flock_database.json"
OUT = REPO / "app" / "census.html"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pen Census — Manatee Creek</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 0 0 6rem 0;
         background: #f4f1ea; color: #222; }
  @media (prefers-color-scheme: dark) { body { background: #1b1a17; color: #eee; } }
  header { position: sticky; top: 0; background: #3d5a3d; color: #fff; padding: .7rem 1rem;
           z-index: 2; }
  header h1 { font-size: 1.05rem; margin: 0; }
  header .meta { font-size: .75rem; opacity: .85; }
  .row { padding: .6rem .8rem; border-bottom: 1px solid rgba(128,128,128,.25); }
  .row.done { opacity: .45; }
  .who { font-weight: 600; margin-bottom: .35rem; }
  .who small { font-weight: 400; opacity: .7; }
  .pens { display: flex; flex-wrap: wrap; gap: .35rem; }
  button.pen { border: 1px solid rgba(128,128,128,.5); border-radius: .5rem;
               padding: .5rem .65rem; font-size: .85rem; background: rgba(128,128,128,.12);
               color: inherit; }
  button.pen.picked { background: #3d5a3d; color: #fff; border-color: #3d5a3d; }
  button.pen.status { background: rgba(180,120,40,.15); }
  button.pen.status.picked { background: #a05a2c; border-color: #a05a2c; }
  footer { position: fixed; bottom: 0; left: 0; right: 0; background: #3d5a3d; color: #fff;
           padding: .6rem 1rem; display: flex; gap: .8rem; align-items: center; }
  footer button { border: 0; border-radius: .5rem; padding: .55rem .9rem; font-weight: 600; }
  #exportBox { display: none; white-space: pre-wrap; font-family: ui-monospace, monospace;
               font-size: .78rem; background: rgba(128,128,128,.12); margin: .8rem;
               padding: .8rem; border-radius: .5rem; }
</style>
</head>
<body>
<header>
  <h1>Pen census — tap where each one lives</h1>
  <div class="meta">__COUNT__ animals without a pen · data build __BUILD__ · progress saves on this phone</div>
</header>
<div id="list"></div>
<div id="exportBox"></div>
<footer>
  <span id="progress"></span>
  <button onclick="doExport()">Export answers</button>
  <button onclick="if(confirm('Clear all answers on this phone?')){localStorage.removeItem(KEY);render();}">Reset</button>
</footer>
<script>
const ANIMALS = __ANIMALS__;
const PENS = __PENS__;
const STATUSES = ["Sold", "Deceased", "Skip"];
const KEY = "mcs-pen-census-v1";
const state = () => JSON.parse(localStorage.getItem(KEY) || "{}");
function pick(id, val) {
  const s = state(); s[id] = (s[id] === val) ? undefined : val;
  localStorage.setItem(KEY, JSON.stringify(s)); render();
}
function render() {
  const s = state();
  const el = document.getElementById("list");
  el.innerHTML = ANIMALS.map(a => {
    const chosen = s[a.id];
    const btn = (v, cls) => `<button class="pen ${cls}${chosen===v?" picked":""}"
      onclick="pick('${a.id}','${v}')">${v}</button>`;
    return `<div class="row${chosen?" done":""}">
      <div class="who">${a.name || a.id} <small>${a.tag ? "tag "+a.tag+" · " : ""}${a.sex||""} · ${a.id}</small></div>
      <div class="pens">${PENS.map(p=>btn(p,"")).join("")}${STATUSES.map(v=>btn(v,"status")).join("")}</div>
    </div>`;
  }).join("");
  const done = Object.values(s).filter(Boolean).length;
  document.getElementById("progress").textContent = done + " / " + ANIMALS.length;
}
function doExport() {
  const s = state();
  const lines = ANIMALS.filter(a => s[a.id] && s[a.id] !== "Skip")
    .map(a => a.id + " -> " + s[a.id]);
  const box = document.getElementById("exportBox");
  box.style.display = "block";
  box.textContent = lines.length
    ? "PEN CENSUS " + new Date().toISOString().slice(0,10) + "\\n" + lines.join("\\n")
    : "(nothing answered yet)";
  box.scrollIntoView({behavior:"smooth"});
  if (navigator.clipboard && lines.length) navigator.clipboard.writeText(box.textContent);
}
render();
</script>
</body>
</html>
"""


def main():
    db = json.loads(DB.read_text())
    no_pen = [{"id": s["id"], "name": s.get("name"), "tag": s.get("tag"), "sex": s.get("sex")}
              for s in db["sheep"] if s.get("status") == "alive" and not s.get("pen")]
    no_pen.sort(key=lambda a: (a.get("name") or a["id"]).lower())
    html = (TEMPLATE
            .replace("__ANIMALS__", json.dumps(no_pen))
            .replace("__PENS__", json.dumps(list(ph.CANONICAL_PENS)))
            .replace("__COUNT__", str(len(no_pen)))
            .replace("__BUILD__", datetime.date.today().isoformat()))
    OUT.write_text(html)
    print(f"wrote {OUT} — {len(no_pen)} animals, pens: {', '.join(ph.CANONICAL_PENS)}")


if __name__ == "__main__":
    main()
