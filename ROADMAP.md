# TNC Build Roadmap — state + next actions

> **Master context:** this roadmap is the media/agentic slice of the
> **TNC MASTER BUILD PLAN v2** (Google Doc "TNC MASTER BUILD PLAN — v2",
> July 2026). That plan governs: five public wings, /vendors + /brief +
> /care sections, revenue architecture, and the infra decision —
> **one VPS running Coolify (+ Plausible, Listmonk, Ghost, Cal.com, n8n)**
> hosting the server suite. **Reconciled hosting decision (with PR #3):**
> hybrid — Cloudflare Registrar + Pages serves all static sites (client
> sites + TNC site); the Coolify VPS runs everything with a backend
> (Plausible, Listmonk, Ghost, n8n, the proposal portal + QC dashboard,
> trend-watcher cron). Railway is superseded. The render rig (homelab/)
> is unchanged — the production engine behind the drone-media wing.
> Sibling project: **PR #3** (`tnc-website-builder/`) — the website
> service playbook + go-live runbook; its handoff docs cross-reference
> this file. Merge BOTH PRs so main shows the whole estate.

Living checklist for the full TNC stack build. Everything marked DONE is
committed on this branch (PR #2). Resume point for any future session:
read this file first, then vault playbooks in `claude-os-starter/vault/`.

## DONE (shipped on PR #2)
- [x] Claude OS starter kit: `claude-os-starter/` — vault, CLAUDE.md,
      one-command `setup.sh`
- [x] Skills: `/brain`, `/plan-today`, `/tnc-video-factory`
- [x] Interactive proposal portal: `/admin` + `/p/:token` (toggle line items,
      live totals, BEFORE/AFTER image swap, submissions) — tested end-to-end
- [x] Render-rig kit: `homelab/SETUP.md` + `bootstrap.sh` (Ubuntu, Node 20,
      ffmpeg, Tailscale, pm2, Claude Code, rclone Drive sync)
- [x] Vault playbooks: AI walkthrough, drone-hybrid tour (premium tier),
      longform estate film (flagship), Drive asset map
- [x] Verified accounts: Higgsfield connected (Plus, ~2,010 credits;
      365-day unlimited image models; 7-day unlimited Kling 3.0 +
      Seedance 2.0 Std video expiring ~Jul 17 — SPRINT WINDOW)

## RYAN'S ERRANDS (nothing blocks on code)
- [ ] Apify account + token (console.apify.com → Settings → Integrations) — THE blocker for tours
- [ ] ElevenLabs free account (SFX + music MCP)
- [ ] Download DJI D-Log M → Rec709 LUT (free, dji.com) → Drive `LUT/` folder
- [ ] Fill vault: `tnc-offer.md`, 5 content ideas, this week's metrics
- [ ] Cancel CapCut Pro (replaced by Palmier + Resolve free + factory)
- [ ] Install Palmier on Mac (github.com/palmier-io/palmier-pro releases)
- [ ] USB stick + 30 min for the rig install (homelab/SETUP.md phases A–B)
- [ ] Confirm whether 7-day unlimited video renews monthly (Higgsfield
      subscription page → tap the Kling v3.0 row)

## NEXT BUILD SESSION (in order)
1. **First tour sprint** (needs Apify token): run `/re-walkthrough-pro` on a
   real listing; measure exact credit burn (balance before/after); batch
   5–10 pitch tours inside the unlimited window
2. **First live proposal**: generate before/after images via Higgsfield
   (unlimited Nano Banana), build a demo proposal in `/admin`, send link
3. **Railway deploy**: portal to production (set ADMIN_KEY, add volume or
   wire a small DB for `data/`), custom domain
4. **Rig day** (needs Ryan at the PC once): phases B–D of homelab/SETUP.md,
   then rclone asset sync + skills install
5. **Dashboard phase**: convert Lens-ai homepage into the war-room
   (vitals from stats.json, command deck buttons → skills, BHAG bar)
6. **Longform automation**: wire DaVinci MCP + the Resolve script suite
   (Drive: Project_Template scripts) into an 8hr→2hr estate-film pipeline
7. **Music library**: fill `10_MUSIC/longform_estate/` (Artlist downloads
   or ElevenLabs compose_music)

## STACK MAP (who does what)
Railway = client-facing (portal, dashboard) · Rig = factory (tours, shorts,
stitching, storage) · Mac = cockpit (Palmier finishing, Resolve grading via
DaVinci MCP) · Drive = asset library (LUTs, scripts, templates, footage) ·
Vault = memory · Higgsfield MCP = all generation (never Replicate/OpenAI/
HeyGen) · Apify MCP = listing scrapes.
