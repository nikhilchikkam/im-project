import { Heart, ShoppingCart, User, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';

const NavbarAfter = () => {
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
    <header className="w-full px-4 md:px-6 py-3 md:py-4 flex items-center justify-between border-b border-neutral-200">
      <div 
        className="text-xl md:text-2xl font-bold cursor-pointer hover:text-blue-600 transition-colors"
        onClick={() => navigate('/')}
      >
        Nutrition Logo
      </div>
      {/* Desktop nav */}
      <div className="hidden sm:flex items-center gap-4 md:gap-10">
        <button onClick={() => navigate('/wishlist')} className="focus:outline-none">
          <Heart className="w-5 h-5 md:w-8 md:h-8" />
        </button>
        <button onClick={() => navigate('/cart')} className="focus:outline-none">
          <ShoppingCart className="w-5 h-5 md:w-8 md:h-8" />
        </button>
        <button onClick={() => navigate('/profile')} className="focus:outline-none">
          <User className="w-5 h-5 md:w-8 md:h-8" />
        </button>
      </div>
      {/* Mobile nav: Hamburger menu */}
      <div className="flex sm:hidden items-center relative">
        <button onClick={() => setMobileMenuOpen((v) => !v)} className="focus:outline-none">
          <Menu className="w-7 h-7" />
        </button>
        {mobileMenuOpen && (
          <div ref={menuRef} className="absolute right-0 top-12 mt-2 w-40 bg-white border rounded-lg shadow-lg z-50 flex flex-col py-2">
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate('/wishlist'); }}
            >
              <Heart className="w-5 h-5" /> Wishlist
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate('/cart'); }}
            >
              <ShoppingCart className="w-5 h-5" /> Cart
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate('/profile'); }}
            >
              <User className="w-5 h-5" /> Profile
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default NavbarAfter;