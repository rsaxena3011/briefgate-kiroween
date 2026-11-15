#!/usr/bin/env python3
"""Evidence-schema lint (hook: evidence-schema-lint).

Statically checks that every finding record constructed in checks.py /
evidence.py carries the evidence fields required by
.kiro/steering/evidence-rule.md: finding_id, type, severity,
timestamp_in_s, frame_image, expected, observed, confidence, status.
Also runs the runtime validator over a synthetic record. Exits non-zero
on any violation.
"""
import re
import sys
from pathlib import Path

REQUIRED = ["finding_id", "type", "severity", "timestamp_in_s",
            "frame_image", "expected", "observed", "confidence", "status"]
ROOT = Path(__file__).resolve().parent.parent

errors = []
for name in ("app/backend/checks.py", "app/backend/evidence.py"):
    p = ROOT / name
    if not p.exists():
        errors.append(f"{name}: file missing")
        continue
    src = p.read_text()
    # every dict literal passed to make_finding / Finding(...) must name all fields
    for m in re.finditer(r"make_finding\((.*?)\)", src, re.S):
        body = m.group(1)
        missing = [f for f in REQUIRED if f not in body]
        if missing:
            errors.append(f"{name}: make_finding call missing {missing}")

# runtime check of the validator itself
sys.path.insert(0, str(ROOT / "app" / "backend"))
try:
    from evidence import validate_finding
    bad = {"finding_id": "x", "type": "logo_mismatch"}
    try:
        validate_finding(bad)
        errors.append("evidence.validate_finding accepted an incomplete record")
    except ValueError:
        pass
    good = {f: ("open" if f == "status" else 0.0 if f in ("timestamp_in_s", "confidence")
                else "x") for f in REQUIRED}
    good["timestamp_in_s"] = 43.0
    good["confidence"] = 0.9
    validate_finding(good)
except Exception as e:  # noqa: BLE001 - lint must report, not crash silently
    errors.append(f"evidence validator import/run failed: {e}")

if errors:
    print("EVIDENCE-SCHEMA LINT FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("evidence-schema lint: OK")
