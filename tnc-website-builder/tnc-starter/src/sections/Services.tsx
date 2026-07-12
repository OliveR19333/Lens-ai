import { useReveal } from '@/hooks/useAnimationTimeline';

const services = [
  { icon: '🎨', title: 'Web Design', desc: 'Beautiful, modern websites' },
  { icon: '⚡', title: 'Performance', desc: 'Blazingly fast load times' },
  { icon: '📱', title: 'Responsive', desc: 'Perfect on all devices' },
  { icon: '🔒', title: 'Secure', desc: 'Enterprise-grade security' },
  { icon: '🔍', title: 'SEO', desc: 'Search engine optimized' },
  { icon: '🚀', title: 'Deployment', desc: 'Instant global distribution' },
];

export default function Services() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold mb-12 text-center">Our Services</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {services.map((service) => (
            <div key={service.title} className="p-6 bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">{service.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{service.title}</h3>
              <p className="text-text/70">{service.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
