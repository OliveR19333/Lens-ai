---
tags: [playbook, real-estate, video]
date: 2026-07-11
---

# Playbook — Zillow listing → cinematic walkthrough

The production pipeline sold as part of [[tnc-offer]]. All open source /
public tooling; the only costs are Apify (sub-cent per scrape) and
Higgsfield credits (~$1–5 per finished tour).

## One-time setup (done once per machine)
```bash
brew install ffmpeg
npx re-walkthrough-pro install
claude mcp add apify --env APIFY_TOKEN=<token> -- npx -y @apify/actors-mcp-server
# Higgsfield MCP: follow https://higgsfield.ai/mcp
```
Keys live in a password manager, never in this vault.

## Per-tour run
1. Open Claude Code, run `/re-walkthrough-pro`
2. Paste the Zillow URL (or ask it to find listings in a zip code)
3. Approve the room curation + cost estimate it shows
4. Output lands in `listing-walkthroughs/<address>/final/`
5. Review against its quality checklist, deliver 16:9 (+9:16 for social)

## Pricing math
Cost per tour ≈ $1–5. Sell at $500+. Note actual numbers per delivery in
the client's note in `30-Clients/`.
