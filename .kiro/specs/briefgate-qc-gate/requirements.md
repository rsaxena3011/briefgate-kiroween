# Spec — BriefGate QC gate: requirements

## Introduction

BriefGate is a brief-vs-final video QC gate for video producers. A finished
client video plus its written brief goes in; three checks run; every flag
carries a timestamp and a screenshot of the actual frame; a human approves or
dismisses each flag; a QC report exports as PDF + JSON.

## Requirements

### Req 1 — Run creation
The system SHALL accept one video file (.mp4/.mov, H.264/H.265, ≤3 min,
≤500 MB), one brief JSON file, and one approved logo PNG per run, and SHALL
reject inputs outside those limits with a plain message.
- Acceptance: oversized / wrong-format / over-length input is rejected before
  any check runs; the rejection names the limit breached.

### Req 2 — Brief schema
The brief SHALL validate against the schema in BUILD_SPEC_v1.md §3.2
(`project`, `expected_duration_s`, `duration_tolerance_s`,
`scenes[] {id, description}`, `brand {logo_ref, logo_required_in}`,
`technical {max_black_frame_s, max_silence_s}`).
- Acceptance: a malformed brief is rejected before the run starts with the
  failing field named; no partial run is created.

### Req 3 — Ingestion
The system SHALL probe the video (duration, resolution, streams), detect shot
boundaries, and extract one keyframe per shot plus frames at logo-candidate
moments, storing a run record.
- Acceptance: a 90-second sample yields ≥1 shot per scene change and a
  keyframe whose timestamp is within 1s of its shot midpoint.

### Req 4 — Logo check
For each shot in `logo_required_in`, the system SHALL compare the visible logo
in keyframes against the approved reference via the vision adapter and SHALL
flag a mismatch or an absent logo with the frame beside the reference.
- Acceptance: the planted wrong-logo case at 0:43 is flagged as
  `logo_mismatch` with an evidence frame within 1s of 43.0s.

### Req 5 — Missing-scene check
The system SHALL match the brief scene list, in order, against detected shots
and SHALL flag any brief scene with no matching shot, carrying neighbouring
shot frames as evidence.
- Acceptance: the planted absent scene is flagged as `scene_missing` with the
  correct brief scene id.

### Req 6 — Technical QC (deterministic)
The system SHALL detect, via FFmpeg, black-frame segments longer than
`max_black_frame_s`, total duration outside tolerance, silence segments longer
than `max_silence_s`, and unreadable/corrupt streams — with measured values.
- Acceptance: the planted black segment is flagged with its measured
  duration; the clean control produces zero blocker findings.

### Req 7 — Evidence rule
Every finding SHALL conform to the evidence record in
`.kiro/steering/evidence-rule.md`. A check that cannot produce evidence SHALL
return `not_checked` for its scope, never a silent pass.
- Acceptance: the evidence-schema lint hook rejects any finding record
  missing its evidence fields.

### Req 8 — Review
The reviewer SHALL see a findings list and an evidence view per finding, and
SHALL mark each finding approved or dismissed with an optional note.
- Acceptance: a decision persists across reload; a dismissed finding appears
  in the report appendix with its note.

### Req 9 — Export
The system SHALL export one QC report per run as PDF (humans) and JSON (audit
trail), containing only decided findings plus the run summary, generated from
the stored records.
- Acceptance: PDF and JSON agree with the on-screen decisions on the sample
  run, field for field.

### Req 10 — Performance + fresh clone
A full run on the 90-second sample SHALL complete in under 2 minutes, and a
fresh clone SHALL run the sample end to end from the README alone.
- Acceptance: timed run log + fresh-clone run log, both quoted in the review
  rounds.
