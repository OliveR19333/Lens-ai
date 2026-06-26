"""Download a trained YOLOv8 aerial-detection model into models/ (spec §8.3).

The detector looks for the weights at ``YOLO_MODEL_PATH`` (default
``models/yolov8n-aerial-property.pt``). Pick a model from Roboflow Universe
(search "aerial property", "building footprint", "swimming pool aerial", etc.),
export it as **YOLOv8 PyTorch (.pt)**, and pass its download URL here.

Usage:
    python scripts/fetch_model.py <url> [dest_path]

Example:
    python scripts/fetch_model.py "https://.../weights.pt" models/yolov8n-aerial-property.pt

No third-party deps — uses urllib so it runs anywhere.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

DEFAULT_DEST = "models/yolov8n-aerial-property.pt"


def fetch(url: str, dest: str = DEFAULT_DEST) -> None:
    out = Path(dest)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model → {out} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "GAS-Mapping/1.0"})
    with urllib.request.urlopen(req) as resp, open(out, "wb") as f:  # noqa: S310
        f.write(resp.read())
    size_mb = out.stat().st_size / 1e6
    print(f"✅ Saved {out} ({size_mb:.1f} MB). Set YOLO_MODEL_PATH={out} in .env if different.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    fetch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEST)
