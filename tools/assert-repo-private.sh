#!/bin/sh
# assert-repo-private.sh — fail-closed gate: refuse to proceed unless a GitHub repo is PRIVATE.
#
# WHY: CLAUDE.md §1.5 — the `ken` repo (and the other personal/pastoral/family repos) are private and
# stay private. On 2026-06-22 `ken` was found PUBLIC for a window (pastoral + memory + automation
# exposed; no creds leaked). This guard prevents the recurrence mode: pushing to a repo that is — or has
# silently become — public. See cluster/INCIDENT_2026-06-22_ken-repo-public.md.
#
# Wire it as a git pre-push hook (see .githooks/pre-push + README) so a push to a must-be-private repo
# aborts BEFORE any data leaves the machine. Also usable standalone in CI / scripts:
#     tools/assert-repo-private.sh [owner/repo]
# With no arg it derives the repo from `origin`. Exit 0 = confirmed private; non-zero = refuse.
#
# FAIL-CLOSED: any inability to confirm "private" (gh missing, unauthenticated, network down, repo not
# found) refuses — silence is treated as exposure (the household's worst-outcome rule). For a genuine
# gh outage, verify visibility by hand and set ASSERT_PRIVATE_OVERRIDE=1 for that one push (logged below).
set -eu

# scrub: redact embedded credentials from ANY string before it is printed. A remote URL can carry a
# token as `https://user:TOKEN@host/...` (e.g. a gh/CI checkout) — echoing it verbatim leaks the token
# into terminals, logs, and AI transcripts. Belt-and-suspenders alongside the credential-stripping
# parse below: every echo of repo/url runs through this so no known token shape ever reaches output.
scrub() {
  printf '%s' "$1" | sed -E \
    -e 's#(://)[^/@]*@#\1***REDACTED***@#g' \
    -e 's#gh[oprsu]_[A-Za-z0-9]+#***REDACTED***#g' \
    -e 's#github_pat_[A-Za-z0-9_]+#***REDACTED***#g'
}

repo="${1:-}"
managed_env=0
if [ -z "$repo" ]; then
  url="$(git config --get remote.origin.url 2>/dev/null || true)"
  # Managed-container recognition (guard-assert-private-managed-env, operator-authorized 2026-07-29):
  # Claude Code Remote / CI sandboxes route git through a LOOPBACK proxy
  # (`http://…@127.0.0.1:PORT/git/<owner>/<repo>`). Two consequences: (1) the userinfo there is a
  # session-local proxy credential that never leaves the machine — the rotate warning below would be
  # noise and its suggested fix would BREAK the sanctioned push path; (2) owner/repo sits after the
  # `/git/` path prefix, not after a github.com host.
  case "$url" in
    *://*127.0.0.1:*|*://*localhost:*|*://*@127.0.0.1:*|*://*@localhost:*) managed_env=1 ;;
  esac
  # Derive owner/repo, stripping CREDENTIALS FIRST so a tokenized URL never reaches gh or output:
  #   1. drop the scheme (https:// , ssh:// , git+ssh:// …)
  #   2. drop any `user[:pass]@` userinfo  ← this is what previously leaked the token
  #   3. drop the github.com host (`github.com/` or `github.com:`) — or, in a managed container,
  #      the loopback host:port and its `/git/` prefix
  #   4. drop a trailing .git
  repo="$(printf '%s' "$url" \
    | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##' \
    | sed -E 's#^[^@/]*@##' \
    | sed -E 's#^(127\.0\.0\.1|localhost):[0-9]+/git/##' \
    | sed -E 's#^github\.com[:/]##' \
    | sed -E 's#\.git$##')"
  # Proactive nudge: a credential embedded in the remote URL (`scheme://user:TOKEN@host/…`) is a
  # standing leak — every `git remote -v`, verbose push, or tool that echoes the URL exposes it. Warn
  # (don't refuse — CI checkouts legitimately use tokenized URLs) and point at the credential-helper fix.
  # Suppressed for the loopback proxy: that credential is machine-local by construction.
  if [ "$managed_env" -eq 0 ]; then
    case "$url" in
      *://*@*) echo "assert-repo-private: ⚠ origin URL embeds a credential — rotate + remove it so it can't leak." >&2
               echo "  Fix: git remote set-url origin https://github.com/$repo.git && gh auth setup-git" >&2 ;;
    esac
  fi
