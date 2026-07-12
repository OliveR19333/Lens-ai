import { useState } from 'react';
import { useReveal } from '@/hooks/useAnimationTimeline';

export default function Contact() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const ref = useReveal();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    setFormData({ name: '', email: '', message: '' });
    alert('Thank you for your message! We\'ll get back to you soon.');
  };

  return (
    <section className="py-20 px-4 max-w-2xl mx-auto" ref={ref}>
      <h2 className="text-4xl font-bold mb-12 text-center">Get In Touch</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-semibold mb-2">Name</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 border border-primary/20 rounded-lg focus:outline-none focus:border-primary"
            placeholder="Your name"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-2">Email</label>
          <input
            type="email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-2 border border-primary/20 rounded-lg focus:outline-none focus:border-primary"
            placeholder="your@email.com"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold mb-2">Message</label>
          <textarea
            required
            value={formData.message}
            onChange={(e) => setFormData({ ...formData, message: e.target.value })}
            className="w-full px-4 py-2 border border-primary/20 rounded-lg focus:outline-none focus:border-primary h-32"
            placeholder="Your message..."
          />
        </div>
        <button
          type="submit"
          className="w-full bg-primary hover:bg-primary/90 text-white py-3 rounded-lg font-semibold transition-colors"
        >
          Send Message
        </button>
      </form>
    </section>
  );
}
