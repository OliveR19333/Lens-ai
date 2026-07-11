# TNC Build Pipeline — Intake to Live Site

Every client site runs through these seven phases. Nothing ships until the
gate at the end of each phase is met.

## Phase 1 — Intake

Fill out [INTAKE.md](INTAKE.md) with the client. Capture:
brand assets (logo, colors, fonts), business goal of the site, 3–5 reference
sites they love, tier selection, content inventory (copy, photos, video),
domain situation, and deadline.

**Gate:** signed-off intake doc + tier locked.

## Phase 2 — Concept & reference board

- Build a one-page concept: layout direction, palette, type pairing, motion
  language (subtle / kinetic / immersive), and the "wow moment" for the site.
- Pull 2–3 concrete component references from React Bits' showcase and (for 3D
  tier) three.js/R3F examples so the client approves against real visuals,
  not abstractions.
- Generate 2–3 mood/hero concept images with Higgsfield `generate_image` so
  the client sees the visual direction before code exists.

**Gate:** client approves one concept.

## Phase 3 — Asset system

Generate the full asset kit through Higgsfield MCP:

| Asset | Tool | Notes |
|---|---|---|
| Hero & section imagery | `generate_image` | Brand-consistent prompt set, then `upscale_image` to 2K/4K |
| Background motion loops | `generate_video` | 3–6s seamless loops for hero backgrounds (Motion + 3D tiers) |
| Cutouts / product shots | `remove_background` | Transparent PNGs for layered layouts |
| 3D meshes | `generate_3d` | Image → GLB mesh, dropped into R3F scenes (3D tier) |
| Wide/tall crops | `outpaint_image` / `reframe` | Responsive art direction |

Store everything in `assets/` with a `manifest.json` mapping asset → section.

**Gate:** all sections have final assets; nothing is placeholder.

## Phase 4 — Build to the board

- Scaffold: Vite + React 19 + Tailwind (or the Higgsfield SSR scaffold if
  deploying through `create_website`).
- Assemble sections from **React Bits** components (copied into
  `src/components/`, then customized to the brand — we own the code).
- Wire animations with **Anime.js v4**: entrance timelines, scroll-triggered
  reveals, hover states. Use `createLayout()` for layout transitions.
- **3D tier only:** build the scene in React Three Fiber + drei, drive camera
  and material animation through Anime.js' three.js adapter, lazy-load the
  scene, and always ship a static-image fallback for low-power devices.

**Gate:** every page matches the approved concept board; Lighthouse
performance ≥ 90 mobile (≥ 80 for 3D tier with the fallback path verified).

## Phase 5 — Motion pass

Dedicated pass tuning easing, stagger, and scroll choreography so motion feels
intentional, not templated. Rule: max one attention-grabbing motion per
viewport; everything else supports it.

**Gate:** motion review on a real phone, not just desktop.

## Phase 6 — Metadata & launch kit

- OG title/description, favicon, social cover image (generate the cover with
  `generate_image`; optional cover video is client-billed, ask first).
- SEO basics: semantic headings, alt text, sitemap, meta tags.
- Analytics snippet if the client wants it.

**Gate:** share the URL in a chat app — the preview card must look right.

## Phase 7 — Launch (TNC-managed, no handoff)

TNC builds AND maintains — the client never touches infrastructure. All
client repos live in TNC's GitHub, hosting runs under TNC's accounts, and
domains sit in TNC's registrar.

1. **Domain:** register (or transfer) the client's domain into TNC's
   Cloudflare account. Cloudflare Registrar sells at wholesale cost with
   free enterprise DNS — one dashboard for every client domain, SSL, and CDN.
2. **Production hosting:** deploy to Cloudflare Pages/Workers under the TNC
   account and connect the domain (one click, automatic SSL). Higgsfield
   `deploy_website` is the rapid-preview path during the build; production
   lives on TNC-controlled infra.
3. **SEO baseline:** submit the sitemap to Google Search Console (TNC-owned
   property), verify indexing, confirm meta/schema, wire analytics.

**Gate:** client sign-off on the live URL at their domain. Archive the intake
+ concept board into the project folder for the portfolio/example library.

## Phase 8 — Ongoing management (the recurring service)

The monthly service layer every client is on:

- **Updates:** content/design changes on request; changes ship through the
  same repo + deploy pipeline, so every edit is versioned and reversible.
- **SEO management:** Search Console monitoring, ranking reports, sitemap and
  schema upkeep, meta refreshes as content changes.
- **Fresh assets:** periodic AI imagery/motion drops via Higgsfield to keep
  the site current (seasonal, promotional).
- **Operations:** uptime, SSL and domain renewals, analytics reporting.

## After every launch

Add the site to `CLIENT-OPTIONS.md`'s example gallery with a screenshot —
the gallery is the sales tool for the next client.
