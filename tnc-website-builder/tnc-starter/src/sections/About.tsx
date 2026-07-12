import { useReveal } from '@/hooks/useAnimationTimeline';

export default function About() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 max-w-6xl mx-auto" ref={ref}>
      <h2 className="text-4xl font-bold mb-8">About Us</h2>
      <div className="grid md:grid-cols-2 gap-12">
        <div>
          <p className="text-lg text-text/80 mb-4">
            We create beautiful, fast, and accessible websites that help businesses grow.
          </p>
          <p className="text-lg text-text/80">
            Our team specializes in modern web technologies and user-centered design.
          </p>
        </div>
        <div className="bg-primary/10 rounded-lg p-8">
          <h3 className="text-2xl font-semibold mb-4">Why Choose Us?</h3>
          <ul className="space-y-3">
            <li>✓ Custom, hand-coded solutions</li>
            <li>✓ Lightning-fast performance</li>
            <li>✓ Mobile-first design</li>
            <li>✓ Ongoing support & updates</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
