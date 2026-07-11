"""DJI Waypoint (WPML 2.0) mission generation.

Native Python implementation of the KMZ builder described in spec §6. Depends
only on the Python standard library so it runs client-side-equivalent and in CI
without GIS/heavy dependencies.
"""
from .kmz_builder import build_mission_kmz, MissionParams  # noqa: F401
