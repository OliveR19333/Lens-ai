#!/bin/bash
# ============================================================================
#  TNC GAS — DJI RC 2 Mission Installer (macOS)
#  Double-click this to push the latest mapping mission onto a connected RC 2.
#
#  ONE-TIME SETUP (do once — see /tools/SETUP.txt on your app for full details):
#    1. Install adb:  brew install android-platform-tools
#    2. On the RC 2: enable Developer Options (tap the build/version number 5x),
#       turn ON "USB debugging", plug into the Mac, tap "Allow".
#    3. In DJI Fly -> Waypoint, make ONE mission with a dummy point and save it.
#       That's the placeholder this tool overwrites. Make it once, reuse forever.
#
#  EACH MISSION:
#    AirDrop the .kmz from your iPhone to this Mac, then double-click this file.
# ============================================================================
set -uo pipefail

WP_DIR="/sdcard/Android/data/dji.go.v5/files/waypoint"
DOWNLOADS="$HOME/Downloads"

pause() { echo; read -n 1 -s -r -p "Press any key to close this window."; echo; }

echo "============================================"
echo " TNC GAS — DJI RC 2 Mission Installer"
echo "============================================"
echo

# --- locate adb (Homebrew installs to /opt/homebrew on Apple Silicon) ---------
ADB="$(command -v adb 2>/dev/null || true)"
if [ -z "$ADB" ]; then
  for p in /opt/homebrew/bin/adb /usr/local/bin/adb; do
    [ -x "$p" ] && ADB="$p" && break
  done
fi
if [ -z "$ADB" ]; then
  echo "X  'adb' is not installed yet (one-time)."
  echo "   Open Terminal, paste this, press Enter, then run me again:"
  echo
  echo "       brew install android-platform-tools"
  echo
  echo "   (No Homebrew? See SETUP.txt on your app's /tools page.)"
  pause; exit 1
fi

# --- newest KMZ in Downloads (where AirDrop lands) ----------------------------
KMZ="$(ls -t "$DOWNLOADS"/*.kmz 2>/dev/null | head -n1 || true)"
if [ -z "$KMZ" ]; then
  echo "X  No .kmz found in your Downloads folder."
  echo "   AirDrop the mission from your iPhone to this Mac first, then run me again."
  pause; exit 1
fi
echo ">  Mission file: $(basename "$KMZ")"

# --- device check -------------------------------------------------------------
"$ADB" start-server >/dev/null 2>&1 || true
DEV_COUNT="$("$ADB" devices | awk 'NR>1 && $2=="device"' | wc -l | tr -d ' ')"
if [ "$DEV_COUNT" = "0" ]; then
  if "$ADB" devices | awk 'NR>1 && $2=="unauthorized"' | grep -q .; then
    echo "X  RC 2 is plugged in but not authorized."
    echo "   Look at the RC 2 screen and tap 'Allow' on the USB debugging prompt,"
    echo "   then run me again."
  else
    echo "X  RC 2 not detected."
    echo "   - Plug the RC 2 into this Mac with a USB-C cable"
    echo "   - Make sure USB debugging is ON (one-time setup)"
  fi
  pause; exit 1
fi

# --- newest waypoint folder on the controller ---------------------------------
FOLDER="$("$ADB" shell "ls -t $WP_DIR 2>/dev/null" | tr -d '\r' | head -n1 || true)"
if [ -z "$FOLDER" ]; then
  echo "X  No waypoint mission folder found on the RC 2."
  echo "   In DJI Fly -> Waypoint, create and SAVE one mission first (the placeholder),"
  echo "   then run me again."
  pause; exit 1
fi

# --- existing .kmz name inside it (the name DJI expects) ----------------------
TARGET="$("$ADB" shell "ls $WP_DIR/$FOLDER/*.kmz 2>/dev/null" | tr -d '\r' | head -n1 || true)"
if [ -z "$TARGET" ]; then
  TARGET="$WP_DIR/$FOLDER/$FOLDER.kmz"
fi

echo ">  Target mission slot: $FOLDER"
echo ">  Installing..."
if "$ADB" push "$KMZ" "$TARGET" >/dev/null 2>&1; then
  echo
  echo "============================================"
  echo " DONE!  Reopen DJI Fly -> Waypoint on the"
  echo " RC 2 and your mapping mission is loaded."
  echo "============================================"
else
  echo "X  Transfer failed. Unplug/replug the RC 2, confirm 'Allow' on its screen,"
  echo "   and try again."
fi
pause
