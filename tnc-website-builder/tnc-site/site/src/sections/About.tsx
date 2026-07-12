import { useReveal } from '@/hooks/useAnimationTimeline';

export default function About() {
  const ref = useReveal();

  return (
    <section id="about" className="py-20 px-4 bg-primary/5" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Our Approach</h2>
          <p className="text-xl text-text/70 max-w-2xl mx-auto">
            We believe websites should be beautiful, intelligent, and built to grow your business.
            That's why every TNC site combines motion design, performance optimization, and ongoing support.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="p-8 bg-white rounded-lg shadow-sm">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-semibold mb-3">Design First</h3>
            <p className="text-text/70">
              Every pixel is intentional. We design for your brand, your audience, and your goals—then code it to perfection.
            </p>
          </div>
          <div className="p-8 bg-white rounded-lg shadow-sm">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-3">Performance Obsessed</h3>
            <p className="text-text/70">
              Lighthouse 90+, under 2s first paint, 60fps on mobile. We optimize for speed because users demand it.
            </p>
          </div>
          <div className="p-8 bg-white rounded-lg shadow-sm">
            <div className="text-4xl mb-4">🔄</div>
            <h3 className="text-xl font-semibold mb-3">Always Evolving</h3>
            <p className="text-text/70">
              TNC Membership means your site grows with your business. Content updates, design refreshes, ongoing support—included.
            </p>
          </div>
        </div>

        <div className="bg-gradient-to-r from-secondary to-accent rounded-lg p-12 text-white text-center">
          <h3 className="text-3xl font-bold mb-4">Ready to move faster?</h3>
          <p className="text-lg text-white/90 mb-6 max-w-2xl mx-auto">
            Join forward-thinking brands building with TNC. Choose your tier, launch in weeks, not months.
          </p>
          <button className="px-8 py-3 bg-white text-secondary font-semibold rounded-lg hover:bg-primary transition-colors">
            Start Your Project
          </button>
        </div>
      </div>
    </section>
  );
}
