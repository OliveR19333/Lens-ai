# START HERE — TNC Website Builder Go-Live Session

You are picking up the TNC website building service project. Everything
decided so far is locked and documented; this session's job is to EXECUTE
Phase A and go live. Read PROJECT-STATE.md for full context, then run
GO-LIVE-RUNBOOK.md top to bottom.

## What this project is

TNC sells custom websites as a managed membership service: TNC builds,
hosts, manages domains, runs SEO, and ships updates; clients pay monthly.
A premium-priced one-time buildout exists but is discouraged. Three tiers:
Standard, Motion, 3D Premium.

## Where things stand (end of last session)

- ✅ Full playbook written and merged into `tnc-website-builder/` on the
  branch `claude/tnc-website-builder-pipeline-55an2e` (PR #3 on
  OliveR19333/Lens-ai — merge it first if not merged)
- ✅ Business model locked: membership-first, managed everything
- ✅ Stack locked: React + Tailwind + React Bits + Anime.js v4; GSAP +
  Lenis for Motion tier; R3F + drei for 3D tier
- ✅ Infra decisions locked: Cloudflare Registrar (all client domains, TNC
  account) + Cloudflare Pages/Workers (production hosting, TNC account);
  Porkbun API v3 as registrar fallback; Higgsfield MCP for asset
  generation (`generate_image/video/3d`) and rapid build previews
- ✅ 3D standard locked: scroll-first, one hero 3D moment, sacred
  navigation, hard mobile budgets (3D-DESIGN-STANDARD.md)
- ❌ Nothing built yet: no starter template, no TNC site, no TNC accounts,
  no pricing numbers, no billing, no contract

## This session's mission (in order)

1. Merge PR #3 if still open
2. Execute GO-LIVE-RUNBOOK.md — build the starter, build TNC's own site
   through the full pipeline, deploy it live
3. Check off items in ../GAPS-AND-ROADMAP.md as they land

## Things Ryan must do himself (can't be done by the agent)

- Create the TNC Cloudflare account and buy the TNC domain
- Create the TNC GitHub org (or decide to keep using this account)
- Approve pricing numbers
- Stripe account (Phase B)

Ask for these early in the session so they're ready when needed.
