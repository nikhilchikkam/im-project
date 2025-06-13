import { Heart, ShoppingCart, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const NavbarAfter = () => {
  const navigate = useNavigate();
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-neutral-200">
      <div className="text-2xl font-bold">Nutrition Logo</div>
      <div className="flex items-center gap-10">
        <button onClick={() => navigate('/wishlist')} className="focus:outline-none">
          <Heart className="w-8 h-8" />
        </button>
        <button onClick={() => navigate('/cart')} className="focus:outline-none">
          <ShoppingCart className="w-8 h-8" />
        </button>
        <button onClick={() => navigate('/profile')} className="focus:outline-none">
          <User className="w-8 h-8" />
        </button>
      </div>
    </header>
  );
};

export default NavbarAfter;