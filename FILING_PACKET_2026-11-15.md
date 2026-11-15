# Filing packet — C119 Kiroween 2026 (BriefGate)

Prepared 2026-11-15 for a one-pass browser filing. Treat the submission as
FINAL and UNEDITABLE. Fill every field; verify each value against this packet
before AND after filing (standing submission-QC rule). Devpost:
https://kiroween.devpost.com/ — deadline Dec 5 2026 03:30 IST, target file
~Nov 24 IST. Submitter: Ratnesh Saxena, solo (Individual, organisation N/A).

## 1. Category + prizes

| Field | Value |
|---|---|
| Category | **Frankenstein** (locked 2026-10-31) |
| Bonus prizes to be considered for | **Best Demo ($1,000)** — yes. **Bonus Blog** — only if a build-story blog is published before filing (not yet; optional, needs boss go-ahead for a public post). **Social Blitz** — only if a #KiroweenHackathon26 post is published (not yet; optional). |
| Do NOT tick | Best Startup Project ($10,000) — **decision owed, default NO**. Vizoncraft Studio is unregistered; founder status cannot be claimed on a maybe. Only tick if the 2026 rules + boss confirm genuine eligibility. Best Ghost of Kiroween Past — no (not registered in 2025). Best Kiro Crew App — no. Best Student Project — no (not a student). |

## 2. URLs (verified)

| Field | Value | Verified |
|---|---|---|
| Public GitHub repo | https://github.com/rsaxena3011/briefgate-kiroween | Public, MIT licence detected, default branch `main`, `/.kiro` at root (11 files: steering, specs, hooks, agents, MCP settings — verified via GitHub API 2026-11-15) |
| Working app URL | **OWED — deploy pending.** Repo ships `Dockerfile` + `render.yaml` (Render free tier, no card). One command in the parent browser pass: create the Render Web Service from the repo (health check `/api/health`). The app runs locally at http://localhost:8000 (verified) and in Docker via the included Dockerfile. Do NOT file with a localhost URL. | Local run verified 2026-11-15 (sample run 38.1s, control run 0 findings). Public URL still owed. |
| Demo video (YouTube, public, under 3 min) | **OWED — video not yet built.** See DEMO_PLAN_2026-11-15.md. Upload to the **Strange Sightings** channel ONLY, public, after VO + very light music + boss approval of the final cut. | Not built. Do NOT file without it. |
| Login credentials for judges | None needed — no login wall, no accounts. State that in the form if it asks. | Verified: app opens straight into the gate. |

## 3. Text description (paste as-is; no em dashes)

> BriefGate is the brief-vs-final QC gate for video producers. Drop in a finished client video plus its written brief, and in under two minutes the gate returns every violation pinned to a timestamp with a screenshot of the actual frame. It runs three checks: a logo check that compares the visible logo in each required shot against the approved reference; a missing-scene check that matches the brief scene list, in order, against the detected shots; and deterministic technical QC via FFmpeg covering black frames, duration, silence, and corrupt streams. Every finding carries its evidence frame, and a human approves or dismisses each flag before a QC report exports as PDF and JSON. The gate reports; it never modifies the deliverable. Built with Kiro: steering docs written before code, spec-driven development, agent hooks, custom agents, and a local MCP server — all visible in /.kiro at the repo root. The demo uses self-made sample footage with planted defects: a wrong logo at 0:42, one absent scene, and a 3-second black segment, plus a clean control video that passes with zero findings.

## 4. How Kiro was used (write-up — paste as-is)

> Kiro was the development method, not an afterthought. Steering docs were written before any app code: architecture, the evidence rule (every finding carries a real extracted frame or the check returns not-checked), design system, and testing standards. Development was spec-driven from .kiro/specs/briefgate-qc-gate (requirements Req 1-10, design, tasks by slice), and the commit history shows the order: steering and specs first, app code second. Two agent hooks are defined in .kiro/hooks/hooks.json: tests run on save of any backend file, and an evidence-schema lint rejects any finding record missing its evidence fields (the lint is wired to the same validator the backend uses). Two custom agents carry the work: a media-processing agent that owns the video file, the checks, and the sample pack, and a UI review agent that owns the review UI and report export. A local MCP server (mcp-server/server.py, configured in .kiro/settings/mcp.json) exposes probe_video (ffprobe facts) and list_runs (the SQLite run store) so Kiro inspects real media facts during development instead of guessing. Kiro credits: 4,000 requested on Oct 31, no code issued as of Nov 15, so the build did not wait on credits; the /.kiro evidence in the repo was authored by hand with the project's own code tools in Kiro's spec-driven shape, and the dated log of every Kiro feature used is in KIRO_DEV_LOG.md. The Kiro Web free tier (50 credits/month) is the account on record.

## 5. Everything else the form may ask

- Team: solo. Members: Ratnesh Saxena only (rsaxena3011@gmail.com). Organisation: N/A.
- Licence: MIT (file at repo root, detected by GitHub).
- Built with: React + TypeScript frontend, Python + FastAPI backend, FFmpeg/FFprobe + OpenCV media engine, SQLite, reportlab. No paid services, no API keys, no card anywhere in the build.
- Limitations stated honestly (also in REVIEW_ROUNDS_2026-11-15.md): the logo check is a local OpenCV template-matching adapter (provider-swappable, no hosted vision model in v1); scene matching is colour-word based on the brief descriptions. Both are labelled in the repo.
- Sample inputs/outputs in the repo: `sample-pack/` (sample + control videos, brief, answer key, both logos).

## 6. Pre-filing checklist (do not file until all are green)

- [x] Repo public, MIT, /.kiro at root, never gitignored
- [x] Review rounds 1 (BLOCK → 8 defects fixed) + 2 (ALLOW) on file
- [x] Submission sweep PASS on source + built artifact
- [x] Fresh-clone run: 10/10 tests pass from README-only steps
- [ ] Live app URL (Render free tier from render.yaml) — OWED
- [ ] Demo video: VO + light music + boss approval + public YouTube upload (Strange Sightings) — OWED
- [ ] Best Startup eligibility decision (default NO) — OWED
- [ ] Bonus Blog post published (optional, needs boss go-ahead) — OWED if pursued
- [ ] Form double-check before + after filing; screenshot every step; capture submission URL + confirmation
