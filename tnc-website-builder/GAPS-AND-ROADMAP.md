# TNC — Honest Gap Analysis & Roadmap

Snapshot (July 2026): the playbook is solid; the product is unbuilt. No site
has run the pipeline yet, the gallery is empty, and there is no TNC infra,
pricing, billing, or contract. This file tracks the gaps and the order to
close them. Update it as items land.

## Gaps, ranked by impact

| # | Flaw | Solution | Status |
|---|---|---|---|
| 1 | Pipeline unproven, gallery empty — nothing to show clients | Build TNC's own marketing site (Motion tier) through the full pipeline; it becomes demo #1 and the home of the intake form | ☐ |
| 2 | Every build starts from scratch — "custom" fights "rapid" | `tnc-starter` template repo: React + Tailwind + React Bits pre-wired + Anime.js + SEO baseline + deploy config; separate 3D variant with a reusable R3F scene rig | ☐ |
| 3 | No pricing numbers, no billing | Set tier pricing (straw man: Standard $1.5–2.5k + $99–149/mo; Motion $3–5k + $199–249/mo; 3D $6–12k + $299–399/mo; buyout = build × 1.5–2). Stripe subscriptions for membership | ☐ |
| 4 | Legal exposure: TNC holds client domains, AI-image usage undefined | One reusable service agreement: ownership, exit terms (client can always take domain + site export), update SLA, cancellation; confirm commercial terms on generated assets | ☐ |
| 5 | Maintenance promise scales linearly with one person | Cap monthly update hours per tier; automate SEO reports (Search Console API → generated monthly PDF); single request channel that creates tracked tickets | ☐ |
| 6 | All-AI imagery reads generic for local businesses | Hybrid asset policy at intake: client photos where authenticity matters (food, work, faces), AI for heroes/backgrounds/polish | ☐ |
| 7 | 3D tier is the hardest delivery with the worst perf traps | Don't sell 3D until 2–3 Standard/Motion launches; build one re-skinnable R3F rig instead of novel 3D per client | ☐ |
| 8 | No uptime monitoring behind an uptime promise | Cloudflare health checks or UptimeRobot (free) on every client site | ☐ |
| 9 | Playbook + client work living inside the unrelated Lens-ai repo | TNC GitHub org: `playbook`, `tnc-starter`, one private repo per client | ☐ |

## Roadmap

### Phase A — Prove it (now)
1. Create TNC GitHub org + TNC Cloudflare account (Registrar + Pages)
2. Build `tnc-starter`
3. Build TNC's own site through the full pipeline → first gallery entry
4. Set pricing numbers in CLIENT-OPTIONS.md

### Phase B — Make it a business (before client #1)
5. Service agreement template
6. Stripe subscription billing
7. SEO report automation
8. Online intake form (on the TNC site)

### Phase C — Scale the flagship (after 2–3 launches)
9. 3D scene rig + first 3D Premium sale
10. Grow the gallery; tighten SLAs from real delivery data
