import { useReveal } from '@/hooks/useAnimationTimeline';

const tiers = [
  {
    name: 'Standard',
    icon: '⚡',
    description: 'Perfect for startups and small businesses',
    features: [
      'Responsive design',
      'SEO optimization',
      'Cloudflare hosting',
      'SSL & domain management',
      'Monthly updates included',
    ],
    price: 'Starting at $1,500/mo',
  },
  {
    name: 'Motion',
    icon: '🎬',
    description: 'Engaging experiences with premium animations',
    features: [
      'Everything in Standard',
      'Anime.js scroll animations',
      'GSAP ScrollTrigger effects',
      'Parallax & parallax effects',
      'Lenis smooth scrolling',
      'Motion UX optimization',
    ],
    price: 'Starting at $2,500/mo',
    highlight: true,
  },
  {
    name: '3D Premium',
    icon: '🎨',
    description: 'Immersive 3D experiences with Three.js',
    features: [
      'Everything in Motion',
      'Three.js 3D scenes',
      'React Three Fiber integration',
      'Custom 3D models & meshes',
      'Advanced performance tuning',
      'Enterprise support',
    ],
    price: 'Starting at $4,500/mo',
  },
];

export default function Services() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold mb-12 text-center">Service Tiers</h2>
        <p className="text-center text-text/70 mb-16 max-w-2xl mx-auto">
          Choose the tier that fits your vision. All tiers include monthly management and ongoing support.
        </p>
        <div className="grid md:grid-cols-3 gap-8">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`p-8 rounded-lg transition-all ${
                tier.highlight
                  ? 'bg-gradient-to-br from-secondary to-accent text-white shadow-xl scale-105'
                  : 'bg-white shadow-sm hover:shadow-lg text-text'
              }`}
            >
              <div className={`text-5xl mb-4 ${tier.highlight ? '' : ''}`}>{tier.icon}</div>
              <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
              <p className={`mb-6 ${tier.highlight ? 'text-white/90' : 'text-text/70'}`}>{tier.description}</p>
              <ul className={`space-y-3 mb-8 text-sm ${tier.highlight ? 'text-white/80' : 'text-text/80'}`}>
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start">
                    <span className="mr-3">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <div className="mb-6">
                <p className={`font-bold ${tier.highlight ? 'text-white' : 'text-accent'}`}>{tier.price}</p>
              </div>
              <button
                className={`w-full py-3 px-4 rounded-lg font-semibold transition-all ${
                  tier.highlight
                    ? 'bg-white text-secondary hover:bg-primary hover:text-white'
                    : 'bg-secondary text-white hover:bg-primary'
                }`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
