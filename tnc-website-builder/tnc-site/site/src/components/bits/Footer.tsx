export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-white py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">TNC</h3>
            <p className="text-white/80">Beautiful, intelligent digital experiences for forward-thinking brands.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Services</h4>
            <ul className="space-y-2 text-white/80">
              <li><a href="#services" className="hover:text-white transition">Standard Tier</a></li>
              <li><a href="#services" className="hover:text-white transition">Motion Tier</a></li>
              <li><a href="#services" className="hover:text-white transition">3D Premium</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Explore</h4>
            <ul className="space-y-2 text-white/80">
              <li><a href="#portfolio" className="hover:text-white transition">Portfolio</a></li>
              <li><a href="#process" className="hover:text-white transition">Process</a></li>
              <li><a href="#about" className="hover:text-white transition">About</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-white/80">
              <li>Email: hello@tncgas.com</li>
              <li>Twitter: @tncgas</li>
              <li>GitHub: OliveR19333</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-white/20 pt-8 flex justify-between items-center">
          <p className="text-white/60">&copy; {currentYear} TNC — The Network Company. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="https://twitter.com/tncgas" className="text-white/60 hover:text-white transition">Twitter</a>
            <a href="#" className="text-white/60 hover:text-white transition">LinkedIn</a>
            <a href="https://github.com/OliveR19333" className="text-white/60 hover:text-white transition">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
