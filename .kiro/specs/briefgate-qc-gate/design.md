# Spec — BriefGate QC gate: design

## Architecture

Single deployable service. FastAPI backend serves the API and the built React
bundle. SQLite run store. Media engine: FFmpeg/FFprobe + OpenCV. Vision
behind a provider-swappable adapter (`vision.py`); v1 ships the local adapter
(OpenCV template matching + badge-presence test). No API key, no paid call.

```
browser ──► FastAPI (main.py) ──► checks.py ──► media.py (ffmpeg/ffprobe)
                                  │               └─► vision.py (local adapter)
                                  └─► store.py (SQLite) ──► reports.py (PDF/JSON)
```

## Ingestion pipeline

1. Upload → validate limits (Req 1) → validate brief schema (Req 2) →
   create run record (inputs stored by SHA-256 hash).
2. `ffprobe`: duration, resolution, streams. Unreadable stream → `stream_error`.
3. Shot boundaries: `ffmpeg -vf select='gt(scene,0.30)',showinfo` — one shot
   per scene change; keyframe = midpoint frame of each shot, extracted as PNG.
4. Logo-candidate frames: one frame per second inside logo-required shots,
   plus the exact midpoint, so the 0:43 plant is sampled.

## Checks

### Logo check (`checks.logo_check`)
- For each logo-required shot, run the vision adapter on its keyframes:
  `matchTemplate` (normalised cross-correlation) of the approved logo at
  scales 0.5–1.5 against the frame, best score kept.
- Score ≥ 0.55 → logo present. Score < 0.55 → test the logo zone (top-right
  30% × 20%): high edge density + a bounded high-contrast region means a
  badge is present but is NOT the approved logo → `logo_mismatch`;
  no badge → `logo_absent`.
- Evidence: the keyframe at the flagged timestamp + the approved reference,
  side by side in the UI. Confidence = 1 − best score for mismatches.

### Missing-scene check (`checks.scene_check`)
- Per shot, compute an auto-description: dominant colour name (nearest of a
  fixed palette: navy, teal, amber, green, purple, crimson, slate, gold) +
  logo presence + shot index.
- Greedy in-order alignment of brief scenes to shots: a scene matches a shot
  when a colour word in its description equals the shot's dominant colour, or
  when a content keyword overlaps the shot description. Scenes are consumed in
  order; a scene with no matching shot is `scene_missing`.
- Evidence: brief scene text + frames of the neighbouring matched shots, with
  the record stating the defect is an absence.

### Technical QC (`checks.technical_check`)
- `blackdetect` (picture black ratio 0.98, min duration = `max_black_frame_s`)
  → `black_frame` with measured duration, evidence frame at segment midpoint.
- `silencedetect` (noise −50 dB, min duration = `max_silence_s`) → `silence`
  with measured duration. No audio stream → `not_checked` (silence scope),
  stated in the run summary.
- Duration vs `expected_duration_s ± tolerance` → `duration_mismatch`.
- ffprobe failure → `stream_error`, run stops, no findings invented.

## Data model (SQLite)

- `runs(id, created_at, video_name, video_sha256, brief_json, status,
  duration_s, checks_run_json, summary_json)`
- `findings(id, run_id, finding_id, type, severity, timestamp_in_s,
  timestamp_out_s, frame_path, expected, observed, confidence, status,
  reviewer_note)`
- `not_checked(run_id, scope, reason)`

## UI

React + TypeScript, single page: upload panel → run progress → findings list
(left) + evidence viewer (right) → approve/dismiss + note → export PDF/JSON.
Dark review-room theme per steering/design-system.md. No login wall.

## Out of scope (v1)

Script/dialogue verification, wardrobe/prop/location continuity, LUFS
loudness, batch runs, accounts, editing the video, MCP beyond the probe tool
(see `.kiro/settings/mcp.json`).
