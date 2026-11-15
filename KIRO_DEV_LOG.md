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
