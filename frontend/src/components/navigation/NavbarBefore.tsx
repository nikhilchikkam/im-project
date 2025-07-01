import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';

const NavbarBefore = () => {
  const navigate = useNavigate();
  
  return (
    <header className="w-full px-6 py-4 flex justify-between items-center border-b">
      <div 
        className="text-2xl font-bold cursor-pointer hover:text-blue-600 transition-colors"
        onClick={() => navigate('/')}
      >
        Nutrition Logo
      </div>
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
