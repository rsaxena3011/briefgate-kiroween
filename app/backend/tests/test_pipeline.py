"""Pipeline acceptance test — the gate scored against the sample-pack
answer key (BUILD_SPEC_v1.md §9). The sample pack is read, never
regenerated, by this test.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend import checks, media  # noqa: E402
from backend.vision import get_adapter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2].parent
PACK = ROOT / "sample-pack"


def _run(video: str, tmp: Path):
    brief = json.loads((PACK / "brief.json").read_text())
    run_dir = tmp / video.replace(".mp4", "")
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    findings, not_checked, info = checks.run_checks(
        PACK / video, brief, PACK / "approved_logo.png", run_dir, "test")
    return findings, not_checked, info, time.time() - t0


def test_logo_adapter_scores(tmp_path):
    """Approved logo scores high, wrong logo scores low — measured."""
    adapter = get_adapter("local")
    for t, want in ((7.0, True), (43.0, False)):
        fp = tmp_path / f"f{t}.png"
        media.extract_frame(PACK / "sample_video.mp4", t, fp)
        res = adapter.check_logo(str(fp), str(PACK / "approved_logo.png"))
        assert res["present"] is want, (t, res)
        if want:
            assert res["score"] >= 0.55
        else:
            assert res["score"] < 0.55 and res["badge_present"] is True


def test_sample_video_catches_all_plants(tmp_path):
    findings, not_checked, info, secs = _run("sample_video.mp4", tmp_path)
    key = json.loads((PACK / "ANSWER_KEY.json").read_text())["sample_video.mp4"]
    assert secs < 120, f"run took {secs:.1f}s, limit 120s"
    by_type = {}
    for f in findings:
        by_type.setdefault(f["type"], []).append(f)
    # 1. wrong logo at 43.0 ± 1s
    assert "logo_mismatch" in by_type
    lm = by_type["logo_mismatch"][0]
    assert abs(lm["timestamp_in_s"] - 43.0) <= 1.0, lm
    assert Path(lm["frame_image"]).exists()
    # 2. missing scene s04
    assert "scene_missing" in by_type
    assert any("s04" in f["observed"] for f in by_type["scene_missing"])
    # 3. black frame 60-63, measured ~3.0s
    assert "black_frame" in by_type
    bf = by_type["black_frame"][0]
    assert abs(bf["timestamp_in_s"] - 60.0) <= 1.0
    assert "3.0s" in bf["observed"]
    # silence is the same plant, warning severity
    assert "silence" in by_type
    # 4. blocker count matches the key
    blockers = [f for f in findings if f["severity"] == "blocker"]
    assert len(blockers) == key["expected_blockers"], findings
    # 5. every finding opens a real extracted frame
    for f in findings:
        assert Path(f["frame_image"]).exists()
        assert Path(f["frame_image"]).stat().st_size > 1000
    # 6. shots detected per scene change
    assert len(info["shots"]) >= 6, info["shots"]
    assert info["scenes_matched"] == ["s01", "s02", "s03", "s05", "s06", "s07"]


def test_control_video_zero_blockers(tmp_path):
    findings, not_checked, info, secs = _run("control_video.mp4", tmp_path)
    blockers = [f for f in findings if f["severity"] == "blocker"]
    assert blockers == [], findings
    assert info["scenes_matched"] == ["s01", "s02", "s03", "s04", "s05",
                                      "s06", "s07"]
