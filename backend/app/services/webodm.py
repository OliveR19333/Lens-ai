"""WebODM REST client (spec §7).

Drives a self-hosted WebODM instance through the documented pipeline (spec §7.2):

    1. POST /api/token-auth/                 → JWT token
    2. POST /api/projects/                   → project id
    3. POST /api/projects/{id}/tasks/        → task uuid  (images[] + options)
    4. GET  /api/projects/{id}/tasks/{uuid}/ → status (40 = COMPLETED)
    5. GET  .../download/{orthophoto,dsm,dtm}.tif

The network layer is isolated behind three small methods (`_post_json`,
`_get_json`, `_get_bytes`) that use ``httpx`` (imported lazily). Tests subclass
the client and override those three, so the orchestration logic — option
building, status mapping, the polling loop, output download — is fully
unit-tested without httpx or a live WebODM.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

# NOTE: app.config / app.storage are imported lazily inside the functions that
# need them so this module stays importable (and unit-testable) without the
# pydantic-settings stack.

logger = logging.getLogger("gas.webodm")

# WebODM task status codes (spec §7.2; 40 = COMPLETED).
STATUS_QUEUED = 10
STATUS_RUNNING = 20
STATUS_FAILED = 30
STATUS_COMPLETED = 40
STATUS_CANCELED = 50

_STATUS_LABELS = {
    STATUS_QUEUED: "queued",
    STATUS_RUNNING: "running",
    STATUS_FAILED: "failed",
    STATUS_COMPLETED: "completed",
    STATUS_CANCELED: "canceled",
}

# Processing options (spec §7.1): produce DSM + DTM at 2 cm/px ortho resolution.
PROCESSING_OPTIONS = [
    {"name": "dsm", "value": True},
    {"name": "dtm", "value": True},
    {"name": "orthophoto-resolution", "value": 2},
]

# Output assets we retrieve (spec §7.3) → local filenames.
ASSETS = {
    "orthophoto.tif": "ortho.tif",
    "dsm.tif": "dsm.tif",
    "dtm.tif": "dtm.tif",
}


def status_label(code: Optional[int]) -> str:
    return _STATUS_LABELS.get(code, "unknown")


def is_terminal(code: Optional[int]) -> bool:
    return code in (STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELED)


def is_success(code: Optional[int]) -> bool:
    return code == STATUS_COMPLETED


def build_task_options() -> List[dict]:
    """The options JSON posted with a task (spec §7.2 step 3)."""
    return list(PROCESSING_OPTIONS)


def asset_download_path(project_id: int, task_uuid: str, asset: str) -> str:
    return f"/projects/{project_id}/tasks/{task_uuid}/download/{asset}"


class WebODMError(Exception):
    pass


class WebODMClient:
    """Thin WebODM API client. Network methods are overridable for testing."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        timeout: float = 120.0,
    ):
        # Only touch settings (pydantic) when a value wasn't supplied — keeps the
        # client constructible in tests without the settings stack.
        if base_url is None or username is None or password is None:
            from app.config import get_settings

            settings = get_settings()
            base_url = base_url or settings.webodm_base_url
            username = username or settings.webodm_username
            password = password or settings.webodm_password
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self._token: Optional[str] = None

    # ---- network layer (override in tests) ----
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"JWT {self._token}"} if self._token else {}

    def _client(self):
        import httpx  # lazy

        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _post_json(self, path: str, *, json=None, data=None, files=None) -> dict:
        with self._client() as c:
            r = c.post(path, json=json, data=data, files=files, headers=self._headers())
            r.raise_for_status()
            return r.json()

    def _get_json(self, path: str) -> dict:
        with self._client() as c:
            r = c.get(path, headers=self._headers())
            r.raise_for_status()
            return r.json()

    def _get_bytes(self, path: str) -> bytes:
        with self._client() as c:
            r = c.get(path, headers=self._headers())
            r.raise_for_status()
            return r.content

    # ---- pipeline steps (spec §7.2) ----
    def authenticate(self) -> str:
        data = self._post_json(
            "/token-auth/", data={"username": self.username, "password": self.password}
        )
        token = data.get("token")
        if not token:
            raise WebODMError("WebODM auth failed: no token returned.")
        self._token = token
        return token

    def create_project(self, name: str) -> int:
        data = self._post_json("/projects/", json={"name": name})
        pid = data.get("id")
        if pid is None:
            raise WebODMError("WebODM create_project failed: no id returned.")
        return int(pid)

    def submit_task(self, project_id: int, image_paths: List[str]) -> str:
        """Upload images + options, start processing, return the task uuid."""
        import json as _json

        files = []
        opened = []
        try:
            for p in image_paths:
                fh = open(p, "rb")
                opened.append(fh)
                files.append(("images", (Path(p).name, fh, "image/jpeg")))
            files.append(("options", (None, _json.dumps(build_task_options()))))
            data = self._post_json(f"/projects/{project_id}/tasks/", files=files)
        finally:
            for fh in opened:
                fh.close()
        uuid = data.get("id")
        if not uuid:
            raise WebODMError("WebODM submit_task failed: no task id returned.")
        return str(uuid)

    def get_task(self, project_id: int, task_uuid: str) -> dict:
        return self._get_json(f"/projects/{project_id}/tasks/{task_uuid}/")

    def task_status(self, project_id: int, task_uuid: str) -> Optional[int]:
        info = self.get_task(project_id, task_uuid)
        status = info.get("status")
        # WebODM sometimes nests the code under {"status": {"code": 40}}.
        if isinstance(status, dict):
            return status.get("code")
        return status

    def poll_until_done(
        self,
        project_id: int,
        task_uuid: str,
        *,
        interval_s: float = 15.0,
        max_attempts: int = 240,
        sleep: Callable[[float], None] = time.sleep,
    ) -> int:
        """Poll task status until terminal (spec §7.2 step 4). Returns the code."""
        for _ in range(max_attempts):
            code = self.task_status(project_id, task_uuid)
            if is_terminal(code):
                return code
            sleep(interval_s)
        raise WebODMError(f"WebODM task {task_uuid} did not finish in time.")

    def download_outputs(self, project_id: int, task_uuid: str, dest_dir: Path) -> Dict[str, str]:
        """Download ortho/dsm/dtm GeoTIFFs (spec §7.2 step 5, §7.3)."""
        dest_dir.mkdir(parents=True, exist_ok=True)
        out: Dict[str, str] = {}
        for asset, local_name in ASSETS.items():
            try:
                content = self._get_bytes(asset_download_path(project_id, task_uuid, asset))
            except Exception as exc:  # noqa: BLE001 — DSM/DTM optional if disabled
                logger.warning("WebODM asset %s unavailable: %s", asset, exc)
                continue
            path = dest_dir / local_name
            path.write_bytes(content)
            out[local_name] = str(path)
        return out

    def run_pipeline(
        self,
        name: str,
        image_paths: List[str],
        dest_dir: Path,
        *,
        sleep: Callable[[float], None] = time.sleep,
        interval_s: float = 15.0,
    ) -> Dict[str, str]:
        """Full auth→create→submit→poll→download (spec §7.2). Returns asset paths."""
        self.authenticate()
        project_id = self.create_project(name)
        task_uuid = self.submit_task(project_id, image_paths)
        code = self.poll_until_done(project_id, task_uuid, sleep=sleep, interval_s=interval_s)
        if not is_success(code):
            raise WebODMError(f"WebODM task ended with status {status_label(code)} ({code}).")
        outputs = self.download_outputs(project_id, task_uuid, dest_dir)
        outputs["_webodm_project_id"] = str(project_id)
        outputs["_webodm_task_id"] = task_uuid
        return outputs


