#!/bin/bash
# ============================================================================
#  TNC-GAS — Make Map  (double-click me)
#  Pick a flight folder that contains the DJI video + .SRT, and this geotags the
#  frames, builds the map in WebODM, and drops the finished map in that folder.
# ============================================================================
TOOLS="$HOME/TNC-GAS/tools"

echo "=================================="
echo " TNC-GAS — Make Map"
echo "=================================="

# 1. Pick the flight folder (Finder dialog)
FOLDER=$(osascript -e 'POSIX path of (choose folder with prompt "Pick the flight folder (contains the video + .SRT)")' 2>/dev/null)
[ -z "$FOLDER" ] && exit 0
FOLDER="${FOLDER%/}"
echo "Flight folder: $FOLDER"

# 2. Make sure the map engine is running (start Docker + WebODM if needed)
if ! curl -s -o /dev/null http://localhost:8000; then
  echo "Starting the map engine (Docker + WebODM)…"
  open -a Docker 2>/dev/null
  open -a "WebODM Manager" 2>/dev/null || open -a WebODM 2>/dev/null
  for i in $(seq 1 60); do
    curl -s -o /dev/null http://localhost:8000 && break
    sleep 3
  done
fi
if ! curl -s -o /dev/null http://localhost:8000; then
  echo "X  WebODM isn't responding at localhost:8000."
  echo "   Open Docker + WebODM, wait for them to start, then run me again."
  read -n 1 -s -r -p "Press any key to close."; exit 1
fi

# 3. Geotag the frames
echo "Extracting + geotagging frames…"
python3 "$TOOLS/tnc_video.py" "$FOLDER" || { echo "X  Frame/geotag step failed."; read -n 1 -s -r; exit 1; }

# 4. Optional saved WebODM login (line 1 = username, line 2 = password)
if [ -f "$TOOLS/webodm.txt" ]; then
  export WEBODM_USER=$(sed -n 1p "$TOOLS/webodm.txt")
  export WEBODM_PASS=$(sed -n 2p "$TOOLS/webodm.txt")
fi

# 5. Build the map
echo "Building the map (this takes a while — leave it running)…"
python3 "$TOOLS/tnc_process.py" "$FOLDER/frames" || { echo "X  Processing failed."; read -n 1 -s -r; exit 1; }

# 6. Move the map into the flight folder and open it
NEWMAP=$(ls -dt "$HOME/Desktop/TNC_map_"* 2>/dev/null | head -1)
if [ -n "$NEWMAP" ]; then
  mv "$NEWMAP" "$FOLDER/map"
  echo "Map saved in: $FOLDER/map"
  open "$FOLDER/map"
fi
echo "DONE.  Open orthophoto.tif in QGIS to measure."
read -n 1 -s -r -p "Press any key to close."
