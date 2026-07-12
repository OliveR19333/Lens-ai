export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-white py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">Brand</h3>
            <p className="text-white/80">Creating beautiful digital experiences.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Services</h4>
            <ul className="space-y-2 text-white/80">
              <li><a href="#" className="hover:text-white transition">Web Design</a></li>
              <li><a href="#" className="hover:text-white transition">Development</a></li>
              <li><a href="#" className="hover:text-white transition">SEO</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-white/80">
              <li><a href="#" className="hover:text-white transition">About</a></li>
              <li><a href="#" className="hover:text-white transition">Portfolio</a></li>
              <li><a href="#" className="hover:text-white transition">Blog</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-white/80">
              <li>Email: hello@brand.com</li>
              <li>Phone: (555) 123-4567</li>
              <li>Address: City, State ZIP</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-white/20 pt-8 flex justify-between items-center">
          <p className="text-white/60">&copy; {currentYear} Your Brand. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="text-white/60 hover:text-white transition">Twitter</a>
            <a href="#" className="text-white/60 hover:text-white transition">LinkedIn</a>
            <a href="#" className="text-white/60 hover:text-white transition">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
