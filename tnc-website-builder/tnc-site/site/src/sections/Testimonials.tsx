import { useReveal } from '@/hooks/useAnimationTimeline';

const testimonials = [
  {
    name: 'Sarah Chen',
    company: 'Velocity Ventures',
    text: 'TNC rebuilt our site in 3 weeks. The motion design closed deals. Best investment we made.',
    tier: 'Motion',
    result: '+120% qualified leads',
  },
  {
    name: 'Marcus Johnson',
    company: 'Creative Agency',
    text: 'Finally a partner who understands performance AND beauty. They deliver both.',
    tier: 'Motion',
    result: 'Site traffic 3x',
  },
  {
    name: 'Elena Rodriguez',
    company: 'Tech SaaS',
    text: 'The 3D hero moment was a game-changer. Enterprise clients are impressed. Highly recommend.',
    tier: '3D Premium',
    result: 'Sales +250k/mo',
  },
  {
    name: 'David Park',
    company: 'Design Studio',
    text: 'TNC handles all updates, hosting, SEO—we just focus on business. Worth every penny.',
    tier: 'Motion',
    result: 'Zero ops overhead',
  },
  {
    name: 'Nina Patel',
    company: 'Luxury Brand',
    text: 'The attention to detail is unmatched. Our site looks premium because TNC demands it.',
    tier: 'Motion',
    result: 'Brand perception +89%',
  },
  {
    name: 'Alex Mueller',
    company: 'E-commerce',
    text: 'Fast, beautiful, and actually converts. TNC knows what they\'re doing.',
    tier: 'Standard',
    result: 'Conversion +45%',
  },
];

export default function Testimonials() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">What Clients Achieve</h2>
          <p className="text-xl text-text/70">
            Real results from real brands who trust TNC to deliver.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.name} className="p-8 bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow">
              {/* Stars */}
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">★</span>
                ))}
              </div>

              {/* Quote */}
              <p className="text-text/70 mb-6 italic">"{testimonial.text}"</p>

              {/* Result highlight */}
              <div className="mb-6 p-4 bg-secondary/10 rounded-lg border-l-4 border-accent">
                <p className="font-bold text-accent text-sm">{testimonial.result}</p>
              </div>

              {/* Author */}
              <div className="border-t border-text/10 pt-4">
                <p className="font-semibold text-primary">{testimonial.name}</p>
                <p className="text-sm text-text/60 mb-2">{testimonial.company}</p>
                <span className="inline-block px-2 py-1 bg-secondary/20 text-secondary text-xs font-semibold rounded">
                  {testimonial.tier}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
