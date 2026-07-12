import { useReveal } from '@/hooks/useAnimationTimeline';

export default function Hero() {
  const ref = useReveal({ duration: 1000 });

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary to-secondary px-4">
      <div className="text-center max-w-4xl" ref={ref}>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
          Welcome to Your Brand
        </h1>
        <p className="text-xl md:text-2xl text-white/80 mb-8">
          Create amazing digital experiences with our modern web solutions.
        </p>
        <button className="px-8 py-4 bg-accent hover:bg-accent/80 text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105">
          Get Started
        </button>
      </div>
    </section>
  );
}
