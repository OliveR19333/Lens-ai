# TNC Client Options — Service Tiers

Three tiers. Every tier is a fully custom design — the tier sets how much
motion and dimension the site gets, not how much care.

## Tier 1 — Standard ("Sharp & Fast")

Clean, modern, fast marketing site with tasteful entrance animations.

- Up to 5 sections/pages (hero, about, services, gallery, contact)
- React Bits components customized to the brand (text reveals, cards, grids)
- Anime.js entrance + scroll animations
- AI-generated hero/section imagery via Higgsfield, upscaled to 2K
- Deployed with custom domain, OG/social cards, SEO basics
- **Best for:** local businesses, professionals, restaurants, landing pages

## Tier 2 — Motion ("Alive")

Everything in Standard, plus a kinetic layer that makes the site feel alive.

- Video hero: seamless AI-generated motion loop (`generate_video`)
- Scroll-choreographed storytelling (pinned sections, staggered reveals,
  parallax layers)
- Interactive components: animated backgrounds (Aurora, Particles, Beams from
  React Bits), magnetic buttons, cursor effects
- Micro-interactions across all CTAs and cards
- **Best for:** brands, agencies, products, events, creators

## Tier 3 — 3D Premium ("Immersive")

The flagship. A high-end 3D experience in the browser.

- Custom React Three Fiber scene: product configurator, 3D hero object,
  scroll-driven 3D story, or environment fly-through
- 3D assets generated from brand imagery via `generate_3d` (image → GLB),
  or modeled/sourced as needed
- Camera + material animation driven by Anime.js' three.js adapter and/or GSAP
  ScrollTrigger
- Static-image fallback path so the site stays fast on low-power devices
- Everything from the Motion tier included
- **Best for:** premium brands, real estate, automotive, tech products,
  portfolios that need to win attention

## Add-ons (any tier)

- Short-form launch video for socials (Higgsfield shorts studio)
- Brand voiceover / audio branding (`generate_audio`)
- Extra pages, blog setup, booking/contact integrations, e-commerce
- Monthly care plan: content updates, new imagery drops, seasonal refreshes

## Example gallery

> Add every launched TNC site here with a screenshot, tier, and live URL.
> This section is the sales deck — keep it current.

| Site | Tier | URL | Notes |
|---|---|---|---|
| _(first launch goes here)_ | | | |

### Reference examples to show clients (until our gallery fills in)

- React Bits showcase — https://reactbits.dev/showcase (Standard/Motion feel)
- Anime.js homepage — https://animejs.com (Motion feel)
- three.js showcase — https://threejs.org (3D Premium feel)
- Adrian Hajdin 3D portfolio (open source) —
  https://github.com/adrianhajdin/3d-portfolio (3D Premium structure)
