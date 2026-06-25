"""Map output & print scaling (spec §9).

``scale`` is implemented (pure stdlib). ``flat_map`` and ``elevation_map`` are
structured stubs that depend on rasterio/matplotlib (Phase 2/3).
"""
from .scale import PrintScale, compute_print_scale  # noqa: F401
