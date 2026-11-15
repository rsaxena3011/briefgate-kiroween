# BUILD SPEC v1: C119 Kiroween brief-vs-final video QC gate

Status: v1 slice definition, written 2026-11-01, before any code. Category: Frankenstein (locked 2026-10-31, see CATEGORY_DECISION_2026-10-31.md). Product name: to be chosen at build start with boss approval. The name is NOT "FrameProof" (owned by the C056 OpenCV entry). Zero code or asset reuse from C099 Cutline Studio; everything here is built fresh inside the Kiroween window.

## 1. The v1 slice in one line

One sample client video plus one structured brief goes in; the gate runs three checks (logo, missing scene, technical QC); every flag comes back with a timestamp and a screenshot of the actual frame; a human approves or dismisses each flag; a QC report exports as PDF and JSON.

This is the smallest end-to-end slice that demos the anchor moment: the gate catches the wrong logo at 0:43 with screenshot evidence before the client ever sees the video.

## 2. What v1 does, step by step

1. Create a run: upload one video file and one brief file, plus the approved logo reference image named in the brief.
2. Ingest: probe the video (duration, resolution, streams), detect shot boundaries, extract one keyframe per shot plus frames at every logo-candidate moment.
3. Check: run the three v1 checks (section 4) against the brief. Each check produces findings or an explicit "not checked" state, never a silent pass.
4. Review: the reviewer sees a findings list. Each finding opens an evidence view: the extracted frame, the timestamp, what was expected, what was observed, and a confidence value.
5. Decide: the reviewer marks each finding approved (a real defect) or dismissed (a false alarm), with an optional note.
6. Export: one QC report per run, PDF for humans and JSON for the audit trail, containing only decided findings plus the run summary.

## 3. Input contracts

### 3.1 Video input
- One file per run: .mp4 or .mov, H.264 or H.265, maximum 3 minutes, maximum 500 MB (v1 limits; larger inputs are rejected with a plain message, not truncated).
- The video is treated as the final client deliverable. It is never edited, re-encoded for the client, or uploaded anywhere by the tool.

### 3.2 Brief input (JSON, UTF-8)
Required fields:
- `project`: string, project or client name used in the report header.
- `expected_duration_s`: number, with `duration_tolerance_s` (default 2).
- `scenes`: ordered array of `{ "id": string, "description": string }`. The description is what the vision check matches against detected shots.
- `brand`: `{ "logo_ref": string (path to the approved logo image supplied with the brief), "logo_required_in": array of scene ids, or "all" }`.
- `technical`: `{ "max_black_frame_s": number (default 0.5), "max_silence_s": number (default 2.0) }`.

A brief that fails schema validation is rejected before the run starts, with the failing field named. No partial runs on a malformed brief.

### 3.3 Reference assets
- The approved logo as a PNG with transparency or a clean background, supplied per brief.
- Sample pack for development and acceptance: self-made footage only (no real client footage, ever). One sample video of about 90 seconds with planted defects and a written answer key:
  - a wrong logo shown at a known timestamp (the 0:43 case used in the demo),
  - one brief scene that is absent from the video,
  - one black-frame segment longer than the brief allows,
  - one clean control video with no planted defects.

## 4. The three v1 checks

1. **Logo check.** For each shot in scope (`logo_required_in`), compare the visible logo in keyframes against the approved reference using the vision model. Flag a mismatch or an absent logo. Evidence: the frame at the flagged timestamp plus the approved reference image, side by side.
2. **Missing-scene check.** Match the brief scene list, in order, against detected shots (shot boundaries plus a vision description per shot). Flag any brief scene with no matching shot. Evidence: the brief scene text plus the frames of the neighbouring matched shots, so the reviewer can see the gap.
3. **Technical QC (deterministic, no model).** FFmpeg-based: black-frame segments longer than `max_black_frame_s`, total duration outside tolerance, silence segments longer than `max_silence_s`, unreadable or corrupt streams. Evidence: frame at the segment midpoint for visual defects; measured values for the rest.

Explicitly the whole of v1. GPT's brainstorm proposed five capabilities; v1 ships three and cuts two (see section 8).

## 5. Evidence format (the product's core rule)

Every finding is one record:

