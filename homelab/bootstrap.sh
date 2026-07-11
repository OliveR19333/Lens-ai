#!/usr/bin/env bash
# TNC Render Rig bootstrap — run once on a fresh Ubuntu Server 24.04 install.
#   curl -fsSL <raw url>/homelab/bootstrap.sh -o bootstrap.sh && bash bootstrap.sh
# Idempotent: safe to re-run.
set -euo pipefail

echo "==> TNC Render Rig bootstrap starting"

# --- base packages ----------------------------------------------------------
sudo apt-get update -y
sudo apt-get install -y git ffmpeg curl build-essential unattended-upgrades

# --- Node 20 (via NodeSource) -----------------------------------------------
if ! command -v node >/dev/null || [ "$(node -v | cut -c2-3)" -lt 20 ]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
echo "==> node $(node -v), npm $(npm -v)"

# --- process manager + Claude Code ------------------------------------------
sudo npm install -g pm2 @anthropic-ai/claude-code
echo "==> pm2 + Claude Code installed"

# --- Tailscale (private network — SSH from anywhere, no port forwarding) -----
if ! command -v tailscale >/dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi

# --- keep the box awake + auto security updates ------------------------------
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo dpkg-reconfigure -f noninteractive unattended-upgrades

# --- working directories ------------------------------------------------------
mkdir -p "$HOME/work" "$HOME/tours"

echo ""
echo "==> Bootstrap complete. Two manual steps remain:"
echo ""
echo "  1. Connect Tailscale (prints a login link — open it on your Mac):"
echo "       sudo tailscale up --ssh"
echo ""
echo "  2. Log Claude Code into your account:"
echo "       claude"
echo ""
echo "  Then add your MCP servers + skills (see homelab/SETUP.md, 'One-time after bootstrap')."
