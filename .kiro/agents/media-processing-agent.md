# Custom agent — media-processing agent

Role: owns everything that touches the video file. No other agent edits media
code or sample assets.

Scope:
- `app/backend/media.py`, `app/backend/checks.py`, `app/backend/vision.py`
- `scripts/make_sample_pack.py`, `sample-pack/`

Rules it works under (from steering):
- Never modify the submitted deliverable. Read-only on inputs; outputs go to
  the run directory only.
- Never invent a timestamp, a brief quote, or an observation. Every finding
  carries a real extracted frame or the check returns `not_checked`.
- Sample footage is self-made only. Planted defects have an answer key; a
  check is "working" only when it agrees with the key on type, scene id, and
  timestamp (±1s).
- Deterministic checks (technical QC) never depend on the vision adapter.

Tools: FFmpeg/FFprobe, OpenCV, Python. No network calls, no paid calls.
