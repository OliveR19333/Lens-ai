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

## Two ways to buy — membership is the default

### TNC Service Membership (the way we sell it)

Every tier is offered first as a managed membership. The site is only half
the product — the membership is the other half:

- Domain registration/renewal and DNS (TNC-managed Cloudflare)
- Hosting, SSL, and uptime
- SEO management: Search Console, sitemaps, meta/schema, ranking reports
- Content and design updates on request — text us a change, it ships
- Analytics reporting
- **Member discount on all other TNC services** (launch videos, imagery
  drops, campaigns, additional pages/sites)
- Lower upfront build price than the one-time option

### One-time standalone buildout (available, not encouraged)

For the customer who insists on a one-time setup. Sold at a **premium
upfront price** (rule of thumb: build price + roughly a year of membership
value), because TNC's ongoing revenue isn't in the deal:

- Full custom build per the same pipeline and tier
- Delivered to hosting/domain in the client's own accounts, with a handoff
  doc — after delivery, updates/SEO/support are not included
- No member discounts; future change requests billed at full project rates
- Standard rebuttal when quoted: "Most clients choose membership — the site
  launches cheaper, stays updated, ranks better, and you never think about
  hosting or domains. The one-time price is higher because you're buying
  out the service."

A buyout client can convert to membership later — migration of their site
into TNC management is a paid onboarding.

## Add-ons (any tier)

- Short-form launch video for socials (Higgsfield shorts studio)
- Brand voiceover / audio branding (`generate_audio`)
- Extra pages, blog setup, booking/contact integrations, e-commerce
- Premium refresh plan: scheduled new imagery drops, seasonal campaigns

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
