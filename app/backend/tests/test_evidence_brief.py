"""Unit tests: evidence rule + brief schema validation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from backend.evidence import make_finding, validate_finding
from backend.checks import validate_brief

GOOD = {"finding_id": "run-01", "type": "logo_mismatch", "severity": "blocker",
        "timestamp_in_s": 43.0, "frame_image": "x.png",
        "expected": "approved logo", "observed": "wrong logo",
        "confidence": 0.9, "status": "open"}


def test_validate_accepts_complete_record():
    assert validate_finding(dict(GOOD))["finding_id"] == "run-01"


def test_validate_rejects_missing_frame():
    bad = dict(GOOD)
    del bad["frame_image"]
    with pytest.raises(ValueError, match="frame_image"):
        validate_finding(bad)


def test_validate_rejects_bad_type():
    bad = dict(GOOD, type="made_up")
    with pytest.raises(ValueError, match="unknown finding type"):
        validate_finding(bad)


def test_make_finding_rounds_and_validates():
    f = make_finding("r-01", "black_frame", "blocker", 60.04, 63.0, "f.png",
                     "no black > 0.5s", "black 3.0s", 0.99)
    assert f["timestamp_in_s"] == 60.04 and f["status"] == "open"


def test_brief_valid():
    brief = {"project": "P", "expected_duration_s": 90,
             "scenes": [{"id": "s01", "description": "navy title"}],
             "brand": {"logo_ref": "logo.png", "logo_required_in": "all"},
             "technical": {}}
    assert validate_brief(brief) == []


def test_brief_rejects_missing_fields_and_names_them():
    errs = validate_brief({"project": "P"})
    assert any("expected_duration_s" in e for e in errs)
    assert any("scenes" in e for e in errs)
    assert any("brand.logo_ref" in e for e in errs)


def test_brief_rejects_scene_without_description():
    brief = {"project": "P", "expected_duration_s": 90,
             "scenes": [{"id": "s01"}],
             "brand": {"logo_ref": "logo.png", "logo_required_in": "all"}}
    assert any("scenes[0]" in e for e in validate_brief(brief))
