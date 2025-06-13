import { Heart, ShoppingCart, User, Search, X } from 'lucide-react';
import { Button } from './Button';
import { useState } from 'react';

const NavbarAfter = () => {
  const [query, setQuery] = useState('');

  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-neutral-200">
      <div className="text-xl font-bold">Nutrition Logo</div>

      <div className="flex items-center gap-6">
        <nav className="hidden md:flex space-x-6 text-base font-medium text-neutral-900">
          <a href="#">Products</a>
          <a href="#">Pricing</a>
          <a href="#">Resources</a>
          <a href="#">Contact us</a>
        </nav>

        <div className="hidden md:flex items-center space-x-4">
          <div className="relative">
            <Heart className="w-5 h-5" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-600" />
          </div>
          <div className="relative">
            <ShoppingCart className="w-5 h-5" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-600" />
          </div>
          <User className="w-5 h-5" />
        </div>
      </div>

      <div className="flex items-center gap-4 ml-4">
        <div className="relative flex items-center border border-gray-400 rounded-md px-3 py-1.5">
          <Search className="w-4 h-4 text-gray-500 mr-2" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            type="text"
            placeholder="Search Products"
            className="bg-transparent outline-none placeholder:text-gray-400"
          />
          {query && (
            <X
              className="w-4 h-4 text-gray-500 ml-2 cursor-pointer"
              onClick={() => setQuery('')}
            />
          )}
        </div>
      </div>
    </header>
  );
};

export default NavbarAfter;