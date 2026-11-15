# Review rounds — BriefGate v1 (2026-11-15)

Two genuine review rounds on the banked v1, done by the build lead (Doom)
with measured evidence at every step. **Notion panel legs were not run in
this session** (blocked on the parent browser pass since Oct 30; recorded
honestly, never invented). Argon/GPT panel legs remain available to the
parent before filing if wanted — these two rounds do not claim to be them.

## Round 1 — adversarial review of banked v1 (2026-11-15, before fixes)

Scope: full spec (BUILD_SPEC_v1.md §9 acceptance criteria), API end to end,
evidence frames eyeballed, error paths, secrets/template sweep.

### What was verified with evidence
- **Acceptance run (pytest, 10 tests):** 10/10 pass on the sample pack —
  wrong logo caught at 42.24s (key: 43.0 ± 1.0s), missing scene s04 by id,
  black frame 60.0–63.0s measured 3.0s, silence 60.0–63.0s measured 3.0s,
  control video zero blockers, every finding opens a real extracted frame,
  run time 38.1s (< 120s), fresh clone 10/10 pass from README-only steps.
- **API end to end (live server, port 8000):** sample run `run-99b1e27d`
  (38.1s, 3 blockers + 1 warning), control run `run-7e67e522` (0 findings);
  approve/dismiss persist and summary counts update; PDF (106,754 bytes,
  valid `%PDF-`) and JSON exports agree with on-screen decisions field for
  field; frontend index 200; evidence frame URL 200.
- **Evidence frame eyeballed:** `logo-02-42s.png` shows the amber
  TESTIMONIAL scene with the wrong **NovaCorp** logo top-right — the anchor
  moment is real, not asserted.
- **PDF page 1 rendered and eyeballed:** header, run summary, approved
  logo_mismatch with its frame, dismissed silence with its black frame.
- **Error paths:** non-video upload → 400; malformed brief → 400 naming
  every failing field; decide on an unknown finding → 400.
- **Secrets/template sweep:** no secrets in tracked code (only false
  positives: `_tokens` function name, node_modules changelogs); no
  "FrameProof" in app code (only in competition docs as the guardrail);
  zero C099/Cutline reuse; `.kiro` tracked (11 files), not gitignored.

### Defects found (all fixed in this round)
1. **R1-1 — shot detection missed low-luma cuts.** ffmpeg `scene` (luma)
   merged the green→slate and slate→purple cuts; the control video then
   mis-flagged scene s05 as missing. Fixed: OpenCV colour-change detection
   (2 fps, RGB distance > 30); design.md corrected to match. Re-verified:
   7 shots in both videos.
2. **R1-2 — concat demuxer destroyed the silence plant.** `-c copy`
   concat misaligned AAC audio; the 60–63s black segment measured −21 dB
   tone and silencedetect found nothing. Fixed: concat filter with one
   re-encode; silence now measures 60.02–63.04s, 3.02s. Control: zero
   silence lines.
3. **R1-3 — false `logo_absent` on a black frame.** Shot boundaries are
   ±0.5s; a logo sample landing inside the black segment flagged a logo
   defect. Fixed: logo loop skips black frames (black is a technical
   defect, handled by that check).
4. **R1-4 — control video out of brief order.** s04 was placed after s05
   in the control timeline, so the in-order scene check correctly flagged
   it. Fixed: control rebuilt in brief order (s04 45–48s, s05 48–60s).
5. **R1-5 — fragile neighbour lookup.** `matched[scenes[len(matched)-1]]`
   raised KeyError when an earlier scene was missing. Fixed: explicit
   `last_matched_id` tracking.
6. **R1-6 — lint regex false-failed on nested parens.** Rewrote
   `lint_evidence.py` as AST + runtime checks. Lint now passes.
7. **R1-7 — sample-window overshoot.** Logo sampler tried t=90.0s, past
   the last frame. Fixed: clamp to duration − 0.1s.
8. **R1-8 — dead code + tracked build artifact.** Unused `want_tokens`,
   inline `import math as _m`, dead logo=None branch in the generator,
   `tsconfig.tsbuildinfo` tracked. All removed; README quick-start now
   includes the frontend build step (dist is not shipped in the repo).

### Honest limitations (not defects — recorded, not hidden)
- **L1 — local vision adapter.** Logo check is OpenCV template matching,
  not a hosted vision model. It is exact on crisp logos (measured: approved
  0.85–0.99, wrong 0.15–0.45) and the adapter is provider-swappable, but a
  rotated, partially occluded, or heavily graded logo in real footage may
  score lower. Labelled in code and in the filing packet.
- **L2 — colour-word scene matching.** Scenes match by colour word in the
  brief description vs measured dominant colour. Exact on the sample pack's
  distinct palette; two same-colour scenes in real footage would need the
  vision adapter. Labelled in the filing packet.
- **L3 — run time.** 38s for a 90s video (1 fps template matching). Under
  the 2-minute bar; not instant.
- **L4 — /tmp is 92% full** (512 MB tmpfs; other work's files, not this
  build's). pytest's tmp_path lives there — future runs should set TMPDIR
  to workspace. Noted for the parent; not a product defect.

Verdict round 1: **BLOCK** → all 8 defects fixed same session (above).

## Round 2 — re-review after fixes (2026-11-15)

- Lint: `evidence-schema lint: OK`.
- Full suite re-run: **10 passed in 78.14s**.
- Sample pack regenerated after the generator fix: identical durations
  (90.047s / 90.040s); unit tests 7/7 pass.
- Sweep re-run after fixes: no `node_modules`/`dist`/`.venv`/`runs` tracked;
  no TODO/FIXME/XXX in tracked source (2 false positives only: a lockfile
  hash and a UI input placeholder); no Cutline/C099 reuse; no FrameProof in
  app code; `.kiro` 11 files tracked, not ignored; `tsconfig.tsbuildinfo`
  removed from tracking.
- MCP server smoke-tested: initialize, tools/list, `probe_video` returns
  real ffprobe facts (90.047s, h264 1280×720 + aac), `list_runs` returns the
  real run from SQLite.
- Fresh-clone acceptance: separate clone, README-only steps, 10/10 pass.
- No open defect remains. The two standing v1 cuts (script/dialogue
  verification, wardrobe/prop/location continuity) stay cut per spec §8.

Verdict round 2: **ALLOW** — v1 is banked and submittable on the build side.
Filing still waits on: live app URL (deploy), demo video (VO + music + boss
approval + upload), Best Startup eligibility decision. See
FILING_PACKET_2026-11-15.md.

## Judge sim (self-score, /100 — scored at round 2)

| Pillar | Score | Why |
|---|---|---|
| Potential Impact | 16/20 | Real problem, real audience (production houses shipping client video daily); proof is sample-only, not a real client deployment. |
| Technological Implementation | 17/20 | Dense, genuine /.kiro evidence (steering before code, specs, 2 hooks, 2 agents, local MCP); docked for the local vision adapter vs a hosted model, and Kiro credits never issued. |
| Design | 15/20 | Clean evidence-first UI, no login wall, judge is at the gate in seconds; single-page utilitarian, no drag-and-drop. |
| Innovation / Idea | 16/20 | Frankenstein fusion is real (FFmpeg + OpenCV + spec-driven agent workflow around one evidence rule); the QC-gate concept itself is a known idea, executed with unusual rigour. |
| Presentation | 14/20 | Writeup, README, and sample evidence are strong; the demo video is not yet built, so this is scored on the plan, not the cut. |
| **Total** | **78/100** | The video is the biggest open swing: a clean sub-3-minute cut with the anchor in the first 10 seconds is worth the most remaining points. |
