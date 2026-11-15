# Submission sweep — BriefGate v1 (2026-11-15)

Sweep run on the source tree + the built artifact (frontend `dist/` bundle +
the live API run), before filing. Method: `git ls-files` / `git grep` over
tracked files only, plus live checks.

## Source sweep (tracked files)

| Check | Result |
|---|---|
| Files that must never be tracked (`node_modules`, `dist/`, `.venv`, `runs/`, `*.pyc`, `__pycache__`) | None tracked. PASS |
| `tsconfig.tsbuildinfo` (build artifact) | Was tracked — removed from tracking, added to `.gitignore`. FIXED |
| TODO / FIXME / XXX / lorem in tracked source | None. Two false positives only: a `package-lock.json` integrity hash and the UI input's `placeholder="Optional note…"` attribute. PASS |
| Template leftovers / placeholder text | None in app code. PASS |
| Name guardrail: "FrameProof" in app/sample code | None — appears only in competition docs as the "NOT FrameProof" guardrail. PASS |
| C099 Cutline Studio reuse (code, assets, footage, text) | Zero matches for `cutline` / `C099` in app, scripts, mcp-server, sample-pack. PASS |
| Secrets / keys / tokens in tracked code | None. Grep hits are false positives only (`_tokens` function name; node_modules changelogs, untracked). PASS |
| `.kiro` at repo root, tracked, never gitignored | 11 files tracked; `git check-ignore .kiro` → not ignored. PASS |
| Licence file (MIT) at repo top, detectable | `LICENSE`, verified via GitHub API: `license: MIT`, `visibility: public`. PASS |
| Real client footage anywhere | None — sample pack is self-made (generator in `scripts/`). PASS |
| Dead code | Removed in round 1: unused `want_tokens`, inline `import math as _m`, dead logo=None branch. Re-grep clean. PASS |
| README accuracy | Fixed: quick-start now includes the frontend build step; "built bundle ships in the repo" corrected (dist is built by Docker / npm, not shipped). PASS |

## Built-artifact sweep

| Check | Result |
|---|---|
| Frontend `dist/` builds clean | `tsc -b && vite build`: 31 modules, `index.html` + CSS + JS (148.85 kB). PASS |
| Backend imports + serves | `/api/health` → `{"status":"ok","product":"BriefGate","version":"1.0.0"}`; frontend index 200; evidence frame 200. PASS |
| Sample run on the live server | `run-99b1e27d`, 38.1s, 3 blockers + 1 warning, all with frame URLs. PASS |
| Control run on the live server | `run-7e67e522`, 0 findings. PASS |
| PDF + JSON agree with on-screen decisions | Verified field-for-field after approve + dismiss. PDF 106,754 bytes, valid `%PDF-`, page 1 rendered and eyeballed. PASS |
| MCP server | initialize / tools/list / `probe_video` (real ffprobe: 90.047s, h264 1280×720 + aac) / `list_runs` (real SQLite run). PASS |
| Fresh clone | Separate clone, README-only steps, sample pack regenerated (90.047s / 90.040s), lint OK, 10/10 tests pass. PASS |

## Verdict

**SWEEP PASS** — no blocking item. The repo is public at
https://github.com/rsaxena3011/briefgate-kiroween (main, MIT, `/.kiro` at
root). Open non-blocking items live in the filing packet (live app URL,
demo video, Best Startup decision).
