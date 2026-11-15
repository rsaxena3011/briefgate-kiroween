"""Media engine — FFmpeg/FFprobe + OpenCV wrappers.

Returns plain facts (durations, shot boundaries, frames, colours). Never
findings: the checks in checks.py turn facts into findings.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np

PALETTE = {  # name -> RGB, the colours the self-made sample pack uses
    "navy": (27, 42, 74), "teal": (15, 82, 87), "amber": (138, 90, 0),
    "slate": (51, 65, 85), "green": (30, 91, 52), "purple": (75, 46, 91),
    "crimson": (110, 20, 35), "black": (0, 0, 0), "gold": (176, 141, 42),
}


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def probe(path: str | Path) -> dict:
    r = _run(["ffprobe", "-v", "quiet", "-print_format", "json",
              "-show_format", "-show_streams", str(path)])
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {r.stderr[:300]}")
    d = json.loads(r.stdout)
    fmt = d.get("format", {})
    video = [s for s in d.get("streams", []) if s.get("codec_type") == "video"]
    audio = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    return {
        "duration_s": float(fmt.get("duration", 0) or 0),
        "size_bytes": int(fmt.get("size", 0) or 0),
        "width": int(video[0].get("width", 0)) if video else 0,
        "height": int(video[0].get("height", 0)) if video else 0,
        "video_codec": video[0].get("codec_name") if video else None,
        "has_audio": bool(audio),
        "streams": len(d.get("streams", [])),
    }


def detect_shots(path: str | Path, duration: float,
                 threshold: float = 30.0) -> list[dict]:
    """Shot boundaries by OpenCV colour-change detection.

    Samples the video at 2 fps and cuts when the median colour of the frame
    centre jumps (RGB distance > threshold). Chosen over ffmpeg's `scene`
    filter because that score is luma-driven: it missed the green->slate and
    slate->purple hard cuts in the sample pack (luma differences ~0.04)
    while the colour jump is unambiguous. A small logo swap inside a scene
    (0:42) touches only the top-right corner, which the centre crop
    excludes, so it correctly stays one shot. Minimum shot length 1.0s.
    """
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(round(fps / 2)))  # 2 fps sampling
    cuts = [0.0]
    prev_rgb = None
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            t = idx / fps
            h, w = frame.shape[:2]
            crop = frame[int(h * 0.35):int(h * 0.75),
                         int(w * 0.2):int(w * 0.8)]
            bgr = np.median(crop.reshape(-1, 3), axis=0)
            rgb = (float(bgr[2]), float(bgr[1]), float(bgr[0]))
            if prev_rgb is not None:
                if math.dist(rgb, prev_rgb) > threshold and t - cuts[-1] >= 1.0:
                    cuts.append(round(t, 2))
            prev_rgb = rgb
        idx += 1
    cap.release()
    shots = []
    for i, start in enumerate(cuts):
        end = cuts[i + 1] if i + 1 < len(cuts) else duration
        if end - start >= 0.5:
            shots.append({"start": start, "end": round(end, 2)})
    return shots


def extract_frame(path: str | Path, t: float, out: str | Path) -> str:
    out = str(out)
    r = _run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(path),
              "-frames:v", "1", "-q:v", "2", out])
    if r.returncode != 0 or not Path(out).exists():
        raise RuntimeError(f"frame extract failed at {t}s: {r.stderr[:300]}")
    return out


def black_segments(path: str | Path, min_duration: float) -> list[dict]:
    r = _run(["ffmpeg", "-i", str(path), "-vf",
              f"blackdetect=d={min_duration}:pic_th=0.98:pix_th=0.10",
              "-f", "null", "-"])
    segs = []
    for m in re.finditer(
            r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)",
            r.stderr):
        segs.append({"start": float(m.group(1)), "end": float(m.group(2)),
                     "duration": float(m.group(3))})
    return segs


def silence_segments(path: str | Path, min_duration: float) -> list[dict]:
    r = _run(["ffmpeg", "-i", str(path), "-af",
              f"silencedetect=noise=-50dB:d={min_duration}",
              "-f", "null", "-"])
    segs = []
    for m in re.finditer(
            r"silence_start: ([\d.]+).*?silence_end: ([\d.]+) \| "
            r"silence_duration: ([\d.]+)", r.stderr, re.S):
        segs.append({"start": float(m.group(1)), "end": float(m.group(2)),
                     "duration": float(m.group(3))})
    # trailing silence (no silence_end before EOF)
    m = re.search(r"silence_start: ([\d.]+)\s*$", r.stderr)
    if m and not any(abs(s["start"] - float(m.group(1))) < 0.01
                     for s in segs):
        segs.append({"start": float(m.group(1)), "end": None, "duration": None})
    return segs


def dominant_colour(image_path: str | Path) -> tuple[str, tuple[int, int, int]]:
    """Dominant colour of the frame centre (logo zone + text excluded by
    sampling the middle band). Returns (palette name, rgb)."""
    img = cv2.imread(str(image_path))
    if img is None:
        return "black", (0, 0, 0)
    h, w = img.shape[:2]
    crop = img[int(h * 0.35):int(h * 0.75), int(w * 0.2):int(w * 0.8)]
    # median colour resists the white title text
    bgr = np.median(crop.reshape(-1, 3), axis=0)
    rgb = (int(bgr[2]), int(bgr[1]), int(bgr[0]))
    best, best_d = "black", 1e9
    for name, ref in PALETTE.items():
        d = math.dist(rgb, ref)
        if d < best_d:
            best, best_d = name, d
    return best, rgb
