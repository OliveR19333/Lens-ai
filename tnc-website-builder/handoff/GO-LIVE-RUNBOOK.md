# GO-LIVE RUNBOOK — execute top to bottom

Each step has a done-check. Don't skip gates. Ryan-action steps are marked
**[RYAN]** — request them early, keep building while waiting.

## Step 0 — Housekeeping (5 min)

- [ ] Merge PR #3 (this playbook) AND PR #2 (TNC master plan stack) into
      main if still open — both are independent and mergeable; main should
      show the whole estate
- [ ] **[RYAN]** Create TNC Cloudflare account; **[RYAN]** pick + register
      the TNC domain (Cloudflare Registrar); **[RYAN]** confirm GitHub org
- [ ] Confirm pricing numbers with Ryan → write them into
      ../CLIENT-OPTIONS.md (replace the straw-man ranges)

## Step 1 — Build `tnc-starter` (the speed multiplier)

Scaffold once, reuse forever. Create repo `tnc-starter`:

- [ ] Vite + React 19 + Tailwind + TypeScript
- [ ] `src/components/bits/` — curated React Bits set, pre-themed via CSS
      variables: text reveal, gradient text, animated background (Aurora or
      Particles), card grid, magnetic button, navbar, footer
- [ ] Anime.js v4 wired with an entrance-timeline helper +
      scroll-reveal hook (`useReveal`)
- [ ] GSAP + ScrollTrigger + Lenis configured (Motion layer, tree-shaken
      out when unused)
- [ ] SEO baseline: meta/OG component, sitemap generation, semantic layout,
      robots.txt
- [ ] `brand.config.ts` — single file that sets palette, fonts, radius,
      motion intensity (this is what makes each client site custom-fast)
- [ ] Section library: Hero, About, Services, Gallery, Testimonials,
      Contact (each accepts brand config + content props)
- [ ] Deploy config for Cloudflare Pages + a `deploy preview` path via
      Higgsfield `create_website`/`deploy_website`
- [ ] README: "how to start a client site from this template in 10 steps"

**Gate:** `npm run build` clean; template deploys to a preview URL.

## Step 2 — TNC's own site (Motion tier, demo #1)

Run the FULL pipeline in ../PIPELINE.md on TNC itself — this validates
every phase and produces the sales site.

- [ ] Phase 1 Intake: fill ../INTAKE.md for TNC (Ryan answers; goal =
      generate client leads; CTA = intake/booking form)
- [ ] Phase 2 Concept: brand direction + 2–3 Higgsfield concept images;
      Ryan approves one
- [ ] Phase 3 Assets: hero imagery + one background motion loop via
      Higgsfield; upscale; store in `assets/` with manifest
- [ ] Phase 4 Build: start from `tnc-starter`; sections: Hero (motion
      loop), What We Build (3 tiers with pricing), Gallery (seed with the
      tier reference examples until real launches), How It Works (the
      pipeline, client-facing words), Membership (the value pitch),
      Intake/Contact form
- [ ] Phase 5 Motion pass: real-phone scroll test
- [ ] Phase 6 Metadata: OG cover, favicon, sitemap, Search Console
      property, analytics
- [ ] Phase 7 Launch: deploy to Cloudflare Pages on the TNC domain
- [ ] Add TNC site as gallery entry #1 in ../CLIENT-OPTIONS.md

**Gate:** live at the TNC domain, Lighthouse mobile ≥90, form submits.

## Step 3 — Business layer (Phase B, same session if tokens allow)

- [ ] Intake form on the live site writes somewhere durable (email or DB)
- [ ] Draft the one-page service agreement (ownership, exit terms, update
      SLA, cancellation) → Ryan reviews
- [ ] **[RYAN]** Stripe account → create membership products per tier
- [ ] SEO report automation plan: Search Console API → monthly summary

## Step 4 — Wrap

- [ ] Update ../GAPS-AND-ROADMAP.md checkboxes
- [ ] Commit everything; PRs merged; note what's left for Phase C (3D rig)

## Deferred to Phase C (do NOT build this session)

- The reusable R3F 3D scene rig (build after 2–3 real launches)
- 3D Premium sales
