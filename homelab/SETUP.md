# TNC Render Rig — turn an old PC into your 24/7 workhorse

Goal: a headless ("dumb") PC that sits in a corner with only a power cable
and ethernet, fully controlled from your Mac. It runs Claude Code, the
walkthrough pipeline, ffmpeg, and stores every tour. The client-facing stuff
(proposal portal, dashboard) lives on Railway — if this box ever goes down,
no client notices.

## The stack split

| Where | What runs there | Why |
|-------|-----------------|-----|
| **Railway** (~$5/mo) | Proposal portal, dashboard | Always up, clients see it |
| **The PC** (this guide) | Claude Code, RE Walkthrough Pro, ffmpeg, tour storage (1TB) | Free compute, big storage, can be down without harm |
| **Your Mac** | Nothing but a terminal | The cockpit — you SSH in from anywhere |

Your specs (8GB RAM, 1TB disk) are plenty: the AI video renders in
Higgsfield's cloud, not on this box. The PC only orchestrates, downloads
clips, and stitches — light work.

## Phase A — on your Mac (10 min)

1. Download **Ubuntu Server 24.04 LTS** (the server ISO, not desktop):
   https://ubuntu.com/download/server
2. Flash it to a USB stick (8GB+) with **balenaEtcher** (free):
   https://etcher.balena.io

## Phase B — at the PC, one time only (20 min)

You need a keyboard + monitor plugged in ONCE. After this, never again.

1. **BIOS first:** boot and mash `F2`/`Del` to enter BIOS. Set:
   - Boot order: USB first (for the install)
   - **"Restore on AC Power Loss" → Power On** (so it self-revives after outages)
2. Boot from the USB → Ubuntu Server installer:
   - Accept defaults (whole disk, no LVM questions needed — default is fine)
   - Hostname: `tnc-rig`, user: `tnc`, a strong password
   - ✅ **CHECK "Install OpenSSH server"** — this is the critical box
   - Skip all the optional snaps
3. Reboot, pull the USB. When you see the login prompt, type
   `ip a` after logging in and note the IP address (looks like `192.168.x.x`).
4. Unplug keyboard and monitor. The PC is now "dumb." Put it in its corner.

## Phase C — back on your Mac (10 min, mostly automated)

```bash
# 1. Get in (use the IP from Phase B)
ssh tnc@192.168.x.x

# 2. Pull the bootstrap script and run it
curl -fsSL https://raw.githubusercontent.com/OliveR19333/Lens-ai/claude/photo-upload-prep-bhz1kd/homelab/bootstrap.sh -o bootstrap.sh
bash bootstrap.sh
```

The script installs: Node 20, ffmpeg, git, Tailscale, pm2, Claude Code,
and creates the `~/tours` + `~/work` directories. It prints a Tailscale
login link at the end — open it on your Mac and approve the machine.

## Phase D — access from anywhere (5 min)

Tailscale (free) puts your Mac and the rig on a private network, so
`ssh tnc@tnc-rig` works from home, a coffee shop, anywhere — no router
port-forwarding, nothing exposed to the internet.

1. Install Tailscale on your Mac too: https://tailscale.com/download
2. Log both devices into the same (free) account.
3. From then on: `ssh tnc@tnc-rig` from any network. That's the whole trick.

## Daily use

```bash
ssh tnc@tnc-rig          # from your Mac, from anywhere
cd ~/work
claude                    # Claude Code on the rig, with all your skills
/re-walkthrough-pro       # tours render while your Mac sleeps
```

Finished tours land in `~/tours`. Pull one to your Mac with:
`scp tnc@tnc-rig:~/tours/<file>.mp4 ~/Desktop/`

## One-time after bootstrap

On the rig, sign in and add the MCP servers (same as your Mac):

```bash
claude                    # first run: log in to your Claude account
claude mcp add apify --env APIFY_TOKEN=<token> -- npx -y @apify/actors-mcp-server
# Higgsfield MCP: same setup command you used from higgsfield.ai/mcp
npx re-walkthrough-pro install
npx ugc-factory install

# TNC video factory (drone + AI stitching, shorts, captions) — installed by
# claude-os-starter/setup.sh. Also clone the upstream reference library it
# consults for advanced recipes:
git clone https://github.com/Bomx/super-video-maker-skill ~/work/super-video-maker-skill

# Drop your D-log conversion LUT (.cube) into ~/work/luts/
mkdir -p ~/work/luts
```

## Troubleshooting

- **Can't SSH?** The rig and Mac must be on the same network for Phase C
  (before Tailscale). Check the IP again — it can change; Tailscale fixes
  this permanently in Phase D.
- **Rig unreachable after power outage?** You skipped the BIOS
  "Restore on AC Power" setting in Phase B.
- **Disk filling up?** `du -sh ~/tours/*` and delete delivered tours —
  or keep everything; 1TB ≈ 500+ finished tours.
