"""Tests for the WebODM client orchestration (spec §7.2).

A FakeWebODMClient overrides the three network methods, so the pipeline logic
(auth, task submission, status polling, output download) is exercised without
httpx or a live WebODM server."""
import pytest

from app.services import webodm
from app.services.webodm import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_QUEUED,
    STATUS_RUNNING,
    WebODMClient,
    WebODMError,
    asset_download_path,
    build_task_options,
    is_success,
    is_terminal,
    status_label,
)


# ---- pure helpers ----
def test_task_options_request_dsm_dtm_and_resolution():
    opts = {o["name"]: o["value"] for o in build_task_options()}
    assert opts["dsm"] is True
    assert opts["dtm"] is True
    assert opts["orthophoto-resolution"] == 2


def test_status_helpers():
    assert status_label(STATUS_COMPLETED) == "completed"
    assert status_label(999) == "unknown"
    assert is_terminal(STATUS_COMPLETED) and is_terminal(STATUS_FAILED)
    assert not is_terminal(STATUS_RUNNING)
    assert is_success(STATUS_COMPLETED)
    assert not is_success(STATUS_FAILED)


def test_asset_download_path():
    p = asset_download_path(42, "abc", "orthophoto.tif")
    assert p == "/projects/42/tasks/abc/download/orthophoto.tif"


# ---- orchestration with a fake transport ----
class FakeWebODMClient(WebODMClient):
    def __init__(self, status_sequence, **kw):
        super().__init__(base_url="http://fake", username="u", password="p")
        self._status_sequence = list(status_sequence)
        self.calls = []

    def _post_json(self, path, *, json=None, data=None, files=None):
        self.calls.append(("POST", path))
        if path == "/token-auth/":
            return {"token": "tok123"}
        if path == "/projects/":
            return {"id": 42}
        if path.endswith("/tasks/"):
            return {"id": "task-uuid"}
        return {}

    def _get_json(self, path):
        self.calls.append(("GET", path))
        code = self._status_sequence.pop(0) if self._status_sequence else STATUS_COMPLETED
        return {"status": code}

    def _get_bytes(self, path):
        self.calls.append(("BYTES", path))
        return b"GEOTIFF-BYTES"


def test_run_pipeline_happy_path(tmp_path):
    client = FakeWebODMClient([STATUS_QUEUED, STATUS_RUNNING, STATUS_COMPLETED])
    img = tmp_path / "a.jpg"
    img.write_bytes(b"fake")
    out = client.run_pipeline("proj", [str(img)], tmp_path / "out", sleep=lambda s: None, interval_s=0)
    assert out["_webodm_project_id"] == "42"
    assert out["_webodm_task_id"] == "task-uuid"
    # ortho/dsm/dtm all "downloaded"
    assert out["ortho.tif"].endswith("ortho.tif")
    assert (tmp_path / "out" / "dsm.tif").exists()
    assert client._token == "tok123"


def test_run_pipeline_raises_on_failed_task(tmp_path):
    client = FakeWebODMClient([STATUS_RUNNING, STATUS_FAILED])
    img = tmp_path / "a.jpg"
    img.write_bytes(b"fake")
    with pytest.raises(WebODMError):
        client.run_pipeline("proj", [str(img)], tmp_path / "out", sleep=lambda s: None, interval_s=0)


def test_poll_times_out(tmp_path):
    client = FakeWebODMClient([STATUS_RUNNING] * 5)
    with pytest.raises(WebODMError):
        client.poll_until_done(42, "t", interval_s=0, max_attempts=3, sleep=lambda s: None)


def test_task_status_unwraps_nested_code():
    class Nested(FakeWebODMClient):
        def _get_json(self, path):
            return {"status": {"code": STATUS_COMPLETED}}

    client = Nested([])
    assert client.task_status(1, "t") == STATUS_COMPLETED
