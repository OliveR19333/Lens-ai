import { useReveal } from '@/hooks/useAnimationTimeline';

const phases = [
  { num: 1, title: 'Intake', desc: 'Understand your vision, goals, and brand' },
  { num: 2, title: 'Concept', desc: 'Design direction + mood board approval' },
  { num: 3, title: 'Assets', desc: 'Generate hero imagery + motion loops' },
  { num: 4, title: 'Build', desc: 'Assemble site from tnc-starter template' },
  { num: 5, title: 'Motion', desc: 'Tune animations + scroll choreography' },
  { num: 6, title: 'Meta', desc: 'SEO, OG tags, analytics setup' },
  { num: 7, title: 'Launch', desc: 'Deploy to your domain on Cloudflare' },
  { num: 8, title: 'Manage', desc: 'Ongoing updates + support (included)' },
];

export default function Process() {
  const ref = useReveal();

  return (
    <section id="process" className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Our Process</h2>
          <p className="text-xl text-text/70">
            Eight phases from concept to launch. Every step proven, every gate locked.
          </p>
        </div>

        {/* Desktop: Horizontal timeline */}
        <div className="hidden md:block">
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute top-8 left-0 right-0 h-1 bg-gradient-to-r from-secondary via-accent to-secondary" />

            {/* Phase circles */}
            <div className="grid grid-cols-8 gap-4 relative z-10">
              {phases.map((phase) => (
                <div key={phase.num} className="flex flex-col items-center">
                  {/* Circle with number */}
                  <div className="w-16 h-16 bg-white border-4 border-secondary rounded-full flex items-center justify-center font-bold text-secondary mb-4 shadow-md">
                    {phase.num}
                  </div>
                  {/* Title and description */}
                  <div className="text-center">
                    <h3 className="font-semibold text-primary text-sm">{phase.title}</h3>
                    <p className="text-xs text-text/60 mt-1">{phase.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile: Vertical stacked */}
        <div className="md:hidden space-y-4">
          {phases.map((phase, idx) => (
            <div key={phase.num} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 bg-secondary text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {phase.num}
                </div>
                {idx < phases.length - 1 && <div className="w-1 h-8 bg-secondary/30 mt-2" />}
              </div>
              <div className="flex-1 pt-2 pb-4">
                <h3 className="font-semibold text-primary">{phase.title}</h3>
                <p className="text-sm text-text/70">{phase.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <p className="text-lg text-text/70 mb-6">
            This is how we guarantee every site ships on time, on brand, and on performance.
          </p>
          <button className="px-8 py-3 bg-secondary text-white font-semibold rounded-lg hover:bg-secondary/90 transition-colors">
            Start Phase 1 Today
          </button>
        </div>
      </div>
    </section>
  );
}
