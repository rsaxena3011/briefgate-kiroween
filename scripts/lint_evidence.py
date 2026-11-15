#!/usr/bin/env python3
"""Evidence-schema lint (hook: evidence-schema-lint).

Checks, by AST + runtime, that the finding factory in evidence.py covers
every field required by .kiro/steering/evidence-rule.md and that the
validator rejects incomplete records. Exits non-zero on any violation.
"""
import ast
import sys
from pathlib import Path

REQUIRED = ["finding_id", "type", "severity", "timestamp_in_s",
            "frame_image", "expected", "observed", "confidence", "status"]
ROOT = Path(__file__).resolve().parent.parent

errors = []
ev = ROOT / "app" / "backend" / "evidence.py"
tree = ast.parse(ev.read_text())
fn = next((n for n in ast.walk(tree)
           if isinstance(n, ast.FunctionDef) and n.name == "make_finding"),
          None)
if fn is None:
    errors.append("evidence.make_finding not found")
else:
    params = {a.arg for a in fn.args.args}
    # status is set internally to "open"; every other field must be a param
    missing = [f for f in REQUIRED if f != "status" and f not in params]
    if missing:
        errors.append(f"make_finding signature missing params: {missing}")
    if "validate_finding" not in ev.read_text():
        errors.append("make_finding does not call validate_finding")

sys.path.insert(0, str(ROOT / "app" / "backend"))
try:
    from evidence import make_finding, validate_finding
    good = make_finding("lint-01", "logo_mismatch", "blocker", 43.0, 45.0,
                        "frame.png", "approved logo", "wrong logo", 0.9)
    validate_finding(good)
    try:
        validate_finding({"finding_id": "x", "type": "logo_mismatch"})
        errors.append("validate_finding accepted an incomplete record")
    except ValueError:
        pass
    try:
        validate_finding(dict(good, type="made_up"))
        errors.append("validate_finding accepted an unknown type")
    except ValueError:
        pass
except Exception as e:  # noqa: BLE001 - lint must report, not crash silently
    errors.append(f"evidence validator import/run failed: {e}")

if errors:
    print("EVIDENCE-SCHEMA LINT FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("evidence-schema lint: OK")
