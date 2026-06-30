#!/usr/bin/env python3
"""
TNC GAS — extract geotagged still frames from a DJI flight video + .SRT.

    python3 tnc_video.py ~/TNC-GAS/jobs/2026/mike-white-210 [fps]

Reads the per-frame GPS from the DJI .SRT, pulls still frames from the video at
`fps` (default 1), and writes the matching GPS into each frame's EXIF — so
WebODM can georeference the map and it lands on the real parcel. Output frames
go in a `frames/` subfolder, ready for tnc_process.py.

Needs ffmpeg + exiftool:  brew install ffmpeg exiftool
"""
import bisect
import glob
import os
import re
import shutil
import subprocess
import sys


def parse_srt(path):
    """Return sorted [(t_seconds, lat, lon, abs_alt), ...] from a DJI .SRT."""
    text = open(path, encoding="utf-8", errors="ignore").read()
    out = []
    for block in re.split(r"\n\s*\n", text):
        tm = re.search(r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s*-->", block)
        lat = re.search(r"latitude:\s*([-\d.]+)", block)
        lon = re.search(r"longitude:\s*([-\d.]+)", block)
        alt = re.search(r"abs_alt:\s*([-\d.]+)", block)
        if tm and lat and lon:
            h, m, s, ms = map(int, tm.groups())
            t = h * 3600 + m * 60 + s + ms / 1000.0
            out.append((t, float(lat.group(1)), float(lon.group(1)),
                        float(alt.group(1)) if alt else 0.0))
    out.sort()
    return out


def nearest(entries, times, t):
    i = bisect.bisect_left(times, t)
    cands = []
    if i < len(entries):
        cands.append(entries[i])
    if i > 0:
        cands.append(entries[i - 1])
    return min(cands, key=lambda e: abs(e[0] - t))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tnc_video.py <job-folder> [fps]")
        sys.exit(1)
    folder = os.path.expanduser(sys.argv[1])
    fps = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    vids = glob.glob(os.path.join(folder, "*.MP4")) + glob.glob(os.path.join(folder, "*.mp4"))
    srts = glob.glob(os.path.join(folder, "*.SRT")) + glob.glob(os.path.join(folder, "*.srt"))
    if not vids or not srts:
        print("Need a .MP4 and a .SRT in:", folder)
        sys.exit(1)
    for tool in ("ffmpeg", "exiftool"):
        if not shutil.which(tool):
            print(f"Missing {tool}. Install with:  brew install {tool}")
            sys.exit(1)

    video, srt = vids[0], srts[0]
    entries = parse_srt(srt)
    if not entries:
        print("No GPS found in the SRT.")
        sys.exit(1)
    times = [e[0] for e in entries]
    print(f"Parsed {len(entries)} GPS points. First fix: {entries[0][1]:.6f}, {entries[0][2]:.6f}")

    out = os.path.join(folder, "frames")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    print(f"Extracting frames at {fps} fps…")
    subprocess.run(["ffmpeg", "-y", "-i", video, "-vf", f"fps={fps}", "-q:v", "2",
                    os.path.join(out, "frame_%05d.jpg")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frames = sorted(glob.glob(os.path.join(out, "frame_*.jpg")))
    print(f"Extracted {len(frames)} frames. Geotagging…")

    for idx, fp in enumerate(frames):
        t = idx / fps
        _, lat, lon, alt = nearest(entries, times, t)
        subprocess.run([
            "exiftool", "-overwrite_original",
            f"-GPSLatitude={abs(lat)}", f"-GPSLatitudeRef={'N' if lat >= 0 else 'S'}",
            f"-GPSLongitude={abs(lon)}", f"-GPSLongitudeRef={'E' if lon >= 0 else 'W'}",
            f"-GPSAltitude={abs(alt)}", f"-GPSAltitudeRef={'0' if alt >= 0 else '1'}",
            fp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"\nDone — {len(frames)} geotagged frames in:\n  {out}")
    print("Now process them into a map:")
    print(f"  python3 ~/TNC-GAS/tools/tnc_process.py '{out}'")


if __name__ == "__main__":
    main()