fi
# Whatever the derivation produced must LOOK like owner/repo before it reaches any command line or
# URL — a hostile origin URL must not smuggle metacharacters through this script.
case "$repo" in
  */*) if printf '%s' "$repo" | grep -Eqv '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'; then
         echo "assert-repo-private: derived repo '$(scrub "$repo")' is not a clean owner/repo — REFUSE" >&2; exit 2
       fi ;;
  *)   echo "assert-repo-private: cannot derive owner/repo from origin — REFUSE" >&2; exit 2 ;;
esac
[ -n "$repo" ] || { echo "assert-repo-private: cannot determine repo (no arg, no origin remote) — REFUSE" >&2; exit 2; }

safe_repo="$(scrub "$repo")"

if [ "${ASSERT_PRIVATE_OVERRIDE:-}" = "1" ]; then
  echo "assert-repo-private: ⚠ OVERRIDE set — skipping the check for $safe_repo (operator-asserted private). Logged." >&2
  exit 0
fi

# Managed-container prover (guard-assert-private-managed-env): gh does not exist in the sandbox and
# the anonymous API probe is useless there (the egress proxy 403s BOTH private and public — measured
# 2026-07-29, so it cannot distinguish and must not be trusted). Instead the agent verifies privacy
# via the AUTHENTICATED GitHub MCP and stamps a short-lived attestation that this script validates:
#   .git/hls-private-attestation.json  →  {"repo":"owner/name","private":true,
#                                           "verified_via":"…","verified_at_epoch":N,"verified_by":"…"}
# Accepted ONLY when: repo matches exactly, private is true, and age is 0..24h (ephemeral containers
# live shorter than that; a future timestamp is invalid). Trust level is the SAME as the existing
# ASSERT_PRIVATE_OVERRIDE escape — any local process could write either — but this one is repo-scoped,
# time-boxed, and logged with who/how, which the env var is not. gh remains the primary prover
# wherever it exists; a stale/mismatched/absent attestation falls through to the fail-closed REFUSE.
if ! command -v gh >/dev/null 2>&1; then
  att="$(git rev-parse --git-dir 2>/dev/null || echo .git)/hls-private-attestation.json"
  if [ -f "$att" ] && command -v node >/dev/null 2>&1; then
    # node prints the full human line itself (via/by may contain spaces — no shell word-splitting).
    verdict="$(node -e '
      try {
        const a = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
        const age = Math.floor(Date.now()/1000) - Number(a.verified_at_epoch);
        if (a.repo === process.argv[2] && a.private === true && age >= 0 && age <= 86400) {
          console.log(`OK attested PRIVATE ${age}s ago via ${JSON.stringify(String(a.verified_via||"?"))} by ${JSON.stringify(String(a.verified_by||"?"))}`);
        } else console.log("NO");
      } catch { console.log("NO"); }
    ' "$att" "$repo" 2>/dev/null || echo NO)"
    case "$verdict" in
      OK*) echo "assert-repo-private: ok — $safe_repo ${verdict#OK } (managed container; gh absent)" >&2
           exit 0 ;;
    esac
  fi
  echo "assert-repo-private: gh CLI not found and no valid attestation for $safe_repo — REFUSE (fail-closed)" >&2
  echo "  Managed container: verify via authenticated GitHub MCP, then stamp: node tools/attest-repo-private.mjs $safe_repo" >&2
  exit 3
fi

vis="$(gh repo view "$repo" --json isPrivate --jq '.isPrivate' 2>/dev/null || echo "ERROR")"
case "$vis" in
  true)  echo "assert-repo-private: ok — $safe_repo is PRIVATE" >&2; exit 0 ;;
  false) echo "assert-repo-private: 🚨 REFUSE — $safe_repo is PUBLIC. §1.5: this repo must stay private." >&2
         echo "  Fix: gh repo edit $safe_repo --visibility private --accept-visibility-change-consequences" >&2
         exit 1 ;;
  *)     echo "assert-repo-private: REFUSE — could not confirm $safe_repo is private (gh said: '$(scrub "$vis")')." >&2
         echo "  Verify by hand; for a real gh outage, re-run the push with ASSERT_PRIVATE_OVERRIDE=1." >&2
         exit 4 ;;
esac
