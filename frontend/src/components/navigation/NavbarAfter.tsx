import { Heart, ShoppingCart, User, Menu, Palette } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { useCartWishlist } from '../../contexts/CartWishlistContext';

const NavbarAfter = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { cartCount, wishlistCount } = useCartWishlist();
  
  const isNutsVersion = location.pathname === '/products-nuts';

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
        {/* UI Toggle Button */}
        <button 
          onClick={() => navigate(isNutsVersion ? '/products' : '/products-nuts')} 
          className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          title={`Switch to ${isNutsVersion ? 'Original' : 'Nuts.com'} UI`}
        >
          <Palette className="w-3 h-3" />
          {isNutsVersion ? 'Original' : 'Nuts.com'}
        </button>
        
        <button onClick={() => navigate('/wishlist')} className="focus:outline-none relative">
          <Heart className="w-5 h-5 md:w-8 md:h-8" />
          {wishlistCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
              {wishlistCount > 99 ? '99+' : wishlistCount}
            </span>
          )}
        </button>
        <button onClick={() => navigate('/cart')} className="focus:outline-none relative">
          <ShoppingCart className="w-5 h-5 md:w-8 md:h-8" />
          {cartCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
              {cartCount > 99 ? '99+' : cartCount}
            </span>
          )}
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
          <div ref={menuRef} className="absolute right-0 top-12 mt-2 w-48 bg-white border rounded-lg shadow-lg z-50 flex flex-col py-2">
            <button
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate(isNutsVersion ? '/products' : '/products-nuts'); }}
            >
              <Palette className="w-4 h-4" />
              Switch to {isNutsVersion ? 'Original' : 'Nuts.com'} UI
            </button>
            <div className="border-t border-gray-200 my-1"></div>
            <button
              className="flex items-center justify-between px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate('/wishlist'); }}
            >
              <div className="flex items-center gap-2">
                <Heart className="w-5 h-5" /> Wishlist
              </div>
              {wishlistCount > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                  {wishlistCount > 99 ? '99+' : wishlistCount}
                </span>
              )}
            </button>
            <button
              className="flex items-center justify-between px-4 py-2 text-gray-700 hover:bg-gray-100 text-base"
              onClick={() => { setMobileMenuOpen(false); navigate('/cart'); }}
            >
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-5 h-5" /> Cart
              </div>
              {cartCount > 0 && (
                <span className="bg-blue-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                  {cartCount > 99 ? '99+' : cartCount}
                </span>
              )}
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