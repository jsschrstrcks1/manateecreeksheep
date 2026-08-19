#!/usr/bin/env node
// attest-repo-private.mjs — stamp the short-lived privacy attestation that
// tools/assert-repo-private.sh accepts when gh is absent (managed containers).
//
// DISCIPLINE (guard-assert-private-managed-env): run this ONLY after actually verifying the
// repo is private through an AUTHENTICATED channel (GitHub MCP repo lookup: "private": true).
// The attestation records repo, when, via what, and by whom; the guard enforces exact repo
// match + ≤24h age + private:true and refuses everything else. Stamping without verifying is
// the same lie as ASSERT_PRIVATE_OVERRIDE without checking — the file just makes the liar
// leave a signature. Soli Deo Gloria.
//
// Usage: node tools/attest-repo-private.mjs <owner/repo> [--via "<how it was verified>"] [--by "<who>"]
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join } from "node:path";

const args = process.argv.slice(2);
const repo = args[0];
const flag = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};
if (!repo || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repo)) {
  console.error("usage: node tools/attest-repo-private.mjs <owner/repo> [--via …] [--by …]");
  process.exit(2);
}
const gitDir = execFileSync("git", ["rev-parse", "--git-dir"], { encoding: "utf8" }).trim();
const path = join(gitDir, "hls-private-attestation.json");
const att = {
  repo,
  private: true,
  verified_via: flag("--via", "authenticated-github-mcp"),
  verified_by: flag("--by", process.env.HLS_PATRON || "unspecified"),
  verified_at_epoch: Math.floor(Date.now() / 1000),
};
writeFileSync(path, JSON.stringify(att, null, 2) + "\n");
console.log(`attested ${repo} private → ${path} (valid ≤24h; guard enforces repo match + age)`);
