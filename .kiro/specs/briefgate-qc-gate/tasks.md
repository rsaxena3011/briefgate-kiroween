# Spec — BriefGate QC gate: tasks

Status convention: `[ ]` open, `[x]` done with the commit / log that proves it.

## Slice 1 — repo + /.kiro foundation
- [x] Steering docs written before code (architecture, evidence-rule,
  design-system, testing-standards) — commit 0fba197.
- [x] Spec written before code (requirements, design, tasks) — commit 0fba197.
- [x] Hooks scaffold (tests-on-save, evidence-schema lint) — commit 0fba197.
- [x] MCP config + local probe server scaffold — commit 0fba197.
- [x] MIT licence, README skeleton, .gitignore (never .kiro) — commit 0fba197.
- [x] Public GitHub repo created, first push — https://github.com/rsaxena3011/briefgate-kiroween (main, public, MIT).

## Slice 2 — ingestion
- [x] FastAPI skeleton serving the built frontend; SQLite store — commit cdcb1ac.
- [x] Upload endpoint with limits + brief schema validation (Req 1, 2) — commit cdcb1ac.
- [x] Probe + shot detection + keyframe extraction (Req 3) — commit cdcb1ac. Note: shot detection moved from ffmpeg `scene` (luma, missed low-luma cuts) to OpenCV colour-change detection; design.md corrected.
- [x] Sample-pack generator: planted-defect video, clean control, brief, answer key, approved + wrong logos — commit cdcb1ac. Note: concat fixed to the concat filter (demuxer + `-c copy` destroyed the silence plant).

## Slice 3 — checks
- [x] Vision adapter interface + local OpenCV implementation (Req 4) — commit cdcb1ac.
- [x] Logo check with mismatch/absent distinction (Req 4) — commit cdcb1ac. Note: logo loop skips black frames (a black frame is a technical defect, not a logo defect).
- [x] Missing-scene check with in-order alignment (Req 5) — commit cdcb1ac. Note: control video rebuilt in brief order; neighbour-lookup fragility fixed with `last_matched_id`.
- [x] Technical QC: blackdetect, silencedetect, duration, stream errors (Req 6) — commit cdcb1ac.
- [x] Evidence-schema lint enforced on every finding (Req 7) — lint rewritten AST + runtime; `evidence-schema lint: OK`.

## Slice 4 — review + export + banked v1
- [x] Findings list + evidence viewer + approve/dismiss + notes (Req 8) — commit 0fc679d (React + TypeScript).
- [x] PDF + JSON export from stored records (Req 9) — commit 0fc679d. Verified: PDF 106,754 bytes, page 1 eyeballed, JSON agrees with screen field for field.
- [x] Full acceptance run on the sample pack vs ANSWER_KEY.json (Req 10) — 10/10 tests pass; live API run 38.1s (< 120s); control 0 findings; fresh clone 10/10 pass.
- [x] BANKED V1: public repo live. Live app URL still owed (deploy — Dockerfile + render.yaml ready); demo cut plan + VO script in DEMO_PLAN_2026-11-15.md.

## Slice 5 — hardening (before filing)
- [x] Review round 1 on banked v1 + fixes — REVIEW_ROUNDS_2026-11-15.md (BLOCK → 8 defects fixed).
- [x] Review round 2 on the fixed build + fixes — REVIEW_ROUNDS_2026-11-15.md (ALLOW). Judge sim self-score 78/100.
- [x] Submission sweep on source + built artifact — SWEEP_REPORT_2026-11-15.md (PASS).
- [x] Filing packet with every Devpost field pre-filled and verified — FILING_PACKET_2026-11-15.md.
- [ ] Live app URL (Render free tier) — owed, parent browser pass.
- [ ] Demo video (VO + light music + boss approval + upload) — owed, see DEMO_PLAN_2026-11-15.md.
- [ ] Best Startup eligibility decision (default NO) — owed at filing.
