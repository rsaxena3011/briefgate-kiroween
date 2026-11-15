"""The three v1 checks. Each takes media facts + the brief and returns
finding records, or an explicit `not_checked` scope — never a silent pass.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import media
from .evidence import make_finding
from .vision import get_adapter

STOPWORDS = {"the", "a", "an", "and", "of", "in", "on", "at", "with", "for",
             "to", "shot", "scene", "background"}


def _tokens(text: str) -> set[str]:
    words = set(re.findall(r"[a-z]+", text.lower()))
    return words - STOPWORDS


def validate_brief(brief: dict) -> list[str]:
    """Returns a list of failing fields (empty = valid)."""
    errs = []
    if not isinstance(brief.get("project"), str) or not brief.get("project"):
        errs.append("project (required string)")
    if not isinstance(brief.get("expected_duration_s"), (int, float)):
        errs.append("expected_duration_s (required number)")
    scenes = brief.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errs.append("scenes (required non-empty array)")
    else:
        for i, s in enumerate(scenes):
            if not isinstance(s, dict) or not s.get("id") or not s.get("description"):
                errs.append(f"scenes[{i}] (needs id + description)")
    brand = brief.get("brand")
    if not isinstance(brand, dict) or not brand.get("logo_ref"):
        errs.append("brand.logo_ref (required string)")
    elif "logo_required_in" not in brand:
        errs.append("brand.logo_required_in (required: scene ids or 'all')")
    tech = brief.get("technical", {})
    if not isinstance(tech, dict):
        errs.append("technical (must be an object)")
    return errs


def _colour_words(text: str) -> set[str]:
    return _tokens(text) & set(media.PALETTE)


def run_checks(video_path: Path, brief: dict, logo_ref: Path,
               run_dir: Path, run_id: str) -> tuple[list[dict], list[dict],
                                                    dict]:
    """Runs all three checks. Returns (findings, not_checked, info).
    `info` carries shots + per-shot descriptions for the run summary."""
    findings: list[dict] = []
    not_checked: list[dict] = []
    probe = media.probe(video_path)
    duration = probe["duration_s"]
    seq = [0]

    def fid() -> str:
        seq[0] += 1
        return f"{run_id}-{seq[0]:02d}"

    # --- ingest: shots + keyframes -------------------------------------
    shots = media.detect_shots(video_path, duration)
    shot_frames = []  # {shot, frame_path, colour, colour_rgb}
    for i, sh in enumerate(shots):
        mid = (sh["start"] + sh["end"]) / 2
        fp = run_dir / f"shot-{i:02d}-{mid:.1f}s.png"
        media.extract_frame(video_path, mid, fp)
        colour, rgb = media.dominant_colour(fp)
        shot_frames.append({"shot": sh, "frame": str(fp),
                            "colour": colour, "rgb": rgb,
                            "mid": round(mid, 2)})
    # black shots are technical defects, not scenes
    scene_shots = [s for s in shot_frames if s["colour"] != "black"]

    # --- check 1: logo --------------------------------------------------
    required = brief["brand"].get("logo_required_in", "all")
    adapter = get_adapter("local")
    in_scope = (scene_shots if required == "all" else
                [s for s in scene_shots])
    for idx, sf in enumerate(in_scope):
        sh = sf["shot"]
        # sample 1 fps across the shot; first flagged frame is the finding.
        # never sample past the last real frame (duration - 0.1s)
        t = sh["start"]
        last_t = min(sh["end"], duration) - 0.1
        flagged = None
        while t <= last_t:
            fp = run_dir / f"logo-{idx:02d}-{t:.0f}s.png"
            media.extract_frame(video_path, t, fp)
            # a black frame cannot show a logo; it is a technical defect,
            # handled by the black-frame check — never a logo finding
            if media.dominant_colour(fp)[0] == "black":
                t += 1.0
                continue
            res = adapter.check_logo(str(fp), str(logo_ref))
            if not res["present"]:
                flagged = (t, str(fp), res)
                break
            t += 1.0
        if flagged is None:
            continue
        t, fp, res = flagged
        expected = (f"Approved logo '{brief['brand']['logo_ref']}' visible "
                    f"in this shot (brief: logo required in "
                    f"{required if isinstance(required, str) else ', '.join(required)}).")
        if res["badge_present"]:
            findings.append(make_finding(
                fid(), "logo_mismatch", "blocker", t, min(t + 2.0, sh["end"]),
                fp, expected,
                f"A different logo is visible at {t:.0f}s — template match "
                f"against the approved logo scored {res['score']} "
                f"(present needs >= 0.55).",
                confidence=round(1 - max(res["score"], 0.0), 3)))
        else:
            findings.append(make_finding(
                fid(), "logo_absent", "blocker", t, min(t + 2.0, sh["end"]),
                fp, expected,
                f"No logo is visible at {t:.0f}s in a shot where the brief "
                f"requires the approved logo.",
                confidence=0.85))

    # --- check 2: missing scenes (in-order alignment) -------------------
    scenes = brief["scenes"]
    pointer = 0  # index into scene_shots
    matched: dict[str, dict] = {}  # scene id -> shot frame record
    last_matched_id: str | None = None
    for sc in scenes:
        want_colours = _colour_words(sc["description"])
        want_tokens = _tokens(sc["description"])
        hit = None
        for j in range(pointer, len(scene_shots)):
            sf = scene_shots[j]
            # primary signal: a colour word in the brief description equals
            # the shot's measured dominant colour
            if sf["colour"] in want_colours:
                hit = j
                break
        if hit is None:
            # evidence: neighbouring matched shots (the defect is an absence)
            if last_matched_id is not None:
                prev_f = matched[last_matched_id]["frame"]
            elif scene_shots:
                prev_f = scene_shots[0]["frame"]
            else:
                prev_f = ""
            next_f = (scene_shots[pointer]["frame"]
                      if pointer < len(scene_shots) else prev_f)
            findings.append(make_finding(
                fid(), "scene_missing", "blocker",
                float(scene_shots[pointer]["mid"]) if pointer < len(scene_shots)
                else duration, None, prev_f,
                f"Brief scene '{sc['id']}': {sc['description']}",
                f"No shot in the video matches scene '{sc['id']}'. "
                f"Neighbouring shots shown as evidence — the scene itself "
                f"does not exist in the video, so no frame of it can be shown.",
                confidence=0.9))
            # keep pointer: the next scene may still match a later shot
            continue
        matched[sc["id"]] = scene_shots[hit]
        last_matched_id = sc["id"]
        pointer = hit + 1

    # --- check 3: technical QC (deterministic) --------------------------
    tech = brief.get("technical", {}) or {}
    max_black = float(tech.get("max_black_frame_s", 0.5))
    max_sil = float(tech.get("max_silence_s", 2.0))
    for seg in media.black_segments(video_path, max_black):
        mid = (seg["start"] + seg["end"]) / 2
        fp = run_dir / f"black-{seg['start']:.0f}s.png"
        media.extract_frame(video_path, mid, fp)
        findings.append(make_finding(
            fid(), "black_frame", "blocker", seg["start"], seg["end"],
            str(fp),
            f"No black-frame segment longer than {max_black}s "
            f"(brief technical limit).",
            f"Black frames from {seg['start']:.1f}s to {seg['end']:.1f}s — "
            f"{seg['duration']:.1f}s, over the {max_black}s limit.",
            confidence=0.99))
    if probe["has_audio"]:
        for seg in media.silence_segments(video_path, max_sil):
            if seg["duration"] is None:
                continue
            mid = (seg["start"] + seg["end"]) / 2
            fp = run_dir / f"silence-{seg['start']:.0f}s.png"
            media.extract_frame(video_path, mid, fp)
            findings.append(make_finding(
                fid(), "silence", "warning", seg["start"], seg["end"],
                str(fp),
                f"No silence segment longer than {max_sil}s "
                f"(brief technical limit).",
                f"Silence from {seg['start']:.1f}s to {seg['end']:.1f}s — "
                f"{seg['duration']:.1f}s, over the {max_sil}s limit.",
                confidence=0.99))
    else:
        not_checked.append({"scope": "silence",
                            "reason": "no audio stream in the video"})
    tol = float(brief.get("duration_tolerance_s", 2))
    expected_d = float(brief["expected_duration_s"])
    if abs(duration - expected_d) > tol:
        fp = shot_frames[-1]["frame"] if shot_frames else ""
        findings.append(make_finding(
            fid(), "duration_mismatch", "warning", duration, None, fp,
            f"Total duration {expected_d}s ± {tol}s (brief).",
            f"Video duration is {duration:.1f}s, "
            f"{abs(duration - expected_d):.1f}s outside the brief.",
            confidence=0.99))

    findings.sort(key=lambda f: f["timestamp_in_s"])
    # re-number in timestamp order so ids read in order
    for i, f in enumerate(findings, 1):
        f["finding_id"] = f"{run_id}-{i:02d}"
    info = {"probe": probe, "shots": shot_frames,
            "scenes_matched": list(matched),
            "scenes_total": len(scenes)}
    return findings, not_checked, info
