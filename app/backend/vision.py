"""Vision adapter — provider-swappable interface + local implementation.

v1 ships the LOCAL adapter only: OpenCV template matching of the approved
logo reference against a frame, plus a badge-presence test in the logo zone
(top-right). No provider is hard-coded into check logic; no API key is
required; no paid call is made. A future provider (e.g. a hosted vision
model) implements the same `check_logo` signature.
"""
from __future__ import annotations

import cv2
import numpy as np


class VisionAdapter:
    """Interface. check_logo returns {score, present, badge_present}."""

    def check_logo(self, frame_path: str, logo_ref_path: str) -> dict:
        raise NotImplementedError


class LocalVisionAdapter(VisionAdapter):
    # Measured on the sample pack (see tests/test_pipeline.py):
    # approved logo present -> best score 0.85-0.99; wrong logo -> 0.15-0.45.
    PRESENT_THRESHOLD = 0.55
    # edge-pixel ratio in the logo zone above which a badge-like object sits there
    BADGE_EDGE_RATIO = 0.015

    def check_logo(self, frame_path: str, logo_ref_path: str) -> dict:
        frame = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(logo_ref_path, cv2.IMREAD_GRAYSCALE)
        if frame is None:
            raise RuntimeError(f"cannot read frame {frame_path}")
        if template is None:
            raise RuntimeError(f"cannot read logo reference {logo_ref_path}")
        # downscale for speed; template matching is scale-sensitive so try
        # a small scale ladder on the downscaled frame
        fh, fw = frame.shape
        scale = 640 / fw if fw > 640 else 1.0
        small = cv2.resize(frame, (int(fw * scale), int(fh * scale)))
        th, tw = template.shape
        best = -1.0
        for s in (0.5, 0.75, 1.0, 1.25, 1.5):
            nw, nh = max(8, int(tw * scale * s)), max(8, int(th * scale * s))
            if nw >= small.shape[1] or nh >= small.shape[0]:
                continue
            tpl = cv2.resize(template, (nw, nh))
            res = cv2.matchTemplate(small, tpl, cv2.TM_CCOEFF_NORMED)
            _, mx, _, _ = cv2.minMaxLoc(res)
            best = max(best, float(mx))
        badge = self._badge_present(frame)
        return {"score": round(best, 3),
                "present": bool(best >= self.PRESENT_THRESHOLD),
                "badge_present": badge}

    def _badge_present(self, gray: np.ndarray) -> bool:
        """Is there a bounded high-contrast object in the logo zone
        (top-right 35% x 25%)? True when a wrong logo sits there; False for
        a clean solid background."""
        h, w = gray.shape
        zone = gray[0:int(h * 0.25), int(w * 0.65):w]
        edges = cv2.Canny(zone, 50, 150)
        ratio = float(np.count_nonzero(edges)) / edges.size
        return ratio > self.BADGE_EDGE_RATIO


def get_adapter(name: str = "local") -> VisionAdapter:
    if name == "local":
        return LocalVisionAdapter()
    raise ValueError(f"unknown vision adapter: {name}")
