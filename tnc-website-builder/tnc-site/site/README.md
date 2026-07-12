# tnc-starter

A production-ready, animation-rich website template for the TNC Website Builder pipeline. Built with React 19, Vite, Tailwind CSS v4, and Anime.js v4 for performant, motion-first web experiences.

**Key Features:**
- 🎨 **Brand Config Central**: Single `brand.config.ts` file controls all theming (colors, fonts, radius, motion intensity)
- 🎬 **Animation Stack**: Anime.js v4 (DOM/SVG/3D adapter) + optional GSAP/Lenis for multi-tier motion
- 📱 **Mobile-First Responsive**: Tailwind CSS v4 with full accessibility and reduced-motion support
- 🚀 **Zero-Config Deployment**: Vite build → Cloudflare Pages/Workers (global CDN)
- 📦 **6 Pre-Built Sections**: Hero, About, Services, Gallery, Testimonials, Contact—all animation-ready
- 🔧 **TypeScript + Strict**: Full type safety with path aliases (`@/` for src/)
- ♿ **WCAG 2.1 AA**: Semantic HTML, ARIA, color contrast, keyboard navigation

---

## Quick Start

### Prerequisites
- Node.js 18+ (tested on 20+)
- npm or yarn

### Installation
```bash
git clone https://github.com/OliveR19333/tnc-starter.git
cd tnc-starter
npm install
```

### Development
```bash
npm run dev
# Open http://localhost:5173
```

### Build
```bash
npm run build
# Output: dist/
```

### Preview
```bash
npm run preview
```

---

## Architecture

### Brand Configuration (`src/brand.config.ts`)

The entire site theme is controlled by a single TypeScript interface:

```typescript
export interface BrandConfig {
  name: string;
  description: string;
  colors: {
    primary: string;      // Main brand color
    secondary: string;    // Accent for highlights
    accent: string;       // CTA buttons
    text: string;         // Body text
    bg: string;          // Page background
  };
  fonts: {
    family: string;           // Body font (e.g., 'Inter')
    headingFamily: string;    // Heading font (e.g., 'Poppins')
  };
  radius: string;        // Border radius (e.g., '0.5rem')
  motionIntensity: 'minimal' | 'standard' | 'intense';
}
```

#### Applying Config

```typescript
import { applyBrandConfig, defaultBrandConfig } from '@/brand.config';

// Apply at runtime (e.g., in App.tsx useEffect)
applyBrandConfig(defaultBrandConfig);
```

This injects CSS variables into `:root`:
```css
--color-primary: #1f2937;
--color-secondary: #6366f1;
--color-accent: #ec4899;
--color-text: #111827;
--color-bg: #ffffff;
--font-family: 'Inter', sans-serif;
--heading-family: 'Poppins', sans-serif;
--radius: 0.5rem;
--motion-intensity: 1;
```

Every component uses these variables via Tailwind or direct CSS, enabling instant site-wide rebranding.

### Tailwind Color Mapping

`tailwind.config.ts` defines:
```typescript
colors: {
  primary: 'var(--color-primary)',
  secondary: 'var(--color-secondary)',
  accent: 'var(--color-accent)',
  text: 'var(--color-text)',
  bg: 'var(--color-bg)',
}
```

Use in JSX:
```jsx
<button className="bg-primary hover:bg-primary/90 text-white">Click me</button>
```

---

## Animation System

### Anime.js v4 Integration

Three-tier motion support:

#### Tier 1: Standard (Default)
All sections ship with scroll-triggered entrance animations via `useReveal()`:

```typescript
import { useReveal } from '@/hooks/useAnimationTimeline';

export default function MySection() {
  const ref = useReveal({ duration: 800 }); // Fade + slide-up on scroll
  return <section ref={ref}>Content</section>;
}
```

The hook uses Intersection Observer to detect when an element enters the viewport, then fires Anime.js:
```typescript
anime({
  targets: element,
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 800,
  easing: 'easeOutQuad',
});
```

#### Tier 2: Motion (Optional Import)
For advanced timelines, import the full animation orchestrator:

```typescript
import anime from 'animejs';
import { gsap, ScrollTrigger } from 'gsap/all';

gsap.registerPlugin(ScrollTrigger);

// Build complex, scroll-linked animations
gsap.to('.hero-title', {
  scrollTrigger: {
    trigger: '.hero',
    start: 'top center',
    markers: true,
  },
  y: -100,
  opacity: 0,
  duration: 2,
});
```

