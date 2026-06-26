"""Merge, deduplicate, and georeference raw detections (spec §8.3 step 3).

Pure standard library. Takes detections in **global pixel** coordinates (already
offset from their chip), maps model class names to our planning feature types,
runs non-maximum suppression to drop overlaps from tile overlap, filters by
confidence, and emits a GeoJSON FeatureCollection matching spec §11.2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.services.detection.geotransform import Affine6, bbox_to_ring, ring_area_sqft

# Map detector class names → our feature types (spec §8.2). Configurable; covers
# common aerial-property model vocabularies.
DEFAULT_CLASS_MAP = {
    "building": "structure",
    "house": "structure",
    "structure": "structure",
    "shed": "structure",
    "pool": "pond",
    "swimming-pool": "pond",
    "pond": "pond",
    "water": "pond",
    "lake": "pond",
    "tree": "trees",
    "trees": "trees",
    "vegetation": "trees",
    "driveway": "driveway",
    "road": "driveway",
    "pavement": "driveway",
    "fence": "fence",
}

LABELS = {
    "structure": "Structure",
    "pond": "Pond",
    "trees": "Trees",
    "driveway": "Driveway",
    "fence": "Fence",
    "slope": "Slope",
}


@dataclass
class Detection:
    col0: float
    row0: float
    col1: float
    row1: float
    score: float
    cls_name: str

    def area_px(self) -> float:
        return max(0.0, self.col1 - self.col0) * max(0.0, self.row1 - self.row0)


def map_class(cls_name: str, class_map: Dict[str, str] | None = None) -> Optional[str]:
    cm = class_map or DEFAULT_CLASS_MAP
    return cm.get(cls_name.strip().lower())


def iou(a: Detection, b: Detection) -> float:
    ix0, iy0 = max(a.col0, b.col0), max(a.row0, b.row0)
    ix1, iy1 = min(a.col1, b.col1), min(a.row1, b.row1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    union = a.area_px() + b.area_px() - inter
    return inter / union if union > 0 else 0.0


def non_max_suppression(dets: List[Detection], iou_thresh: float = 0.5) -> List[Detection]:
    """Greedy NMS: keep the highest-scoring box, drop overlaps above the threshold."""
    kept: List[Detection] = []
    for d in sorted(dets, key=lambda x: x.score, reverse=True):
        if all(iou(d, k) < iou_thresh for k in kept):
            kept.append(d)
    return kept


def detections_to_features(
    dets: List[Detection],
    transform: Affine6,
    *,
    min_confidence: float = 0.45,
    iou_thresh: float = 0.5,
    class_map: Dict[str, str] | None = None,
) -> List[dict]:
    """Filter + NMS + georeference detections into spec §11.2 features."""
    eligible = [d for d in dets if d.score >= min_confidence and map_class(d.cls_name, class_map)]
    kept = non_max_suppression(eligible, iou_thresh=iou_thresh)
    features: List[dict] = []
    for d in kept:
        ftype = map_class(d.cls_name, class_map)
        ring = bbox_to_ring(transform, d.col0, d.row0, d.col1, d.row1)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[list(p) for p in ring]]},
                "properties": {
                    "feature_type": ftype,
                    "label": LABELS.get(ftype, ftype.capitalize()),
                    "confidence": round(float(d.score), 2),
                    "area_sqft": round(ring_area_sqft(ring), 1),
                    "notes": "",
                },
            }
        )
    return features


def feature_collection(features: List[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}
