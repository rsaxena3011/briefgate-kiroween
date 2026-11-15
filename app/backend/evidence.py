"""Evidence records — the one rule no version may break.

Every finding carries a real extracted frame or the check returns
`not_checked`. See .kiro/steering/evidence-rule.md.
"""
from __future__ import annotations

REQUIRED_FIELDS = ["finding_id", "type", "severity", "timestamp_in_s",
                   "frame_image", "expected", "observed", "confidence",
                   "status"]

FINDING_TYPES = {"logo_mismatch", "logo_absent", "scene_missing",
                 "black_frame", "duration_mismatch", "silence",
                 "stream_error"}


def validate_finding(f: dict) -> dict:
    missing = [k for k in REQUIRED_FIELDS if k not in f or f[k] in (None, "")]
    if missing:
        raise ValueError(f"finding {f.get('finding_id', '?')} missing evidence "
                         f"fields: {missing}")
    if f["type"] not in FINDING_TYPES:
        raise ValueError(f"unknown finding type: {f['type']}")
    if f["severity"] not in ("blocker", "warning"):
        raise ValueError(f"unknown severity: {f['severity']}")
    if f["status"] not in ("open", "approved", "dismissed"):
        raise ValueError(f"unknown status: {f['status']}")
    if not (0.0 <= float(f["confidence"]) <= 1.0):
        raise ValueError("confidence must be in [0, 1]")
    return f


def make_finding(finding_id: str, type: str, severity: str,
                 timestamp_in_s: float, timestamp_out_s: float | None,
                 frame_image: str, expected: str, observed: str,
                 confidence: float, note: str = "") -> dict:
    """Build + validate one finding. `frame_image` must be a path to a frame
    extracted from the submitted video — never a generated/stock image.
    For scene_missing, frame_image is the previous matched shot's frame and
    the record states the defect is an absence (see observed text)."""
    f = {
        "finding_id": finding_id,
        "type": type,
        "severity": severity,
        "timestamp_in_s": round(float(timestamp_in_s), 2),
        "timestamp_out_s": (round(float(timestamp_out_s), 2)
                            if timestamp_out_s is not None else None),
        "frame_image": frame_image,
        "expected": expected,
        "observed": observed,
        "confidence": round(float(confidence), 3),
        "status": "open",
        "reviewer_note": note,
    }
    return validate_finding(f)
