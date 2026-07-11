# PROJECT STATE — everything decided, in one place

Snapshot at handoff (July 11, 2026). If this conflicts with a playbook doc,
the playbook doc wins — this is the summary.

## Business model

- **Product:** custom websites as a managed service ("TNC Service
  Membership"). TNC owns all infrastructure: client repos in TNC GitHub,
  hosting on TNC Cloudflare, domains in TNC Cloudflare Registrar. Clients
  never touch infra; they request changes and pay monthly.
- **Membership includes:** domain/DNS/SSL/hosting/uptime, SEO management
  (Search Console, sitemaps, meta/schema, ranking reports), content and
  design updates on request, analytics reporting, member discounts on all
  other TNC services. Membership gets a LOWER upfront build price.
- **One-time buildout:** exists, discouraged. Premium price (build + ~1 yr
  membership value), delivered into client-owned accounts, no ongoing
  service, full rates for future changes. Buyout clients = future
  conversion leads (paid onboarding to migrate back).
- **Pricing:** NOT SET. Straw man awaiting Ryan's approval — Standard
  $1.5–2.5k + $99–149/mo · Motion $3–5k + $199–249/mo · 3D Premium
  $6–12k + $299–399/mo · buyout = build × 1.5–2.

## Tiers

1. **Standard "Sharp & Fast"** — ≤5 sections, React Bits components,
   Anime.js entrance/scroll animation, AI hero imagery. Local businesses.
2. **Motion "Alive"** — + video hero loop, GSAP ScrollTrigger
   choreography, animated backgrounds, micro-interactions. Brands/agencies.
3. **3D Premium "Immersive"** — + one hero 3D moment per
   3D-DESIGN-STANDARD.md (scroll-first, easy nav, hard mobile perf
   budgets, static fallback). Premium brands. NOT sold until 2–3 lower-tier
   launches prove the pipeline.

## Locked technical stack

- **Framework:** React 19 + Vite + Tailwind (Higgsfield SSR scaffold when
  deploying previews through `create_website`)
- **Components:** React Bits (copy into repo, customize per brand)
- **Animation:** Anime.js v4 (has three.js adapter as of v4.5); GSAP +
  ScrollTrigger + Lenis for scroll choreography
- **3D:** three.js via React Three Fiber + drei
- **3D assets:** Poly Haven (CC0) → pmndrs market (CC0) → Sketchfab
  (web-optimized, check license) → Higgsfield `generate_3d` for the
  client's own product/logo
- **2D/video assets:** Higgsfield `generate_image` → `upscale_image`,
  `generate_video` loops, `remove_background`, `outpaint_image`
- **Domains:** Cloudflare Registrar, TNC account. API: Cloudflare
  Registrar API (beta, limited TLDs) primary; Porkbun API v3 fallback
  (register there → point nameservers to Cloudflare). Never GoDaddy.
- **Hosting (HYBRID — reconciled with TNC Master Build Plan v2):**
  Cloudflare Pages/Workers (TNC account) serves all STATIC sites — client
  sites and the TNC site (free bandwidth, zero ops, patching lapses can't
  hurt what clients see). A Coolify VPS (Hetzner/DO, ~$15–25/mo) runs the
  SERVER suite from the master plan: Plausible, Listmonk, Ghost, n8n,
  portals — none of which can run on Pages. Higgsfield `deploy_website`
  for instant build previews. (Higgsfield `type: "website"` forbids
  visitor-facing AI features; irrelevant on our own hosting.)
- **Sibling plan:** the [TNC Master Build Plan v2](https://docs.google.com/document/d/1Dnu3Ec8PAiJug7_O51iEE9Xcftr1bcaTLRaP9mZoOBY/edit)
  (Drive) + PR #2 in this repo govern the full TNC estate — vendor
  network, Builder Brief newsletter, care plans, revenue architecture.
  This playbook is the website-builder wing of that vision; care-plan
  pricing ($99–299/mo) aligns with our membership straw man.
- **Monitoring:** Cloudflare health checks / UptimeRobot per client site.

## Repos & branches

- Playbook lives at `tnc-website-builder/` in OliveR19333/Lens-ai (an
  otherwise-unrelated camera app repo — moving to a TNC org is roadmap
  item #9), branch `claude/tnc-website-builder-pipeline-55an2e`, PR #3
  (draft). Netlify auto-deploys previews of this repo; all green.
- Target structure: TNC GitHub org → `playbook`, `tnc-starter`,
  `tnc-website` (TNC's own site), one private repo per client.

## Key constraints & taste rules

- Scroll-first, not 3D-first. One hero 3D moment max. Never scroll-jack.
- Navigation always visible and clickable; contact one tap away.
- Mobile budgets are hard gates: ≤50k polys/hero model, no bloom on
  mobile, dpr ≤2, 3D lazy-loads after first paint, static fallback ships
  always, 55–60fps on a 3-year-old Android, Lighthouse mobile ≥85.
- Hybrid asset policy: client's real photos where authenticity matters
  (food, faces, work); AI for heroes/backgrounds/polish.
- Every launch adds a gallery entry in CLIENT-OPTIONS.md — the gallery is
  the sales deck.

## Open questions for Ryan

1. Approve/adjust pricing numbers
2. TNC domain name to register (for TNC's own site)
3. Confirm TNC GitHub org name
4. Which business is client #1 (any real prospect to build for after the
   TNC site ships?)
