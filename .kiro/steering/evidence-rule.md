# Steering — Evidence Rule (the product's core rule)

This rule governs the product AND the build agent working on it. It is the
one rule no version may break.

1. Every finding is one record with: `finding_id`, `type`, `severity`,
   `timestamp_in_s`, `timestamp_out_s`, `frame_image`, `expected` (quoted from
   the brief), `observed` (plain words), `confidence`, `status`
   (`open | approved | dismissed`), `reviewer_note` (optional).
2. The frame image is ALWAYS extracted from the actual submitted video at the
   stated timestamp (tolerance ±1 second). Frames are never generated, stock,
   or illustrative.
3. A check that cannot produce evidence returns `not_checked` for its scope.
   It never reports a pass it did not verify.
4. No finding may invent a timestamp, a quote from the brief, or an
   observation.
5. Scene-missing findings carry neighbouring-shot frames as evidence, because
   the defect is an absence. The record states that plainly instead of faking
   a frame of a scene that does not exist.
6. Finding types (v1): `logo_mismatch | logo_absent | scene_missing |
   black_frame | duration_mismatch | silence | stream_error`.
7. The PDF and JSON reports are generated from the stored finding records
   only. A report must agree with the on-screen decisions; if it does not,
   the export is a defect, not a rounding difference.

## Build-agent corollary

- Sample footage is self-made only (no real client footage, ever). Planted
  defects have a written answer key; a check is only "working" when it
  catches the planted defect AND the answer key agrees on timestamp (±1s),
  type, and scene id.
- A test that asserts on a fixture the code itself generated is not evidence.
  Acceptance runs use the sample pack in `sample-pack/` and the answer key in
  `sample-pack/ANSWER_KEY.json`.
- Never claim a detection the run log does not show.
