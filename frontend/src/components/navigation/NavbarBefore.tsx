import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Menu } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const NavbarBefore = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMobileMenuOpen(false);
      }
    }
    if (mobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [mobileMenuOpen]);

  return (
    <header className="w-full px-4 md:px-6 py-3 md:py-4 flex justify-between items-center border-b">
      <div 
        className="flex items-center cursor-pointer hover:opacity-80 transition-opacity"
        onClick={() => navigate('/')}
      >
        <img 
          src="/nutrigence.PNG" 
          alt="Nutrigence Logo" 
          className="h-8 md:h-10 w-auto"
        />
      </div>
      {/* Desktop nav */}
      <nav className="hidden sm:flex gap-3 md:gap-6 text-base font-medium">
        <Link to="/products">Products</Link>
        <Link to="/pricing">Pricing</Link>
        <Link to="/resources">Resources</Link>
        <Link to="/contact">Contact us</Link>
        <Link to="/signup">
          <Button size="sm">Sign up</Button>
        </Link>
      </nav>
      {/* Mobile nav: Hamburger menu */}
      <div className="flex sm:hidden items-center relative">
        <button onClick={() => setMobileMenuOpen((v) => !v)} className="focus:outline-none">
          <Menu className="w-7 h-7" />
        </button>
        {mobileMenuOpen && (
          <div ref={menuRef} className="absolute right-0 top-12 mt-2 w-48 bg-white border rounded-lg shadow-lg z-50 flex flex-col py-2">
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base text-left"
              onClick={() => { setMobileMenuOpen(false); navigate('/products'); }}
            >
              Products
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base text-left"
              onClick={() => { setMobileMenuOpen(false); navigate('/pricing'); }}
            >
              Pricing
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base text-left"
              onClick={() => { setMobileMenuOpen(false); navigate('/resources'); }}
            >
              Resources
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base text-left"
              onClick={() => { setMobileMenuOpen(false); navigate('/contact'); }}
            >
              Contact us
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 text-base text-left font-semibold"
              onClick={() => { setMobileMenuOpen(false); navigate('/signup'); }}
            >
              Sign up
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default NavbarBefore;
