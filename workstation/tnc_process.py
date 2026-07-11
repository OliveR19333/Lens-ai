#!/usr/bin/env python3
"""
TNC GAS — local map processor.

Submits a folder of drone images (or the built-in sample dataset) to a WebODM
running locally at http://localhost:8000, waits for it to finish, and downloads
the orthophoto + elevation rasters to your Desktop.

    python3 tnc_process.py sample            # download + process the test set
    python3 tnc_process.py /path/to/images   # process your own image folder

Standard library only — no pip installs needed. Runs on the Mac where WebODM
is running.
"""
import getpass
import glob
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

WEBODM = "http://localhost:8000"
SAMPLE_URLS = [
    "https://github.com/OpenDroneMap/odm_data_aukerman/archive/refs/heads/master.zip",
    "https://github.com/OpenDroneMap/odm_data_aukerman/archive/refs/heads/main.zip",
]
IMG_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")


def log(msg):
    print(msg, flush=True)


def gather_images(arg):
    if arg == "sample":
        log("Downloading the sample drone dataset (~200 MB, one time)…")
        raw = None
        for url in SAMPLE_URLS:
            try:
                raw = urllib.request.urlopen(url, timeout=600).read()
                break
            except urllib.error.HTTPError:
                continue
        if raw is None:
            log("Could not download the sample dataset. Check your internet and retry.")
            sys.exit(1)
        dest = os.path.expanduser("~/Desktop/aukerman_sample")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            z.extractall(dest)
        root = dest
    else:
        root = os.path.expanduser(arg)
    imgs = [p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
            if p.lower().endswith(IMG_EXT)]
    return sorted(imgs)


def api_json(url, headers=None, fields=None):
    data = urllib.parse.urlencode(fields).encode() if fields is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def post_images(url, headers, options, image_paths):
    """Manual multipart upload of many images (stdlib, no requests dependency)."""
    boundary = uuid.uuid4().hex
    chunks = [f'--{boundary}\r\nContent-Disposition: form-data; name="options"\r\n\r\n{options}\r\n'.encode()]
    for p in image_paths:
        name = os.path.basename(p)
        head = (f'--{boundary}\r\nContent-Disposition: form-data; name="images"; '
                f'filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n')
        chunks.append(head.encode())
        with open(p, "rb") as fh:
            chunks.append(fh.read())
        chunks.append(b"\r\n")
    chunks.append(f'--{boundary}--\r\n'.encode())
    body = b"".join(chunks)
    h = dict(headers)
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read().decode())


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "sample"
    images = gather_images(arg)
    if not images:
        log("No images found. Check the folder path and try again.")
        sys.exit(1)
    log(f"Found {len(images)} images.")

    user = os.environ.get("WEBODM_USER") or input("WebODM username: ")
    pw = os.environ.get("WEBODM_PASS") or getpass.getpass("WebODM password: ")

    log("Signing in to WebODM…")
    try:
        token = api_json(f"{WEBODM}/api/token-auth/",
                         fields={"username": user, "password": pw})["token"]
    except urllib.error.HTTPError:
        log("Login failed — check the WebODM username/password you created at localhost:8000.")
        sys.exit(1)
    H = {"Authorization": f"JWT {token}"}

    proj_name = "TNC " + ("Sample" if arg == "sample" else os.path.basename(os.path.normpath(arg)))
    pid = api_json(f"{WEBODM}/api/projects/", headers=H, fields={"name": proj_name})["id"]
    log(f"Created project '{proj_name}' (#{pid}). Uploading {len(images)} images…")

    # dsm = surface (elevation/slopes), dtm = bare earth (grading/drainage).
    options = json.dumps([{"name": "dsm", "value": True}, {"name": "dtm", "value": True}])
    task = post_images(f"{WEBODM}/api/projects/{pid}/tasks/", H, options, images)
    tid = task["id"]
    log(f"Processing started (task {tid[:8]}). This takes a while — leave it running.")

    # Status codes: 10 queued, 20 running, 30 failed, 40 completed, 50 canceled.
    while True:
        t = api_json(f"{WEBODM}/api/projects/{pid}/tasks/{tid}/", headers=H)
        code = t.get("status")
        prog = int((t.get("running_progress") or 0) * 100)
        log(f"  …status {code}, {prog}%")
        if code == 40:
            break
        if code in (30, 50):
            log("Processing failed: " + str(t.get("last_error") or "unknown"))
            sys.exit(1)
        time.sleep(20)

    out = os.path.expanduser(f"~/Desktop/TNC_map_{tid[:8]}")
    os.makedirs(out, exist_ok=True)
    log("Done! Downloading results…")
    for asset in ("orthophoto.tif", "dsm.tif", "dtm.tif"):
        try:
            req = urllib.request.Request(
                f"{WEBODM}/api/projects/{pid}/tasks/{tid}/download/{asset}", headers=H)
            with urllib.request.urlopen(req, timeout=600) as r:
                with open(os.path.join(out, asset), "wb") as f:
                    f.write(r.read())
            log(f"  saved {asset}")
        except Exception as exc:  # noqa: BLE001
            log(f"  ({asset} not available: {exc})")
    log(f"\nYour map is in:  {out}")
    log("Open the .tif files in QGIS to view, measure, and overlay your parcel data.")


if __name__ == "__main__":
    main()
