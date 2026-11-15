# Kiro dev log — BriefGate (C119 Kiroween 2026)

A dated, honest record of how Kiro was used to build this entry. This log is
the raw material for the Devpost "how Kiro was used" write-up. Kiro credits:
4,000 requested 2026-10-31, no code issued as of 2026-11-15; the build does
not wait on credits. Kiro Web free tier (50 credits/month) is the account on
record. The `/.kiro` evidence in this repo was authored by hand with the
project's own code tools, in the Kiro spec-driven shape (steering → specs →
tasks → hooks → agents → MCP), because no credit code had landed; nothing
here claims a Kiro run that did not happen.

## 2026-11-15 — Slice 1: foundation (before any app code)
- Steering docs written BEFORE code: `architecture.md`, `evidence-rule.md`,
  `design-system.md`, `testing-standards.md`. The evidence rule (every
  finding carries a real extracted frame or the check returns `not_checked`)
  is the steering rule the whole build works under.
- Spec-driven development: `.kiro/specs/briefgate-qc-gate/` —
  `requirements.md` (Req 1–10), `design.md` (pipeline, checks, data model),
  `tasks.md` (slices 1–5 with status boxes). No app code was written before
  these files existed; the slice order in tasks.md is the order commits land.
- Agent hooks (`.kiro/hooks/hooks.json`): (1) `run-tests-on-save` — pytest
  on save of any `app/backend/**/*.py`; (2) `evidence-schema-lint` — rejects
  any finding record missing its evidence fields (script
  `scripts/lint_evidence.py`, wired to the same validator the backend uses).
- Custom agents (`.kiro/agents/`): `media-processing-agent.md` (owns the
  video file, the checks, the sample pack) and `ui-review-agent.md` (owns the
  review UI and report export). Each carries its scope and the steering rules
  it works under.
- MCP (`.kiro/settings/mcp.json` + `mcp-server/server.py`): local stdio MCP
  server with two genuine tools — `probe_video` (ffprobe facts) and
  `list_runs` (SQLite run store) — so Kiro inspects real media facts during
  development instead of guessing durations, codecs, or shot counts.
- No Kiro IDE/CLI/Crew run was available in this build session (no credit
  code issued, no Kiro CLI in the VM); the spec/steering/hook/agent/MCP
  artefacts above are the Kiro usage evidence, authored in Kiro's own shape
  and verified by the tests and the lint hook, not by a Kiro session log.

## 2026-11-15 — Slices 2–4: build (spec → code, in slice order)
- Ingestion (FastAPI + SQLite, upload limits, brief schema validation,
  probe + OpenCV colour-change shot detection + keyframes) and the three
  checks (logo via the local OpenCV vision adapter, missing-scene via
  in-order colour alignment, technical QC via FFmpeg) landed in slice
  order per tasks.md, commits cdcb1ac → 0fc679d.
- The spec itself was corrected twice from measured evidence, which is what
  spec-driven development is for: (1) shot detection moved from ffmpeg
  `scene` to OpenCV colour-change after the luma score missed the
  green→slate and slate→purple cuts; (2) the sample-pack concat moved from
  the demuxer (`-c copy`, which destroyed the silence plant) to the concat
  filter with one re-encode. Both corrections are recorded in design.md and
  in REVIEW_ROUNDS_2026-11-15.md.
- Hooks fired as designed: the evidence-schema lint (rewritten AST +
  runtime after its regex version false-failed) passes
  (`evidence-schema lint: OK`); the test suite passes 10/10, including the
  full pipeline acceptance run against ANSWER_KEY.json.
- MCP smoke-tested end to end: `probe_video` returned real ffprobe facts
  (90.047s, h264 1280×720 + aac) and `list_runs` returned the real run
  (`run-99b1e27d`) from the SQLite store.
- Public repo: https://github.com/rsaxena3011/briefgate-kiroween (main,
  public, MIT licence detected, `/.kiro` at root verified via GitHub API).
- Kiro credits: still unissued as of end of build (requested Oct 31). The
  build never waited on them; nothing in the repo claims a Kiro run that
  did not happen.
