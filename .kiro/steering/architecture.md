# Steering — Architecture

Product: **BriefGate** (C119 Kiroween 2026, Frankenstein category).
One-line: a finished client video plus its written brief goes in; the gate runs
three checks (logo, missing scene, technical QC) and returns every flag with a
timestamp and a screenshot of the actual frame; a human approves or dismisses
each flag; a QC report exports as PDF + JSON.

## Stack (locked for v1)

- Front end: React + TypeScript (Vite), single-user, local-first, no accounts,
  no login wall. The built bundle is served by the backend so the product is
  one deployable service with one URL.
- Back end: Python 3.12 + FastAPI. SQLite run store (one record per run).
- Media engine: FFmpeg / FFprobe (probe, shot boundaries, keyframes,
  blackframe + silence detection) + OpenCV (logo template matching, dominant
  colour per shot).
- Vision: provider-swappable adapter (`backend/vision.py`). v1 ships the local
  adapter only: OpenCV template matching against the approved logo reference
  plus a badge-presence test in the logo zone. No provider is hard-coded into
  check logic; no API key is required to run v1; no paid call is made.
- Reports: reportlab PDF + JSON audit trail, generated from the same stored
  finding records the UI shows (one source of truth, no re-computation).

## Module boundaries

- `backend/main.py` — HTTP API only: upload, run, review, export. No media
  logic here.
- `backend/media.py` — FFmpeg/FFprobe wrappers: probe, shots, keyframes,
  blackdetect, silencedetect. Returns plain data, never findings.
- `backend/checks.py` — the three v1 checks. Each check takes media facts +
  the brief and returns finding records or an explicit `not_checked` scope.
- `backend/vision.py` — the vision adapter interface + local implementation.
- `backend/store.py` — SQLite: runs, findings, decisions, export paths.
- `backend/reports.py` — PDF + JSON export from stored records.
- `backend/evidence.py` — the evidence rule (see steering/evidence-rule.md):
  every finding must carry a real extracted frame or state `not_checked`.

## Rules

1. The gate reports; it never modifies the deliverable. No re-encode for the
   client, no edit, no upload anywhere.
2. One video per run. Re-running the same inputs creates a new run; runs are
   never overwritten.
3. A brief that fails schema validation is rejected before the run starts,
   with the failing field named. No partial runs on a malformed brief.
4. Deterministic checks (technical QC) never depend on the vision adapter.
5. No secrets, no API keys, no credentials in the repo. The app runs with
   zero configuration on a fresh clone.
