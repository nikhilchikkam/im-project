import { Link } from 'react-router-dom';
import { Button } from './Button';

const NavbarBefore = () => {
  return (
    <header className="w-full px-6 py-4 flex justify-between items-center border-b">
      <div className="text-xl font-bold">Nutrition Logo</div>
      <nav className="flex gap-6 text-base font-medium">
        <Link to="/products">Products</Link>
        <Link to="/pricing">Pricing</Link>
        <Link to="/resources">Resources</Link>
        <Link to="/contact">Contact us</Link>
        <Link to="/signup">
          <Button size="sm">Sign up</Button>
        </Link>
      </nav>
    </header>
  );
};

export default NavbarBefore;
