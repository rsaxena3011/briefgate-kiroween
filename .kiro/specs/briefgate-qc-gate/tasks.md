# Spec — BriefGate QC gate: tasks

Status convention: `[ ]` open, `[x]` done with the commit / log that proves it.

## Slice 1 — repo + /.kiro foundation
- [x] Steering docs written before code (architecture, evidence-rule,
  design-system, testing-standards) — this commit.
- [x] Spec written before code (requirements, design, tasks) — this commit.
- [x] Hooks scaffold (tests-on-save, evidence-schema lint) — this commit.
- [x] MCP config + local probe server scaffold — this commit.
- [x] MIT licence, README skeleton, .gitignore (never .kiro) — this commit.
- [ ] Public GitHub repo created, first push (steering + specs only).

## Slice 2 — ingestion
- [ ] FastAPI skeleton serving the built frontend; SQLite store.
- [ ] Upload endpoint with limits + brief schema validation (Req 1, 2).
- [ ] Probe + shot detection + keyframe extraction (Req 3).
- [ ] Sample-pack generator: planted-defect video, clean control, brief,
      answer key, approved + wrong logos (Req 3, evidence rule).

## Slice 3 — checks
- [ ] Vision adapter interface + local OpenCV implementation (Req 4).
- [ ] Logo check with mismatch/absent distinction (Req 4).
- [ ] Missing-scene check with in-order alignment (Req 5).
- [ ] Technical QC: blackdetect, silencedetect, duration, stream errors
      (Req 6).
- [ ] Evidence-schema lint enforced on every finding (Req 7).

## Slice 4 — review + export + banked v1
- [ ] Findings list + evidence viewer + approve/dismiss + notes (Req 8).
- [ ] PDF + JSON export from stored records (Req 9).
- [ ] Full acceptance run on the sample pack vs ANSWER_KEY.json (Req 10).
- [ ] BANKED V1: public repo live, live URL (or honest blocker), demo cut
      plan + VO script ready for approval.

## Slice 5 — hardening (before filing)
- [ ] Review round 1 on banked v1 + fixes.
- [ ] Review round 2 on the fixed build + fixes.
- [ ] Submission sweep on source + built artifact.
- [ ] Filing packet with every Devpost field pre-filled and verified.
