"""Tests for the AI feature-detection core (spec §8.3).

Covers the pure stages — tiling, geo-transform, detection merge/NMS/filter, and
the numpy spectral water + slope math — without ultralytics/rasterio/GDAL."""
import math

import pytest

from app.services.detection.tiling import generate_tiles
from app.services.detection import geotransform as gt
from app.services.detection import merge
from app.services.detection.merge import Detection

# Identity-ish EPSG:4326 north-up transform near Maryville, TN.
TRANSFORM = (1e-5, 0.0, -83.97, 0.0, -1e-5, 35.75)


# ---- tiling ----
def test_tiles_cover_full_raster():
    tiles = generate_tiles(1000, 800, size=640, overlap=64)
    assert max(t.col_end for t in tiles) == 1000
    assert max(t.row_end for t in tiles) == 800
    assert all(t.col_end <= 1000 and t.row_end <= 800 for t in tiles)


def test_single_tile_when_smaller_than_chip():
    tiles = generate_tiles(500, 400, size=640, overlap=64)
    assert len(tiles) == 1
    assert tiles[0].width == 500 and tiles[0].height == 400


def test_tiling_validates_overlap():
    with pytest.raises(ValueError):
        generate_tiles(100, 100, size=640, overlap=640)


# ---- geo-transform ----
def test_pixel_to_world_origin():
    assert gt.pixel_to_world(TRANSFORM, 0, 0) == (-83.97, 35.75)


def test_bbox_to_ring_is_closed():
    ring = gt.bbox_to_ring(TRANSFORM, 0, 0, 10, 10)
    assert ring[0] == ring[-1]
    assert len(ring) == 5


def test_ring_area_sqft_matches_parcel(square_parcel):
    ring = [tuple(p) for p in square_parcel["coordinates"][0]]
    area = gt.ring_area_sqft(ring)
    # 300 × 400 ft ≈ 120,000 sqft.
    assert abs(area - 120000) < 1500


# ---- merge / NMS / filter ----
def test_map_class_aliases():
    assert merge.map_class("Building") == "structure"
    assert merge.map_class("swimming-pool") == "pond"
    assert merge.map_class("unknown-thing") is None


def test_nms_suppresses_overlapping_boxes():
    a = Detection(0, 0, 10, 10, 0.9, "building")
    b = Detection(1, 1, 11, 11, 0.8, "building")  # ~IoU high with a
    c = Detection(100, 100, 110, 110, 0.7, "building")  # far away
    kept = merge.non_max_suppression([a, b, c], iou_thresh=0.5)
    assert a in kept and c in kept and b not in kept


def test_detections_to_features_filters_and_georeferences():
    dets = [
        Detection(0, 0, 50, 50, 0.9, "building"),     # kept → structure
        Detection(200, 200, 250, 250, 0.30, "tree"),  # dropped: below 0.45
        Detection(400, 400, 450, 450, 0.8, "alien"),  # dropped: unknown class
    ]
    feats = merge.detections_to_features(dets, TRANSFORM, min_confidence=0.45)
    assert len(feats) == 1
    f = feats[0]
    assert f["properties"]["feature_type"] == "structure"
    assert f["properties"]["confidence"] == 0.9
    assert f["properties"]["area_sqft"] > 0
    assert f["geometry"]["type"] == "Polygon"


# ---- spectral water ----
def test_water_mask_flags_blue_pixels():
    np = pytest.importorskip("numpy")
    img = np.zeros((20, 20, 3), dtype="uint8")
    img[:, :, 2] = 220  # strong blue
    img[:, :, 0] = 20
    img[:, :, 1] = 40
    mask = __import__("app.services.detection.spectral", fromlist=["water_mask"]).water_mask(img)
    assert mask.mean() > 0.9


def test_mask_to_boxes_finds_regions():
    np = pytest.importorskip("numpy")
    from app.services.detection.spectral import mask_to_boxes

    mask = np.zeros((30, 30), dtype=bool)
    mask[5:15, 5:15] = True  # 100-px blob
    boxes = mask_to_boxes(mask, min_pixels=50)
    assert len(boxes) == 1
    c0, r0, c1, r1 = boxes[0]
    assert (c0, r0, c1, r1) == (5, 5, 15, 15)


def test_slope_aspect_points_downhill():
    np = pytest.importorskip("numpy")
    from app.services.detection.spectral import slope_aspect

    # Elevation increasing to the east → downhill points west.
    dtm = np.tile(np.arange(20, dtype="float32"), (20, 1))  # z grows with col
    slope, aspect = slope_aspect(dtm, pixel_size_ft=1.0)
    assert slope.mean() > 0
    # Aspect ~180° (west) where +x is east and downhill is -x.
    assert 150 < float(np.median(aspect)) < 210