#### Tier 3: 3D Premium (Optional)
For 3D scenes, use Three.js via r3f:

```typescript
import { Canvas } from '@react-three/fiber';
import { useAnimations } from '@react-three/drei';

export default function Scene3D() {
  return (
    <Canvas>
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>
    </Canvas>
  );
}
```

### Reduced Motion Support

The browser's `prefers-reduced-motion` preference is respected globally via `src/App.css`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Users with motion accessibility needs automatically get instant transitions.

---

## Section Components

All sections accept a `ref` prop for animation hooks and use Tailwind for styling:

### Hero (`src/sections/Hero.tsx`)
Full-screen entrance section with gradient background, headline, and CTA button.

**Props:**
- `ref`: Animation trigger ref (via `useReveal()`)

**Example:**
```jsx
<Hero />
```

### About (`src/sections/About.tsx`)
Company story with side-by-side layout (image + text).

### Services (`src/sections/Services.tsx`)
3-column grid of service cards with icons.

### Gallery (`src/sections/Gallery.tsx`)
Masonry or grid layout of portfolio/product images.

### Testimonials (`src/sections/Testimonials.tsx`)
Carousel or grid of client/user quotes.

### Contact (`src/sections/Contact.tsx`)
Contact form with name, email, message fields. Submits via `console.log()` (ready for Formspree, SendGrid, etc.).

---

## Customization Guide

### Rebrand in 5 Minutes

1. **Update brand.config.ts:**
   ```typescript
   export const defaultBrandConfig: BrandConfig = {
     name: 'My Brand',
     description: 'My brand tagline',
     colors: {
       primary: '#0066cc',      // Your brand blue
       secondary: '#ffcc00',    // Your accent
       accent: '#ff0066',       // Your CTA color
       text: '#1a1a1a',
       bg: '#ffffff',
     },
     fonts: {
       family: "'Roboto', sans-serif",
       headingFamily: "'Montserrat', sans-serif",
     },
     radius: '0.75rem',
     motionIntensity: 'standard',
   };
   ```

2. **Save and refresh browser** — entire site rebrands in <100ms.

### Add a Custom Section

1. Create `src/sections/MySection.tsx`:
   ```typescript
   import { useReveal } from '@/hooks/useAnimationTimeline';

   export default function MySection() {
     const ref = useReveal();
     return (
       <section className="py-20 px-4" ref={ref}>
         <h2 className="text-4xl font-bold text-primary">My Section</h2>
         <p className="text-text mt-4">Content here...</p>
       </section>
     );
   }
   ```

2. Import in `src/App.tsx`:
   ```typescript
   import MySection from '@/sections/MySection';

   export default function App() {
     return (
       <div>
         <Navbar />
         <main>
           <Hero />
           <MySection />
           <Contact />
         </main>
         <Footer />
       </div>
     );
   }
   ```

### Customize Navbar

Edit `src/components/Navbar.tsx`:
- Change logo text (`<div className="text-2xl font-bold text-primary">Brand</div>`)
- Add/remove menu links in the `links` array
- Adjust colors via Tailwind classes (e.g., `bg-primary`, `text-accent`)

---

## Styling Guidelines

### CSS Variables
All dynamic styling uses CSS variables (no Tailwind arbitrary values). This ensures consistency and enables runtime rebranding.

### Color Scale
Use Tailwind opacity modifiers for tone depth:
```jsx
<div className="bg-primary">Full primary</div>
<div className="bg-primary/80">80% opacity</div>
<div className="bg-primary/60">60% opacity</div>
<div className="bg-primary/40">40% opacity</div>
```

### Spacing
Tailwind's default scale (`p-4`, `mb-8`, `gap-6`). Adjust `tailwind.config.ts` if custom spacing is needed.

### Typography
All text uses `font-family: var(--font-family)`. Headings auto-load via `--heading-family`.

---

## Accessibility (a11y)

✅ **Semantic HTML**: `<section>`, `<nav>`, `<footer>`, `<header>` used throughout  
✅ **ARIA Labels**: Form inputs, buttons, and interactive elements have descriptive labels  
✅ **Keyboard Navigation**: All links, buttons, and forms fully keyboard-accessible  
✅ **Color Contrast**: WCAG AA minimum (4.5:1 for text, 3:1 for graphics)  
✅ **Reduced Motion**: Respects `prefers-reduced-motion` media query  
✅ **Semantic Heading Hierarchy**: `<h1>` → `<h2>` → `<h3>` (no skips)  