```json
{
  "finding_id": "run-id + sequence",
  "type": "logo_mismatch | logo_absent | scene_missing | black_frame | duration_mismatch | silence | stream_error",
  "severity": "blocker | warning",
  "timestamp_in_s": 43.0,
  "timestamp_out_s": 45.5,
  "frame_image": "path to the frame extracted from the submitted video",
  "expected": "what the brief requires, quoted from the brief",
  "observed": "what the check actually saw, in plain words",
  "confidence": 0.0,
  "status": "open | approved | dismissed",
  "reviewer_note": "optional"
}
```

Rules that no version may break:
- The frame image is always extracted from the actual submitted video at the stated timestamp (tolerance plus or minus 1 second). Frames are never generated, stock, or illustrative.
- A check that cannot produce evidence returns `not_checked` for its scope. It never reports a pass it did not verify.
- No finding may invent a timestamp, a quote from the brief, or an observation. The same rule is written into the /.kiro steering docs, so the build agent works under it too.
- Scene-missing findings carry neighbouring-shot frames as evidence because the defect is an absence; the record states that plainly instead of faking a frame of a scene that does not exist.

## 6. Output contracts

- **Findings list (UI):** one row per finding: type, severity, timestamp, one-line expected vs observed, status. Sorted by timestamp.
- **Evidence view (UI):** frame image large, reference or brief text beside it, confidence, approve and dismiss actions, note field.
- **Report (PDF):** project header, run summary (video name, duration, checks run, counts by status), one section per approved finding with its frame and timestamps, dismissed findings listed in an appendix with their notes.
- **Report (JSON):** the full finding records plus run metadata, exactly as stored. This is the audit trail.
- **Run store:** one record per run (SQLite): inputs by hash, brief as submitted, findings, decisions, export paths. Re-running the same video and brief creates a new run; runs are never overwritten.

## 7. Shape of the build (fresh code, Kiro-driven)

- Front end: React + TypeScript, single-user, local-first, no accounts and no login wall.
- Back end: Python + FastAPI. Media engine: FFmpeg / FFprobe + OpenCV. Vision model behind a provider-swappable adapter (provider chosen at build start; no provider is hard-coded into check logic).
- /.kiro from day one: steering docs written before code (architecture, design system, testing standards, the evidence rule of section 5), specs per slice (requirements, design, tasks), and 2 to 3 agent hooks (tests on save; a lint that rejects any finding record missing its evidence fields).
- The repo is public from slice 1 with /.kiro at the root, never gitignored.

## 8. Out of scope for v1 (explicit)

- Script and dialogue verification (no transcription, no line matching). Cut from the brainstorm's five capabilities; candidate for v2 only after v1 banks.
- Visual continuity checks: wardrobe, props, location consistency across shots. Cut for v1, same reason.
- Loudness-standard compliance (broadcast LUFS targets) beyond silence and corrupt-stream detection.
- More than one video per run; batch queues; multiple projects or clients.
- User accounts, roles, cloud storage, hosted rendering, payments.
- Editing or fixing the video. The gate reports; it never modifies the deliverable.
- MCP integration, unless a genuine use appears during the build (never as decoration).
- Mobile apps, and any theming beyond a clean review UI.
- Real client footage in development, testing, or the demo. Sample assets only.
- Any code, assets, footage, or text from C099 Cutline Studio or any other prior entry.

## 9. Acceptance criteria for banked v1

All must hold on the sample pack, measured, not asserted:
1. The wrong-logo plant is caught and its evidence frame matches the stated timestamp within 1 second.
2. The missing-scene plant is caught and identified by its brief scene id.
3. The black-frame plant is caught with measured duration stated.
4. The clean control video produces zero blocker findings.
5. Every finding in the run opens its evidence view with a real extracted frame.
6. PDF and JSON reports export and agree with the on-screen decisions.
7. Full run on the 90-second sample completes in under 2 minutes on the build machine.
8. A fresh clone of the public repo runs the sample end to end from its own instructions.

## 10. Risks and dependencies

- Vision-model reliability on the logo check is the anchor risk. Mitigation and pivot are in the WIN CARD kill criteria (pivot the anchor to the deterministic checks by Nov 14 if the logo check will not hold).
- Kiro credit supply: 4,000 credits requested, none issued yet; free tier is 50 per month. Scope discipline in the WIN CARD assumes credits stay tight.
- The exact Devpost video and live-URL requirements are confirmed at the day-one live recon (WIN CARD section 3) before the demo is produced.
