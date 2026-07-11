# TNC Premium 3D Design Standard

The rule that defines TNC's high-end look: **scroll-first, not 3D-first.**
3D is seasoning, not the meal. The scroll tells the story; the 3D moments
punctuate it. If an effect doesn't serve the client's story, it gets cut —
gratuitous animation reads as cheap, restraint reads as premium.

## The taste rules

1. **One hero 3D moment per site** — a product that rotates as you scroll, a
   camera that glides through a space, a material that reacts. Not five.
2. **Scroll choreography carries the premium feel** — pinned sections,
   scrubbed camera moves, progressive reveals, parallax depth. This is what
   clients perceive as "expensive," and it's cheap to render.
3. **Luxury palette discipline** — near-black backgrounds, off-white type,
   one metallic/accent tone. Motion slow and eased; nothing bounces.
4. **Navigation is sacred.** The scroll experience never traps the visitor:
   - Persistent nav (or hamburger) visible at all times, with real links
   - Every section reachable by direct click, never scroll-position-only
   - Scroll progress indicator on long story pages
   - Contact/CTA always one tap away — the site exists to convert
   - Deep links work: every section has a URL anchor

## 3D asset hubs (sourcing order)

| Hub | Use | License |
|---|---|---|
| [Poly Haven](https://polyhaven.com/models) | First stop — production-quality models, HDRIs, textures | CC0, no attribution |
| [pmndrs market](https://market.pmnd.rs) | R3F-ready models/materials, drop straight into scenes | CC0 |
| [Sketchfab](https://sketchfab.com) | Huge library; filter web-optimized (<50k polys), GLB downloads | Per-model, check each |
| [Quaternius](https://quaternius.com) / [Kenney](https://kenney.nl) | Stylized/low-poly packs | CC0 |
| Higgsfield `generate_3d` | Custom brand objects — client's product/logo → GLB | Generated per client |

Inspiration hubs to pull references from at concept phase:
[Awwwards 3D](https://www.awwwards.com/websites/3d/) ·
[three.js showcase](https://threejs.org) ·
[Codrops](https://tympanus.net/codrops/) demos.

## The scroll rig (how it's built)

- GSAP ScrollTrigger master timeline, `scrub: true` — camera position, mesh
  transforms, and material uniforms all keyed to scroll progress
- Lenis for smooth scroll feel
- R3F scene mounted once, animated by the timeline — never re-rendered per
  section
- DOM content (headlines, copy, CTA) stays real HTML on top of the canvas:
  selectable, SEO-indexable, accessible

## Mobile performance budget (hard limits, not goals)

Phones are the primary device. The site ships only when it's smooth on a
mid-range phone, not just a MacBook.

| Budget | Limit |
|---|---|
| Scene polycount | ≤ 150k triangles total on mobile tier (≤ 50k per hero model) |
| Textures | ≤ 1024px on mobile, KTX2/basis compressed |
| Draw calls | ≤ 60 on mobile |
| Post-processing | No bloom on mobile (or half-res only); no SSAO |
| Pixel ratio | Cap `dpr` at 1.5–2 |
| Initial load | 3D lazy-loads after first paint; LCP is never the canvas |
| Frame rate | 55–60 fps scroll on a 3-year-old Android — tested, not assumed |

Implementation rules:

1. **Device-tier detection** on load: low-tier devices get reduced geometry,
   smaller textures, effects off.
2. **Static fallback always ships:** a rendered poster image + CSS scroll
   animations for devices (or `prefers-reduced-motion` users) that can't run
   the scene. The story still works without WebGL.
3. **Zone loading:** models load/dispose as the camera passes through scene
   segments — GPU memory stays flat.
4. **Test gate:** real-phone scroll test + Lighthouse mobile ≥ 85 before any
   3D-tier launch.

## What TNC does NOT build

- Full-screen 3D worlds you "walk around" in — disorienting, slow, hurts
  conversion
- Scroll-jacking that overrides native scroll speed/direction
- 3D that blocks reading content or delays first paint
- Loading screens longer than ~1.5s for the 3D layer
