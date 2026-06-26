"""GeoTIFF tiling into model-sized chips (spec §8.3).

Pure standard library. Computes the chip windows over a raster so YOLO can run
on 640×640 inputs with overlap (default 64 px) to catch features that straddle
tile edges. The actual pixel reads happen in the detector (rasterio, lazy).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Tile:
    col_off: int
    row_off: int
    width: int
    height: int

    @property
    def col_end(self) -> int:
        return self.col_off + self.width

    @property
    def row_end(self) -> int:
        return self.row_off + self.height


def generate_tiles(width: int, height: int, size: int = 640, overlap: int = 64) -> List[Tile]:
    """Tile a (width × height) raster into ``size`` chips stepping by size-overlap.

    The final row/column are clamped so chips never run past the raster edge,
    guaranteeing full coverage without out-of-bounds reads.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not (0 <= overlap < size):
        raise ValueError("overlap must be in [0, size)")

    step = size - overlap
    tiles: List[Tile] = []

    def _starts(extent: int) -> List[int]:
        if extent <= size:
            return [0]
        starts = list(range(0, extent - size + 1, step))
        if starts[-1] != extent - size:  # ensure the edge is covered
            starts.append(extent - size)
        return starts

    for row in _starts(height):
        for col in _starts(width):
            w = min(size, width - col)
            h = min(size, height - row)
            tiles.append(Tile(col, row, w, h))
    return tiles
