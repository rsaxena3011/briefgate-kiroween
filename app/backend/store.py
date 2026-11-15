"""SQLite run store. One record per run; re-runs create new runs, never
overwrite. Findings + decisions + export paths live here — the single source
of truth the PDF/JSON reports are generated from.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY, created_at TEXT, video_name TEXT, video_sha256 TEXT,
  brief_json TEXT, status TEXT, duration_s REAL,
  checks_run_json TEXT, summary_json TEXT);
CREATE TABLE IF NOT EXISTS findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, finding_id TEXT,
  type TEXT, severity TEXT, timestamp_in_s REAL, timestamp_out_s REAL,
  frame_path TEXT, expected TEXT, observed TEXT, confidence REAL,
  status TEXT, reviewer_note TEXT);
CREATE TABLE IF NOT EXISTS not_checked (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, scope TEXT, reason TEXT);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def save_run(con, run_id, created_at, video_name, video_sha256, brief,
             status, duration_s, checks_run, summary):
    con.execute(
        "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)",
        (run_id, created_at, video_name, video_sha256, json.dumps(brief),
         status, duration_s, json.dumps(checks_run), json.dumps(summary)))
    con.commit()


def save_findings(con, run_id, findings):
    for f in findings:
        con.execute(
            "INSERT INTO findings (run_id, finding_id, type, severity,"
            " timestamp_in_s, timestamp_out_s, frame_path, expected,"
            " observed, confidence, status, reviewer_note)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, f["finding_id"], f["type"], f["severity"],
             f["timestamp_in_s"], f["timestamp_out_s"], f["frame_image"],
             f["expected"], f["observed"], f["confidence"], f["status"],
             f.get("reviewer_note", "")))
    con.commit()


def save_not_checked(con, run_id, items):
    for it in items:
        con.execute("INSERT INTO not_checked (run_id, scope, reason)"
                    " VALUES (?,?,?)", (run_id, it["scope"], it["reason"]))
    con.commit()


def get_run(con, run_id) -> dict | None:
    row = con.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["brief"] = json.loads(d.pop("brief_json"))
    d["checks_run"] = json.loads(d.pop("checks_run_json"))
    d["summary"] = json.loads(d.pop("summary_json"))
    d["findings"] = [dict(r) for r in con.execute(
        "SELECT * FROM findings WHERE run_id=? ORDER BY timestamp_in_s",
        (run_id,))]
    d["not_checked"] = [dict(r) for r in con.execute(
        "SELECT scope, reason FROM not_checked WHERE run_id=?", (run_id,))]
    return d


def list_runs(con, limit=20) -> list[dict]:
    return [dict(r) for r in con.execute(
        "SELECT id, created_at, video_name, status, duration_s FROM runs"
        " ORDER BY created_at DESC LIMIT ?", (limit,))]


def decide(con, run_id, finding_id, status, note=""):
    if status not in ("approved", "dismissed"):
        raise ValueError("status must be approved or dismissed")
    cur = con.execute(
        "UPDATE findings SET status=?, reviewer_note=? "
        "WHERE run_id=? AND finding_id=?",
        (status, note, run_id, finding_id))
    if cur.rowcount == 0:
        raise KeyError(f"finding {finding_id} not found in run {run_id}")
    con.commit()
