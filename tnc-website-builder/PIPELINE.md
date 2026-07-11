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

## Phase 7 — Deploy & handoff

Two deployment paths — pick per client:

1. **Higgsfield-hosted (default, fastest):** `create_website` with
   `type: "website"` and a memorable subdomain → build → `deploy_website`.
   Client site is an SSR Cloudflare Worker with zero Higgsfield branding.
   Custom domain pointed via CNAME.
2. **Client-owned infra:** push the repo to the client's GitHub, deploy to
   Vercel/Netlify/Railway. Use when the client requires ownership or has
   backend needs beyond a brochure site.

Handoff kit: live URL, repo access, asset manifest, 1-page "how to request
changes" doc.

**Gate:** client sign-off on the live URL. Archive the intake + concept board
into the project folder for the portfolio/example library.

## After every launch

Add the site to `CLIENT-OPTIONS.md`'s example gallery with a screenshot —
the gallery is the sales tool for the next client.
