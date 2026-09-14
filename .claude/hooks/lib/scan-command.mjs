#!/usr/bin/env node
// A.B.O.R.T. destructive-command scanner CLI — a thin wrapper over the shared detector
// (cluster/lib/dangerous-command.mjs). Used by the git pre-commit hook and available for manual/CI use.
//
//   node cluster/scripts/scan-command.mjs "rm -rf /"      # scan one command (arg)
//   echo "rm -rf /" | node cluster/scripts/scan-command.mjs   # scan stdin
//   node cluster/scripts/scan-command.mjs --git-staged    # scan ADDED lines of staged files (pre-commit)
//
// Exit 0 = clean, exit 2 = a catastrophic pattern was found (so callers can `|| exit 1`).

// Leaf layout: the detector is vendored BESIDE this file, not at cluster/lib/, because a leaf
// repo has no cluster/ tree. Same blob either way, only the relative path differs.
import { scanCommand, explain } from "./dangerous-command.mjs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

// The safeguard's own files legitimately CONTAIN these patterns as data (detector, tests, docs, the CLI
// and hook themselves) — never flag a commit for documenting or testing the very thing it guards.
export const EXCLUDE = [
  "dangerous-command", "scan-command", "dangerous-command-guard",
  ".test.mjs", ".test.js", "/tests/", ".md", "SKILL.md", "SOPHOS", "CLAUDE.md", ".githooks/",
  // HLS catalog/events titles + artifacts document hostile probes (guard-quote-split,
  // curl|bash tasks, etc.). Completing those rows rewrites the JSONL line and would
  // false-block every state transition if scanned as shell. Not executable.
  ".household-library/",
  // The household's OWN hook directory, for exactly the reason stated above — it is the
  // safeguard's machinery, and `.githooks/` was already excluded on this same rationale.
  // Measured 2026-08-10: `.claude/hooks/sophos-inject.sh` carries the Sophos doctrine line
  // naming the forbidden shapes, so the scanner matched its own description of what it
  // forbids and REFUSED every merge of origin/main once that file landed there.
  ".claude/hooks/",
  // UL-214: the mutation harness ORACLE fixture (admin/fixtures/guard-oracle.json) is a JSON list of
  // catastrophic commands the harness scores mutants against — data, not executable shell; its
  // generator builds it FROM CHARACTER CODES so no dangerous literal is in source. The safeguard's
  // own test machinery, same rationale as the detector's other test files. Distinctive substrings:
  "guard-oracle", "guard-mutation",
];
// Case-SENSITIVE on purpose. A lowercased match turns the bare `SOPHOS` entry above into a
// SUBSTRING WILDCARD over the whole tree, silently exempting every path containing "sophos" —
// including `atlas/server/sophos.mjs`, the governance kernel itself. Measured 2026-08-10 (navani,
// #2762) end-to-end with this CLI against real staged files: case-insensitivity moved
// `atlas/server/sophos.mjs`, `atlas/server/sophos-pre-thought.mjs` and `tools/sophos-deploy.sh`
// from CAUGHT to skipped — 3 blind spots on EXECUTABLE code.
//
// It also bought nothing. The wedge that motivated it was `.claude/hooks/sophos-inject.sh`, which
// the `.claude/hooks/` entry above already covers; a variant carrying that entry with this
// case-sensitive predicate scored 6/6 on the same battery. And the justification does not hold on
// the merits either: staging the REAL contents of `sophos.mjs` and `sophos-pre-thought.mjs` at a
// non-excluded path scans CLEAN — they do not carry the patterns as data, so exempting them was
// pure loss of coverage. Only `sophos-inject.sh` actually trips the scanner, and it is a hook.
//
// If a case-insensitive match is ever genuinely wanted, narrow `SOPHOS` to a real path prefix
// first (e.g. `docs/SOPHOS-`), so it cannot act as a wildcard over executable code.
export const excluded = (p) => EXCLUDE.some((e) => p.includes(e));

function report(source, hits) {
  for (const h of hits) {
    process.stderr.write(`\n${source}\n` + explain(h.result) + (h.line ? `\n   (at: ${h.line})` : "") + "\n");
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args[0] === "--git-staged") {
    // Scan added lines (+, not +++) of staged files, skipping the safeguard's own files.
    let diff = "";
    try { diff = execFileSync("git", ["diff", "--cached", "--unified=0", "--no-color"], { encoding: "utf8" }); } catch { process.exit(0); }
    let file = null;
    const hits = [];
    for (const raw of diff.split("\n")) {
      if (raw.startsWith("+++ ")) { file = raw.slice(4).replace(/^b\//, ""); continue; }
      if (!raw.startsWith("+") || raw.startsWith("+++")) continue;
      if (!file || excluded(file)) continue;
      const added = raw.slice(1);
      const result = scanCommand(added);
      if (result.blocked) hits.push({ result, line: `${file}: ${added.trim().slice(0, 100)}` });
    }
    if (hits.length) { process.stderr.write("⛔ pre-commit: a staged change introduces a catastrophic command pattern:\n"); report("", hits); process.exit(2); }
    process.exit(0);
  }

  let cmd = args.join(" ").trim();
  if (!cmd) { try { for await (const c of process.stdin) cmd += c; } catch { /* */ } cmd = cmd.trim(); }
  if (!cmd) { process.stderr.write("usage: scan-command.mjs \"<command>\" | --git-staged | (stdin)\n"); process.exit(0); }

  const result = scanCommand(cmd);
  if (result.blocked) { process.stderr.write(explain(result) + "\n"); process.exit(2); }
  process.stdout.write("ok: no catastrophic pattern detected\n");
  process.exit(0);
}
// Run only when invoked as a CLI (the pre-commit hook), so tests can import `excluded`/`EXCLUDE`.
const isCli = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isCli) main();
