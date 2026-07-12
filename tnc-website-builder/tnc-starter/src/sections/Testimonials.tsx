import { useReveal } from '@/hooks/useAnimationTimeline';

const testimonials = [
  { name: 'Client 1', company: 'Acme Corp', text: 'Amazing work! Highly recommended.' },
  { name: 'Client 2', company: 'Tech Startup', text: 'Professional and efficient. Great results!' },
  { name: 'Client 3', company: 'Local Business', text: 'Best decision we made for our online presence.' },
];

export default function Testimonials() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold mb-12 text-center">What Our Clients Say</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.name} className="p-8 bg-white rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">★</span>
                ))}
              </div>
              <p className="text-text/70 mb-4">"{testimonial.text}"</p>
              <div>
                <p className="font-semibold">{testimonial.name}</p>
                <p className="text-sm text-text/60">{testimonial.company}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
