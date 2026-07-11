"""Filesystem artifact storage (spec §4.1 — local FS or S3-compatible).

Phase 1 uses the local filesystem under ``STORAGE_DIR``. Swap this module for an
S3 client to move artifacts off-box without touching the routers.
"""
from __future__ import annotations

import os
from pathlib import Path

from app.config import get_settings


def _storage_root() -> Path:
    root = Path(get_settings().storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def kmz_path(mission_id: str) -> Path:
    return _storage_root() / "missions" / f"{mission_id}.kmz"


def save_kmz(mission_id: str, data: bytes) -> Path:
    path = kmz_path(mission_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def project_dir(project_id: str) -> Path:
    path = _storage_root() / "projects" / project_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def exists(path: os.PathLike | str) -> bool:
    return Path(path).exists()
