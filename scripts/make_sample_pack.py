#!/usr/bin/env python3
"""Generate the BriefGate sample pack — self-made footage only, no real
client footage ever.

Two 90-second videos (1280x720, 25fps, H.264 + AAC sine tone):
  sample_video.mp4 — planted defects, with ANSWER_KEY.json:
      * wrong logo ("NovaCorp") in the testimonial scene, 42-45s
        (first flagged frame 43.0s — the demo anchor moment)
      * brief scene s04 (drone flyover) absent from the video
      * black-frame + silence segment 60-63s (3.0s, limit 0.5s / 2.0s)
  control_video.mp4 — same brief, all scenes present, approved logo
      everywhere, no black/silence. Expected: zero blocker findings.
Plus: brief.json, approved_logo.png, wrong_logo.png, ANSWER_KEY.json.

Each scene is a solid colour + big title text + logo badge top-right.
Scenes (sample): s01 navy 0-15, s02 teal 15-30, s03 amber 30-45
(approved logo 30-42, wrong logo 42-45), s05 green 45-60,
black 60-63, s06 purple 63-78, s07 crimson 78-90.
Control: s01 0-15, s02 15-30, s03 30-45 (approved throughout),
s05 45-60, s04 slate 60-63, s06 63-78, s07 78-90.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sample-pack"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1280, 720
FPS = 25

SCENES = [
    ("s01", "OPENING TITLE", (27, 42, 74), "deep navy background"),
    ("s02", "PRODUCT HERO", (15, 82, 87), "teal background"),
    ("s03", "TESTIMONIAL", (138, 90, 0), "warm amber background"),
    ("s04", "DRONE FLYOVER", (51, 65, 85), "slate grey background"),
    ("s05", "CALL TO ACTION", (30, 91, 52), "deep green background"),
    ("s06", "B-ROLL MONTAGE", (75, 46, 91), "rich purple background"),
    ("s07", "END CARD", (110, 20, 35), "dark crimson background"),
]
BY_ID = {s[0]: s for s in SCENES}

BRIEF = {
    "project": "SaxenaWave — Launch Film (Sample)",
    "expected_duration_s": 90,
    "duration_tolerance_s": 2,
    "scenes": [
        {"id": "s01", "description":
         "Opening title card, deep navy background, SaxenaWave logo top right"},
        {"id": "s02", "description":
         "Product hero shot, teal background, product centre frame"},
        {"id": "s03", "description":
         "Customer testimonial, warm amber background, speaker centre frame"},
        {"id": "s04", "description":
         "Drone flyover, city skyline at dusk, slate grey background"},
        {"id": "s05", "description":
         "Closing call to action, deep green background, SaxenaWave logo top right"},
        {"id": "s06", "description":
         "B-roll montage, rich purple background, fast cuts"},
        {"id": "s07", "description":
         "End card, dark crimson background, SaxenaWave logo top right"},
    ],
    "brand": {"logo_ref": "approved_logo.png", "logo_required_in": "all"},
    "technical": {"max_black_frame_s": 0.5, "max_silence_s": 2.0},
}

ANSWER_KEY = {
    "sample_video.mp4": {
        "expected_findings": [
            {"type": "logo_mismatch", "timestamp_in_s": 43.0,
             "tolerance_s": 1.0, "scene": "s03",
             "note": "wrong NovaCorp logo 42-45s"},
            {"type": "scene_missing", "scene_id": "s04",
             "note": "drone flyover absent"},
            {"type": "black_frame", "start_s": 60.0, "duration_s": 3.0,
             "tolerance_s": 0.3},
            {"type": "silence", "start_s": 60.0, "duration_s": 3.0,
             "tolerance_s": 0.3},
        ],
        "expected_blockers": 3,
        "expected_duration_s": 90,
    },
    "control_video.mp4": {
        "expected_findings": [],
        "expected_blockers": 0,
        "expected_duration_s": 90,
    },
}


def make_logo(path: Path, text: str, bg: tuple, fg: tuple = (255, 255, 255),
              w: int = 320, h: int = 90) -> None:
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=18, outline=fg, width=4)
    f = ImageFont.truetype(FONT, 44)
    d.text((w // 2, h // 2), text, font=f, fill=fg, anchor="mm")
    img.save(path)


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)


def segment(name: str, rgb: tuple, text: str, dur: float, logo: Path | None,
            audio: bool) -> Path:
    """One scene segment as an mp4: solid colour + title + logo badge."""
    out = OUT / "tmp" / f"{name}.mp4"
    hexcol = "0x%02x%02x%02x" % rgb
    filt = f"[0:v][1:v]overlay=W-w-40:40,drawtext=fontfile={FONT}:text='{text}':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "lavfi", "-i", f"color=c={hexcol}:s={W}x{H}:d={dur}:r={FPS}",
           "-i", str(logo)]
    cmd += ["-f", "lavfi", "-i",
            ("sine=frequency=440:sample_rate=44100:duration=%s" % dur) if audio
            else f"anullsrc=channel_layout=mono:sample_rate=44100:d={dur}",
            "-filter_complex", filt,
            "-map", "0:v", "-map", "2:a", "-t", str(dur),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-ar", "44100",
            "-shortest", str(out)]
    run(cmd)
    return out


def black_segment(name: str, dur: float) -> Path:
    out = OUT / "tmp" / f"{name}.mp4"
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={dur}:r={FPS}",
         "-f", "lavfi", "-i",
         f"anullsrc=channel_layout=mono:sample_rate=44100:d={dur}",
         "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "96k", "-ac", "1",
         "-ar", "44100", "-shortest",
         str(out)])
    return out


def concat(parts: list[Path], out: Path) -> None:
    """Join segments with the concat FILTER (one re-encode).

    The concat demuxer with `-c copy` misaligned the AAC audio (the silent
    black segment's audio vanished from the final timeline — measured:
    -21 dB tone where 60-63s should be silent, and zero audio frames in
    places). Re-encoding through the filter keeps A/V aligned; 90s of 720p
    costs under a minute.
    """
    inputs: list[str] = []
    for p in parts:
        inputs += ["-i", str(p)]
    n = len(parts)
    filt = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    filt += f"concat=n={n}:v=1:a=1[v][a]"
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         "-filter_complex", filt, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-ar", "44100",
         str(out)])


def build_sample() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    approved = OUT / "approved_logo.png"
    wrong = OUT / "wrong_logo.png"
    make_logo(approved, "SaxenaWave", (11, 31, 58))
    make_logo(wrong, "NovaCorp", (90, 10, 10), w=260, h=110)
    (OUT / "tmp").mkdir(parents=True, exist_ok=True)

    def seg(scene_id, start, end, logo):
        _, text, rgb, _ = BY_ID[scene_id]
        return segment(f"{scene_id}-{start}", rgb, text, end - start, logo, True)

    # planted-defect video
    parts = [
        seg("s01", 0, 15, approved),
        seg("s02", 15, 30, approved),
        segment("s03a-30", BY_ID["s03"][2], "TESTIMONIAL", 12, approved, True),
        segment("s03b-42", BY_ID["s03"][2], "TESTIMONIAL", 3, wrong, True),
        seg("s05", 45, 60, approved),
        black_segment("black-60", 3),
        seg("s06", 63, 78, approved),
        seg("s07", 78, 90, approved),
    ]
    concat(parts, OUT / "sample_video.mp4")
    # clean control video — SAME brief order as the sample (s01..s07 in
    # order; the scene check aligns in order), all scenes present, approved
    # logo everywhere, tone throughout, no black/silence.
    parts = [
        seg("s01", 0, 15, approved),
        seg("s02", 15, 30, approved),
        seg("s03", 30, 45, approved),
        seg("s04", 45, 48, approved),
        seg("s05", 48, 60, approved),
        seg("s06", 60, 75, approved),
        seg("s07", 75, 90, approved),
    ]
    concat(parts, OUT / "control_video.mp4")

    (OUT / "brief.json").write_text(json.dumps(BRIEF, indent=2))
    (OUT / "ANSWER_KEY.json").write_text(json.dumps(ANSWER_KEY, indent=2))
    import shutil as _shutil
    _shutil.rmtree(OUT / "tmp", ignore_errors=True)
    print("sample pack written to", OUT)
    for f in ("sample_video.mp4", "control_video.mp4"):
        r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                            "format=duration", "-of", "csv=p=0",
                            str(OUT / f)], capture_output=True, text=True)
        print(f, "duration:", r.stdout.strip(), "s")


if __name__ == "__main__":
    build_sample()