# ---- helpers used by the upload endpoint (kept from the original scaffold) ----
async def stage_uploads(project_id: str, images) -> List[str]:
    """Persist uploaded images to the project's storage dir; return their paths."""
    from app.storage import project_dir

    dest = project_dir(project_id) / "images"
    dest.mkdir(parents=True, exist_ok=True)
    saved: List[str] = []
    for img in images:
        out = dest / Path(img.filename).name
        data = await img.read()
        out.write_bytes(data)
        saved.append(str(out))
    logger.info("Staged %d images for project %s", len(saved), project_id)
    return saved


async def stage_video_frames(project_id: str, video, fps: float = 1.0) -> List[str]:
    """Save an uploaded flight video and extract still frames at ``fps`` frames per
    second as the image set for photogrammetry. Returns the frame paths.

    Continuous video guarantees coverage (no gaps from a missed interval shot);
    extracting ~1-2 fps gives plenty of overlapping stills for the orthomosaic.
    Requires ``ffmpeg`` on the server (installed in the backend image).
    """
    import shutil
    import subprocess

    from app.storage import project_dir

    if not 0.1 <= fps <= 5.0:
        raise WebODMError("Frame rate must be between 0.1 and 5 fps.")
    if not shutil.which("ffmpeg"):
        raise WebODMError("ffmpeg is not installed on the server; cannot extract video frames.")

    pdir = project_dir(project_id)
    pdir.mkdir(parents=True, exist_ok=True)
    raw = pdir / f"flight_video{Path(video.filename or 'video.mp4').suffix or '.mp4'}"
    raw.write_bytes(await video.read())

    dest = pdir / "images"
    dest.mkdir(parents=True, exist_ok=True)
    # Clear any prior frames so re-uploads don't mix old + new.
    for old in dest.glob("frame_*.jpg"):
        old.unlink()

    pattern = str(dest / "frame_%05d.jpg")
    cmd = ["ffmpeg", "-y", "-i", str(raw), "-vf", f"fps={fps}", "-q:v", "2", pattern]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise WebODMError(f"Video frame extraction failed: {(proc.stderr or '')[-400:]}")

    frames = sorted(str(p) for p in dest.glob("frame_*.jpg"))
    if not frames:
        raise WebODMError("No frames could be extracted from that video.")
    logger.info("Extracted %d frames (%.1f fps) from video for project %s", len(frames), fps, project_id)
    return frames


def get_task_status(webodm_project_id: int, task_uuid: str) -> str:
    """Convenience used by the project status endpoint."""
    try:
        client = WebODMClient()
        client.authenticate()
        return status_label(client.task_status(webodm_project_id, task_uuid))
    except Exception as exc:  # noqa: BLE001
        logger.info("WebODM status check failed: %s", exc)
        return "unknown"
