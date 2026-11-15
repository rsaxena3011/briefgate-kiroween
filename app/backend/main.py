"""BriefGate API — upload, run, review, export. Serves the built React
frontend so the product is one deployable service with one URL.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import checks, media, reports, store

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
RUNS_DIR = ROOT / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)
DB = RUNS_DIR / "briefgate.db"
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

MAX_VIDEO_BYTES = 500 * 1024 * 1024
MAX_VIDEO_S = 180
ALLOWED_EXT = {".mp4", ".mov"}

app = FastAPI(title="BriefGate", version="1.0.0")


def _con():
    return store.connect(DB)


@app.get("/api/health")
def health():
    return {"status": "ok", "product": "BriefGate", "version": "1.0.0"}


@app.post("/api/runs")
async def create_run(video: UploadFile = File(...),
                     brief: UploadFile = File(...),
                     logo: UploadFile = File(...)):
    started = time.time()
    ext = Path(video.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"video must be .mp4 or .mov, got '{ext}'")
    try:
        brief_data = json.loads((await brief.read()).decode("utf-8"))
    except Exception as e:
        raise HTTPException(400, f"brief is not valid JSON: {e}")
    errs = checks.validate_brief(brief_data)
    if errs:
        raise HTTPException(400, "brief failed validation: " + "; ".join(errs))

    run_id = f"run-{uuid.uuid4().hex[:8]}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    video_path = run_dir / f"input{ext}"
    logo_path = run_dir / "logo_ref.png"
    data = await video.read()
    if len(data) > MAX_VIDEO_BYTES:
        raise HTTPException(400, "video exceeds the 500 MB v1 limit")
    video_path.write_bytes(data)
    logo_path.write_bytes(await logo.read())
    sha = hashlib.sha256(data).hexdigest()

    try:
        probe = media.probe(video_path)
    except RuntimeError as e:
        raise HTTPException(400, f"video could not be probed: {e}")
    if probe["duration_s"] > MAX_VIDEO_S:
        raise HTTPException(
            400, f"video is {probe['duration_s']:.0f}s; v1 limit is 180s")
    if probe["duration_s"] <= 0 or not probe["video_codec"]:
        raise HTTPException(400, "no readable video stream in the file")

    try:
        findings, not_checked, info = checks.run_checks(
            video_path, brief_data, logo_path, run_dir, run_id)
    except Exception as e:  # noqa: BLE001 - a failed run must still be recorded
        con = _con()
        store.save_run(con, run_id, _now(), video.filename, sha, brief_data,
                       "error", probe["duration_s"],
                       ["logo", "missing_scene", "technical"],
                       {"error": str(e)})
        con.close()
        raise HTTPException(500, f"check run failed: {e}")

    summary = {
        "total": len(findings),
        "blocker": sum(1 for f in findings if f["severity"] == "blocker"),
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "approved": 0, "dismissed": 0, "open": len(findings),
        "scenes_matched": len(info["scenes_matched"]),
        "scenes_total": info["scenes_total"],
        "shots": len(info["shots"]),
        "run_seconds": round(time.time() - started, 1),
    }
    con = _con()
    store.save_run(con, run_id, _now(), video.filename, sha, brief_data,
                   "done", probe["duration_s"],
                   ["logo", "missing_scene", "technical"], summary)
    store.save_findings(con, run_id, findings)
    store.save_not_checked(con, run_id, not_checked)
    run = store.get_run(con, run_id)
    con.close()
    return _public_run(run)


@app.get("/api/runs")
def list_runs():
    con = _con()
    rows = store.list_runs(con)
    con.close()
    return rows


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    con = _con()
    run = store.get_run(con, run_id)
    con.close()
    if not run:
        raise HTTPException(404, "run not found")
    return _public_run(run)


@app.post("/api/runs/{run_id}/decide")
async def decide(run_id: str, payload: dict):
    finding_id = payload.get("finding_id")
    status = payload.get("status")
    note = payload.get("note", "")
    con = _con()
    try:
        store.decide(con, run_id, finding_id, status, note)
    except (ValueError, KeyError) as e:
        con.close()
        raise HTTPException(400, str(e))
    run = store.get_run(con, run_id)
    # keep the summary counts in step with decisions
    s = run["summary"]
    s["approved"] = sum(1 for f in run["findings"] if f["status"] == "approved")
    s["dismissed"] = sum(1 for f in run["findings"] if f["status"] == "dismissed")
    s["open"] = sum(1 for f in run["findings"] if f["status"] == "open")
    con.execute("UPDATE runs SET summary_json=? WHERE id=?",
                (json.dumps(s), run_id))
    con.commit()
    con.close()
    return _public_run(run)


@app.get("/api/runs/{run_id}/report.json")
def report_json(run_id: str):
    con = _con()
    run = store.get_run(con, run_id)
    con.close()
    if not run:
        raise HTTPException(404, "run not found")
    out = RUNS_DIR / run_id / "report.json"
    reports.export_json(run, out)
    return FileResponse(out, media_type="application/json",
                        filename=f"briefgate-{run_id}.json")


@app.get("/api/runs/{run_id}/report.pdf")
def report_pdf(run_id: str):
    con = _con()
    run = store.get_run(con, run_id)
    con.close()
    if not run:
        raise HTTPException(404, "run not found")
    out = RUNS_DIR / run_id / "report.pdf"
    reports.export_pdf(run, out)
    return FileResponse(out, media_type="application/pdf",
                        filename=f"briefgate-{run_id}.pdf")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _public_run(run: dict) -> dict:
    """Rewrite absolute frame paths to /frames/ URLs for the browser."""
    run = dict(run)
    for f in run["findings"]:
        p = Path(f["frame_path"])
        f["frame_url"] = (f"/frames/{run['id']}/{p.name}"
                          if p.exists() else None)
    return run


if FRONTEND_DIST.exists():
    app.mount("/frames", StaticFiles(directory=str(RUNS_DIR)), name="frames")
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True),
              name="frontend")
else:
    @app.get("/frames/{run_id}/{name}")
    def frame(run_id: str, name: str):
        p = RUNS_DIR / run_id / name
        if not p.exists():
            raise HTTPException(404, "frame not found")
        return FileResponse(p, media_type="image/png")

    @app.get("/")
    def index():
        return JSONResponse(
            {"product": "BriefGate",
             "note": "frontend bundle not built yet — run npm run build in "
                     "app/frontend, or use the API directly"})
