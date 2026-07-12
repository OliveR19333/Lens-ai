import { useState } from 'react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { label: 'Work', href: '#portfolio' },
    { label: 'Services', href: '#services' },
    { label: 'Process', href: '#process' },
    { label: 'About', href: '#about' },
    { label: 'Contact', href: '#contact' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur shadow-sm">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="text-2xl font-bold text-primary">TNC</div>

          {/* Desktop menu */}
          <div className="hidden md:flex gap-8">
            {links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-text hover:text-primary transition-colors font-medium"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* CTA Button */}
          <button className="hidden md:block px-6 py-2 bg-accent hover:bg-accent/90 text-white rounded-lg font-semibold transition-colors">
            Inquire
          </button>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2"
          >
            <div className="space-y-1">
              <div className="w-6 h-0.5 bg-text"></div>
              <div className="w-6 h-0.5 bg-text"></div>
              <div className="w-6 h-0.5 bg-text"></div>
            </div>
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="block px-4 py-2 text-text hover:bg-primary/10 rounded transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
