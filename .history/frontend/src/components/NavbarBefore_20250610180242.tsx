import { Button } from './Button';
import { Search } from 'lucide-react';

export const NavbarBefore = () => {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-neutral-200">
      <div className="text-xl font-bold">Nutrition Logo</div>

      <nav className="hidden md:flex space-x-6 text-base font-medium text-neutral-900">
        <a href="#">Products</a>
        <a href="#">Pricing</a>
        <a href="#">Resources</a>
        <a href="#">Contact us</a>
      </nav>

      <div className="flex items-center gap-4">
        <div className="relative hidden md:flex items-center border border-gray-400 rounded-md px-3 py-1.5">
          <Search className="w-4 h-4 text-gray-500 mr-2" />
          <input
            type="text"
            placeholder="Search Products"
            className="bg-transparent outline-none placeholder:text-gray-400"
          />
        </div>
        <Button size="sm">Login</Button>
      </div>
    </header>
  );
};
