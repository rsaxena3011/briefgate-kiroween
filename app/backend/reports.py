"""Report export — PDF (humans) + JSON (audit trail), both generated from
the STORED finding records only. If a report disagrees with the screen, the
export is the defect.
"""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

SEV_COLOUR = {"blocker": colors.HexColor("#b3261e"),
              "warning": colors.HexColor("#8a6d00")}


def export_json(run: dict, out: Path) -> Path:
    payload = {
        "product": "BriefGate",
        "run_id": run["id"],
        "created_at": run["created_at"],
        "video": run["video_name"],
        "duration_s": run["duration_s"],
        "project": run["brief"].get("project"),
        "checks_run": run["checks_run"],
        "not_checked": run["not_checked"],
        "summary": run["summary"],
        "findings": [
            {"finding_id": f["finding_id"], "type": f["type"],
             "severity": f["severity"],
             "timestamp_in_s": f["timestamp_in_s"],
             "timestamp_out_s": f["timestamp_out_s"],
             "frame_image": f["frame_path"],
             "expected": f["expected"], "observed": f["observed"],
             "confidence": f["confidence"], "status": f["status"],
             "reviewer_note": f["reviewer_note"]}
            for f in run["findings"]],
    }
    out.write_text(json.dumps(payload, indent=2))
    return out


def export_pdf(run: dict, out: Path) -> Path:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title=f"BriefGate QC report — {run['id']}")
    el = []
    el.append(Paragraph(
        f"BriefGate — QC report: {run['brief'].get('project', '')}",
        styles["Title"]))
    el.append(Paragraph(
        f"Run {run['id']} · {run['created_at']} · video {run['video_name']} "
        f"· duration {run['duration_s']:.1f}s", styles["Normal"]))
    s = run["summary"]
    el.append(Paragraph(
        f"Checks run: {', '.join(run['checks_run'])}. Findings: "
        f"{s['total']} total — {s['blocker']} blocker, {s['warning']} warning; "
        f"{s['approved']} approved, {s['dismissed']} dismissed, "
        f"{s['open']} still open. Scenes matched "
        f"{s['scenes_matched']}/{s['scenes_total']}.", styles["Normal"]))
    if run["not_checked"]:
        el.append(Paragraph(
            "Not checked: " + "; ".join(
                f"{n['scope']} ({n['reason']})" for n in run["not_checked"]),
            styles["Normal"]))
    el.append(Spacer(1, 6 * mm))

    decided = [f for f in run["findings"] if f["status"] != "open"]
    open_f = [f for f in run["findings"] if f["status"] == "open"]
    for f in decided + open_f:
        el.append(Paragraph(
            f"[{f['severity'].upper()}] {f['finding_id']} — {f['type']} @ "
            f"{f['timestamp_in_s']:.1f}s "
            f"(status: {f['status']})", styles["Heading3"]))
        el.append(Paragraph(f"<b>Expected:</b> {f['expected']}",
                            styles["Normal"]))
        el.append(Paragraph(f"<b>Observed:</b> {f['observed']}",
                            styles["Normal"]))
        el.append(Paragraph(
            f"Confidence {f['confidence']:.2f}"
            + (f" · Reviewer note: {f['reviewer_note']}"
               if f.get("reviewer_note") else ""), styles["Normal"]))
        fp = Path(f["frame_path"])
        if fp.exists():
            el.append(Image(str(fp), width=150 * mm, height=84 * mm))
        el.append(Spacer(1, 4 * mm))
    if not run["findings"]:
        el.append(Paragraph("No findings. The video passed all checks that "
                            "could be verified.", styles["Normal"]))
    doc.build(el)
    return out
