# TNC Website Builder — Service Pipeline

The playbook for TNC's custom website building service. Every client site is
built fresh from this pipeline — no recycled themes — using a fixed tool stack
so quality is repeatable and delivery is fast.

## What's in this folder

| File | Purpose |
|---|---|
| [PIPELINE.md](PIPELINE.md) | The end-to-end build pipeline, intake → live site |
| [CLIENT-OPTIONS.md](CLIENT-OPTIONS.md) | The three service tiers clients pick from, with example sites |
| [STACK.md](STACK.md) | The vetted tool stack: component libraries, animation, 3D, builders |
| [INTAKE.md](INTAKE.md) | Client intake questionnaire — fill this out before any build starts |

## The short version

1. **Client picks a tier** — Standard, Motion, or 3D Premium (see CLIENT-OPTIONS.md).
2. **Intake** — brand, goals, references, content (see INTAKE.md).
3. **Build** — React site assembled from React Bits components, animated with
   Anime.js / GSAP, 3D scenes via React Three Fiber when the tier calls for it.
4. **Assets** — hero images, brand imagery, short motion loops, and 3D meshes
   generated through the Higgsfield MCP (`generate_image`, `generate_video`,
   `generate_3d`).
5. **Deploy** — through Higgsfield's website pipeline (`create_website` with
   `type: "website"` → SSR Cloudflare Worker at its own subdomain), or to the
   client's own hosting (Vercel/Netlify/Railway) when they need to own the infra.

## Why this stack

- **React Bits** (reactbits.dev) — 110+ copy-paste animated components, no
  heavyweight dependency chain. Components are owned in-repo, so every client
  site can be customized without fighting a library.
- **Anime.js v4** (animejs.com) — lightweight modular animation engine; v4.5+
  ships a built-in three.js adapter, so the same engine animates DOM *and* 3D
  scenes. One animation API across all tiers.
- **React Three Fiber + drei** — the industry-standard React wrapper for
  three.js. Powers the 3D Premium tier.
- **Higgsfield MCP** — asset generation (image/video/3D) and one-command
  deploys with independent client branding (no Higgsfield branding on
  `type: "website"` builds).
