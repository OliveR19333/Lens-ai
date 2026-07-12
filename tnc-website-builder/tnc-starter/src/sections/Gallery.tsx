import { useReveal } from '@/hooks/useAnimationTimeline';

const galleryItems = [
  { id: 1, title: 'Project 1', category: 'Web Design' },
  { id: 2, title: 'Project 2', category: 'Branding' },
  { id: 3, title: 'Project 3', category: 'Web Design' },
  { id: 4, title: 'Project 4', category: 'Development' },
  { id: 5, title: 'Project 5', category: 'Branding' },
  { id: 6, title: 'Project 6', category: 'Development' },
];

export default function Gallery() {
  const ref = useReveal();

  return (
    <section className="py-20 px-4 max-w-6xl mx-auto" ref={ref}>
      <h2 className="text-4xl font-bold mb-12 text-center">Our Work</h2>
      <div className="grid md:grid-cols-3 gap-6">
        {galleryItems.map((item) => (
          <div
            key={item.id}
            className="group overflow-hidden rounded-lg bg-gradient-to-br from-primary to-secondary h-64 cursor-pointer transform hover:scale-105 transition-transform duration-300"
          >
            <div className="w-full h-full flex items-center justify-center bg-primary/20">
              <div className="text-center text-white">
                <h3 className="text-xl font-semibold">{item.title}</h3>
                <p className="text-sm text-white/80">{item.category}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
