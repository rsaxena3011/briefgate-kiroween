# Steering — Design System

Product: BriefGate. Audience: a video producer doing the last QC pass before
a client delivery. The UI has one job: show what is wrong, with proof, and
let a human decide.

## Principles

- Evidence first: the frame is the largest element on screen, not the text.
- One row per finding: type, severity, timestamp, one-line expected vs
  observed, status. Sorted by timestamp.
- Dark review-room theme (near-black background, warm amber accent for
  blockers, muted teal for warnings) — a light "Costume Contest" skin was
  explicitly cut for v1; the UI is clean, not themed.
- No login wall, no accounts, no onboarding tour. A judge opens the URL and
  is looking at the gate in under 10 seconds.
- Every action is labelled in plain words: Approve, Dismiss, Export PDF,
  Export JSON. No jargon, no icons without labels.

## Layout

- Header: product name, run id, video name, duration.
- Left: findings list (scrollable). Right: evidence viewer — frame large,
  approved reference / brief text beside it, confidence, approve + dismiss,
  note field.
- Footer: run summary (checks run, counts by status), export buttons.
- Colours: background #0e0f12, panel #17181d, text #e8e6e1, accent amber
  #f5a524 (blocker), teal #2dd4bf (warning / ok), muted #8a8f98.
- Type: system sans stack; timestamps and durations in tabular numerals.

## Motion

- No moving/scaling overlays on footage or frames. Findings appear on a cut.
- Transitions, if any, are instant state changes, not animations that hide
  content.
