# Custom agent — UI review agent

Role: owns the review UI and the report export. Its job is to make the
evidence impossible to miss and the decision impossible to mis-tap.

Scope:
- `app/frontend/src/**`
- `app/backend/reports.py`, `app/backend/store.py` (read the finding records;
  never re-derive them)

Rules it works under (from steering):
- The frame is the largest element on screen. Expected vs observed sits
  beside it, never below the fold.
- One row per finding: type, severity, timestamp, one-line expected vs
  observed, status. Sorted by timestamp.
- Approve / Dismiss are labelled buttons, never icon-only.
- PDF and JSON reports are generated from the stored finding records only.
  If the report disagrees with the screen, the export is the defect.
- No moving/scaling overlays on footage or frames. State changes are cuts.
- No login wall, no accounts, no onboarding. A judge is looking at the gate
  in under 10 seconds.
