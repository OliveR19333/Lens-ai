# TNC Website — Concept Board
**Phase 2: Design Direction**

---

## Visual Strategy

### Palette & Tone
- **Primary** (#1f2937): Grounded, professional — anchors the brand
- **Secondary** (#6366f1): Sophisticated accent — builds hierarchy
- **Accent** (#ec4899): High-energy CTAs — commands attention
- **Tertiary** (#14b8a6): Subtle highlights — adds warmth
- **Vibe:** Minimal + intentional; luxury simplicity meets innovation

### Typography Pairing
- **Display:** Poppins 800/700 (bold, distinctive, playful confidence)
- **Body:** Inter 400/500/600 (neutral, legible, modern trustworthiness)
- **Hierarchy:** Clear visual distinction between layers; generous whitespace

### Motion Language
**Tier:** Motion (kinetic, intentional, not overwhelming)
- **Entrance:** Fade + subtle slide-up on scroll (offset stagger across sections)
- **Hover:** Scale + color shift (buttons, cards, links)
- **Scroll choreography:** Parallax + reveal; one "wow moment" per viewport
- **Easing:** Smooth, not bouncy — ease-out-quad for entrances, custom for hero
- **Intensity:** `motionIntensity: 'standard'` (not minimal, not intense)

### The "Wow Moment"
**Hero scroll reveal:** As the user scrolls down the hero section, the background motion loop subtly responds (scale + opacity shift), and the headline locks to viewport (parallax effect). The CTA button has a "ready-to-click" animation (pulse glow on load).

---

## Layout Direction

### Hero Section
- Full-bleed, gradient + motion video background (looping)
- Centered headline + subheading with staggered entrance
- CTA button with hover glow + click state
- Subtle animated shape (circle or polygon) in background, depth-layered

### About / Story
- Two-column layout (image left, text right)
- Team photo with gentle entrance on scroll
- Highlighted callout: "What drives us" (color-blocked accent box)

### Services Grid
- 3-column card layout (1 column mobile, 2 tablet, 3 desktop)
- Each card shows tier name (Standard, Motion, 3D), features list, and starting price
- Hover state: card lifts + accent bar appears
- Ghost CTA button for each tier

### Case Studies / Gallery
- Hero case study card (full-width, image + overlay text, plays video on hover)
- Grid of 6 smaller case thumbnails with hover zoom + accent overlay
- Lazy-loaded images with blur-up effect

### Testimonials
- 5-card carousel (auto-scroll, pausable on hover)
- Quote + author photo + company
- Accent quote marks in background
- Navigation dots + prev/next buttons

### How We Work (Process)
- 8-step visual pipeline (horizontal scroll or stacked vertically)
- Each step: number, title, icon, brief description
- Animated connection lines between steps (draw on scroll)

### Pricing Transparency
- 3-tier pricing table (responsive: stacked on mobile, side-by-side on desktop)
- Tier highlight (Motion tier pre-selected)
- Feature comparison, feature highlights for each tier
- "Schedule a call" CTA per tier

### Contact / Footer
- Prominent form (name, email, project type, message)
- Direct email + booking link in footer
- Social media icons with hover states
- Legal links (privacy, terms)

---

## Component References (React Bits / UI Inspiration)

1. **Vercel's Hero + Button State:** Full-bleed gradient, centered content, sophisticated button with micro-interaction
   - Ref: https://vercel.com
   
2. **Linear's Pricing Table:** Clean, scannable, tier comparison with smooth transitions
   - Ref: https://linear.app/pricing
   
3. **Framer's Case Study Cards:** Media-rich, hover reveals additional info, cohesive design system
   - Ref: https://framer.com/showcase

---

## Visual Moments (AI-Generated Concept Images)

**Generate via Higgsfield `generate_image`:**

1. **Hero Mood Board:**
   - Prompt: "Modern tech brand hero section: dark slate background with abstract geometric shapes, indigo and pink accents, motion blur trails, minimalist elegant"
   - Purpose: Show overall tone, color interplay, abstract motion language

2. **Services Section:**
   - Prompt: "3-column service card grid, teal/indigo/pink tier badges, professional icons, subtle shadow depth, modern SaaS aesthetic"
   - Purpose: Validate service card design direction

3. **Case Study Hero:**
   - Prompt: "Professional portfolio showcase: large image hero with semi-transparent overlay, headline + CTA, dark slate background, tech-forward minimal"
   - Purpose: Show case study card composition and text-over-image legibility

---

## Responsive Behavior

- **Mobile (< 768px):** Single column, full-bleed sections, touch-friendly CTAs (48px min)
- **Tablet (768px–1024px):** 2-column grids, flexible spacing
- **Desktop (> 1024px):** Full 3-column, max-width 1280px, generous gutters

---

## Performance & Accessibility Targets

- **Lighthouse Mobile:** ≥90 (Performance, Accessibility, SEO)
- **First paint:** < 2s on 4G
- **Motion:** Respects `prefers-reduced-motion`
- **Color contrast:** WCAG AA minimum (4.5:1 body, 3:1 graphics)
- **Semantic HTML:** Proper heading hierarchy, ARIA labels, keyboard nav

---

## Next Steps

1. **Client approval:** Confirm motion language + layout direction
2. **Asset generation:** Hero backgrounds, case study images, tier badges
3. **Component build:** Scaffold React site, wire up sections from tnc-starter template

---

*Concept approved by TNC Strategy:* _____ (Date)
