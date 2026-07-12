import { useEffect } from 'react';
import { applyBrandConfig, defaultBrandConfig } from '@/brand.config';
import './App.css';

// Sections
import Hero from '@/sections/Hero';
import About from '@/sections/About';
import Services from '@/sections/Services';
import MotionShowcase from '@/sections/MotionShowcase';
import Gallery from '@/sections/Gallery';
import Process from '@/sections/Process';
import Testimonials from '@/sections/Testimonials';
import Contact from '@/sections/Contact';

// Navigation
import Navbar from '@/components/Navbar';
import Footer from '@/components/bits/Footer';

export default function App() {
  useEffect(() => {
    // Apply brand config on mount
    applyBrandConfig(defaultBrandConfig);
  }, []);

  return (
    <div className="min-h-screen bg-bg text-text">
      <Navbar />
      <main>
        <Hero />
        <About />
        <Services />
        <MotionShowcase />
        <Gallery />
        <Process />
        <Testimonials />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}
