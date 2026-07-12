import { useReveal } from '@/hooks/useAnimationTimeline';

const caseStudies = [
  {
    id: 1,
    title: 'Fast Growth',
    tier: 'Standard',
    description: 'Clean, responsive site built in 2 weeks. +40% lead generation.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    id: 2,
    title: 'Motion Magic',
    tier: 'Motion',
    description: 'Scroll animations + video hero. Site traffic doubled.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 3,
    title: 'Premium Experience',
    tier: '3D Premier',
    description: '3D product showcase + smooth scrolljacking. Enterprise conversion.',
    color: 'from-indigo-500 to-pink-500',
  },
  {
    id: 4,
    title: 'Agency Bold',
    tier: 'Motion',
    description: 'Full portfolio showcase with parallax. Attracted top-tier clients.',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    id: 5,
    title: 'Startup Speed',
    tier: 'Standard',
    description: 'Launch-ready in 10 days. Investors impressed by the polish.',
    color: 'from-orange-500 to-red-500',
  },
  {
    id: 6,
    title: 'Luxury Tier',
    tier: '3D Premier',
    description: 'Immersive brand experience. Premium conversions up 3x.',
    color: 'from-yellow-500 to-orange-500',
  },
];

export default function Gallery() {
  const ref = useReveal();

  return (
    <section id="portfolio" className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Work We're Proud Of</h2>
          <p className="text-xl text-text/70">
            Every site is a collaboration. Here's what happens when brands trust TNC.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {caseStudies.map((study) => (
            <div
              key={study.id}
              className="group overflow-hidden rounded-lg shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-2"
            >
              <div className={`bg-gradient-to-br ${study.color} h-48 flex items-end justify-start p-6 relative overflow-hidden`}>
                {/* Animated background pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl transform translate-x-20 -translate-y-20 group-hover:translate-x-10 group-hover:-translate-y-10 transition-transform duration-300" />
                </div>
                <div className="relative z-10">
                  <span className="inline-block px-3 py-1 bg-white/20 text-white text-xs font-semibold rounded-full mb-3">
                    {study.tier}
                  </span>
                </div>
              </div>
              <div className="p-6 bg-white">
                <h3 className="text-xl font-semibold text-primary mb-2">{study.title}</h3>
                <p className="text-text/70">{study.description}</p>
                <button className="mt-4 text-accent font-semibold text-sm hover:text-accent/80 transition-colors">
                  Read Case Study →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
