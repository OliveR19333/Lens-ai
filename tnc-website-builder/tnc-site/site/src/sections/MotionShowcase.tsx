import { Suspense, lazy } from 'react';
import { useReveal } from '@/hooks/useAnimationTimeline';

// Lazy load 3D scene to avoid blocking main thread
const Scene3D = lazy(() => import('@/components/3D/Scene3D'));

export default function MotionShowcase() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 bg-gradient-to-br from-primary via-primary/80 to-secondary/20" ref={ref}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Motion That Moves</h2>
          <p className="text-xl text-white/80 max-w-2xl mx-auto">
            The Motion tier brings your brand to life. Scroll-triggered animations, video backgrounds,
            and strategic 3D moments that engage without overwhelming.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left: 3D Scene */}
          <div className="order-2 md:order-1">
            <Suspense fallback={
              <div className="w-full h-96 bg-primary/20 rounded-lg flex items-center justify-center">
                <p className="text-white/60">Loading 3D scene...</p>
              </div>
            }>
              <Scene3D />
            </Suspense>
          </div>

          {/* Right: Features */}
          <div className="order-1 md:order-2 text-white">
            <h3 className="text-3xl font-bold mb-8">What's Included</h3>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent text-white font-bold">
                    ✓
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Scroll-Triggered Animations</h4>
                  <p className="text-white/80">
                    Sections fade and slide into view as users scroll. Entrance timelines are tuned for impact.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent text-white font-bold">
                    ✓
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Video Hero Loops</h4>
                  <p className="text-white/80">
                    Seamless background motion loops (3–6s) set the mood and keep visitors engaged.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent text-white font-bold">
                    ✓
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Parallax & Scroll Choreography</h4>
                  <p className="text-white/80">
                    GSAP ScrollTrigger orchestrates micro-interactions. One attention moment per viewport.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent text-white font-bold">
                    ✓
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Micro-Interactions</h4>
                  <p className="text-white/80">
                    Hover states, button animations, and card reveals make every interaction feel intentional.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-accent text-white font-bold">
                    ✓
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2">Accessibility First</h4>
                  <p className="text-white/80">
                    Respects <code className="bg-white/10 px-2 py-1 rounded text-sm">prefers-reduced-motion</code>. No motion overload.
                  </p>
                </div>
              </div>
            </div>

            <button className="mt-8 px-8 py-4 bg-accent text-white font-semibold rounded-lg hover:bg-accent/90 transition-colors transform hover:scale-105">
              Explore Motion Tier
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-16 grid md:grid-cols-3 gap-8 text-white text-center">
          <div>
            <div className="text-4xl font-bold mb-2">+120%</div>
            <p className="text-white/80">Avg. engagement increase</p>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">60fps</div>
            <p className="text-white/80">Smooth on all devices</p>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">2-3 weeks</div>
            <p className="text-white/80">From concept to launch</p>
          </div>
        </div>
      </div>
    </section>
  );
}
