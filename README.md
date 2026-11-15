# BriefGate — the brief-vs-final QC gate

> The brief is the truth. The video has to prove it.

**BriefGate** takes a finished client video plus its written brief and produces
a QC verdict in which every violation is pinned to a timestamp with screenshot
evidence — in under two minutes. A wrong logo or a missing scene never reaches
the client again.

Built for **Kiroween 2026** (Devpost, Frankenstein category). Built with Kiro:
steering docs written before code, spec-driven development, agent hooks, a
local MCP server — see [`.kiro/`](.kiro/) (never gitignored; judges inspect it).

## The anchor moment

Drop in a client video and its brief. In the first 10 seconds the gate flags
the **wrong logo at 0:43** — the actual frame on screen beside the approved
logo — before any human has watched the video through.

## What it checks (v1)

1. **Logo check** — visible logo in each required shot vs the approved
   reference (OpenCV template matching + badge-presence test). Mismatch or
   absent, with the frame beside the reference.
2. **Missing-scene check** — brief scenes, in order, matched against detected
   shots. A scene with no matching shot is flagged with neighbouring-shot
   frames as evidence (the defect is an absence; the record says so).
3. **Technical QC (deterministic, FFmpeg)** — black-frame segments, duration
   outside tolerance, silence segments, unreadable/corrupt streams. Measured
   values, never guesses.

Every finding carries a timestamp and a screenshot of the actual frame. A
human approves or dismisses each flag. A QC report exports as **PDF + JSON**.

## Quick start (fresh clone)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/make_sample_pack.py   # self-made sample footage only
.venv/bin/uvicorn app.backend.main:app --port 8000
# open http://localhost:8000 — upload sample-pack/sample_video.mp4 +
# sample-pack/brief.json + sample-pack/approved_logo.png
```

## Deploy (one URL, no login wall)

```bash
docker build -t briefgate . && docker run -p 8000:8000 briefgate
# or on Render's free tier: create the Web Service from this repo —
# render.yaml points at the Dockerfile (health check: /api/health)
```

Requirements: Python 3.12, FFmpeg 6+ (`ffmpeg`, `ffprobe` on PATH), Node 20+
(only to rebuild the frontend; the built bundle ships in the repo).

## Sample pack

`sample-pack/` holds self-made footage only — no real client footage, ever.
One 90-second video with planted defects (wrong logo at 0:43, one absent
scene, one over-long black-frame segment) plus a clean control video, a brief,
and `ANSWER_KEY.json`. The acceptance run scores the gate against that key.

## Repo map

- `app/backend/` — FastAPI service: upload, probe, checks, review, export
- `app/frontend/` — React + TypeScript review UI (built bundle served by backend)
- `.kiro/` — steering docs, specs, hooks, agents, MCP config (the Kiro evidence)
- `mcp-server/` — local MCP server: `probe_video`, `list_runs`
- `scripts/` — sample-pack generator, evidence-schema lint
- `sample-pack/` — self-made test footage + brief + answer key

## Kiro usage

See [`KIRO_DEV_LOG.md`](KIRO_DEV_LOG.md) — a dated log of every Kiro feature
used (steering, specs, hooks, agents, MCP), kept as the build runs.

## Licence

MIT — see [LICENSE](LICENSE).