### SEO Component

Use `src/components/SEO.tsx` to inject meta tags:

```typescript
import SEO from '@/components/SEO';

export default function App() {
  return (
    <>
      <SEO
        title="My Brand | Web Design & Development"
        description="Beautiful, fast websites built for modern brands."
        canonical="https://mybrand.com"
        ogImage="https://mybrand.com/og-image.png"
      />
      <Navbar />
      {/* ... */}
    </>
  );
}
```

---

## Performance Budgets

**Lighthouse Targets:**
- Performance: ≥90
- Accessibility: ≥95
- Best Practices: ≥90
- SEO: ≥95

**Build Output:**
- JS: <100 kB (gzipped)
- CSS: <30 kB (gzipped)
- Initial paint: <2s on 4G

**Optimizations:**
- Vite code splitting (route-based chunking)
- Lazy loading for images (use `<img loading="lazy" />`)
- Anime.js tree-shakeable imports (import only what you use)
- Tailwind CSS purging (unused styles stripped)

---

## Deployment

### Cloudflare Pages

1. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_ORG/your-site.git
   git push -u origin main
   ```

2. **Create Pages Project:**
   - Dashboard → Pages → Create project → Connect Git repo
   - Build command: `npm run build`
   - Build output directory: `dist`

3. **Deploy:**
   - Push to main branch (automatic deploy)
   - Or manually trigger in Cloudflare dashboard

### Environment Variables

For APIs, form handling, etc., set in Cloudflare Pages:
- Dashboard → Settings → Environment variables
- Access via `import.meta.env.VITE_API_KEY`

### Custom Domain

1. Update DNS to Cloudflare nameservers
2. In Cloudflare dashboard → Domain settings → Custom domains
3. Add your domain, SSL/TLS auto-provisions

---

## Project Structure

```
tnc-starter/
├── src/
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── bits/Footer.tsx
│   │   └── SEO.tsx
│   ├── sections/
│   │   ├── Hero.tsx
│   │   ├── About.tsx
│   │   ├── Services.tsx
│   │   ├── Gallery.tsx
│   │   ├── Testimonials.tsx
│   │   └── Contact.tsx
│   ├── hooks/
│   │   └── useAnimationTimeline.ts
│   ├── App.tsx
│   ├── App.css
│   ├── brand.config.ts
│   └── main.tsx
├── public/
│   └── vite.svg
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── package.json
└── README.md
```

---

## Contributing

### Local Development Workflow

1. Fork/clone the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes, test locally: `npm run dev`
4. Build and preview: `npm run build && npm run preview`
5. Commit with clear messages: `git commit -m "feat: add X"`
6. Push: `git push origin feature/my-feature`
7. Open PR to main

### Code Style

- TypeScript strict mode enabled
- Prettier for formatting (optional: `npm run format`)
- ESLint via Oxlint (auto in build)

---

## Troubleshooting

### Vite dev server slow?
```bash
# Clear cache
rm -rf node_modules .vite
npm install
npm run dev
```

### Tailwind styles not applying?
- Ensure `tailwind.config.ts` includes the correct content paths
- Check for CSS variable typos (e.g., `var(--color-primray)`)
- Rebuild CSS: `npm run build`

### Anime.js not triggering?
- Verify element is in viewport (use browser dev tools)
- Check `useReveal()` ref is attached: `<section ref={ref}>`
- Confirm `threshold: 0.1` in Intersection Observer (adjust if needed)

### Build fails with TypeScript errors?
- Run `tsc --noEmit` to check for issues
- Ensure all imports use correct paths (e.g., `@/hooks/...`)
- Check `.env.example` for missing env vars

---

## Roadmap

- [ ] Built-in form handling (Formspree, SendGrid integration)
- [ ] Dark mode toggle
- [ ] Internationalization (i18n)
- [ ] Blog template with Markdown MDX support
- [ ] E-commerce product grid
- [ ] Video section with Mux integration
- [ ] Storybook integration for component isolation

---

## License

MIT — Free for personal and commercial use.

---

## Support

Questions? Issues? Reach out:
- GitHub Issues: [Issues](https://github.com/OliveR19333/tnc-starter/issues)
- Email: hello@tncgas.com

---

**Built for the TNC Website Builder Pipeline.**  
Made with ❤️ by TNC Creative.
