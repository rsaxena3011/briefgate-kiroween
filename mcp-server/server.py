#!/usr/bin/env python3
"""BriefGate local MCP server (stdio JSON-RPC 2.0).

Genuine, minimal use: lets Kiro query real media facts (ffprobe) and the run
store during development, instead of guessing. Two tools only:
  - probe_video(path) -> duration, resolution, streams, has_audio
  - list_runs(limit)  -> recent runs from the SQLite store (if any)
No network. No credentials. No writes.
"""
import json
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe_video(path):
    if not os.path.isfile(path):
        return {"error": f"no such file: {path}"}
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": "ffprobe failed", "stderr": r.stderr[:500]}
    d = json.loads(r.stdout)
    streams = [{"codec": s.get("codec_name"), "type": s.get("codec_type"),
                "width": s.get("width"), "height": s.get("height")}
               for s in d.get("streams", [])]
    return {"duration_s": float(d.get("format", {}).get("duration", 0)),
            "size_bytes": int(d.get("format", {}).get("size", 0)),
            "streams": streams,
            "has_audio": any(s["type"] == "audio" for s in streams)}


def list_runs(limit=10):
    db = os.path.join(ROOT, "runs", "briefgate.db")
    if not os.path.isfile(db):
        return {"runs": [], "note": "no run store yet"}
    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT id, video_name, status, created_at FROM runs "
        "ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    con.close()
    return {"runs": [{"id": r[0], "video": r[1], "status": r[2],
                      "created_at": r[3]} for r in rows]}


TOOLS = {"probe_video": probe_video, "list_runs": list_runs}


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid,
                "result": {"protocolVersion": "2024-11-05",
                           "serverInfo": {"name": "briefgate-probe",
                                          "version": "1.0.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": [
            {"name": "probe_video",
             "description": "ffprobe a video file",
             "inputSchema": {"type": "object",
                             "properties": {"path": {"type": "string"}},
                             "required": ["path"]}},
            {"name": "list_runs",
             "description": "list recent QC runs",
             "inputSchema": {"type": "object",
                             "properties": {"limit": {"type": "integer"}}}}]}}
    if method == "tools/call":
        name = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {})
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            out = TOOLS[name](**args)
        except TypeError as e:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": str(e)}}
        return {"jsonrpc": "2.0", "id": mid,
                "result": {"content": [{"type": "text",
                                        "text": json.dumps(out, indent=2)}]}}
    if method in ("notifications/initialized", None):
        return None
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"unknown method {method}"}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
