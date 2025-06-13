type Props = {
  onNavigate: (section: 'products' | 'pricing' | 'resources') => void;
};

const NavbarBefore = ({ onNavigate }: Props) => {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-neutral-200">
      <div className="text-xl font-bold">Nutrition Logo</div>
      <nav className="flex gap-6 font-medium text-base">
        <button onClick={() => onNavigate('products')}>Products</button>
        <button onClick={() => onNavigate('pricing')}>Pricing</button>
        <button onClick={() => onNavigate('resources')}>Resources</button>
        <button>Contact us</button> {/* Can scroll to footer later */}
      </nav>
      <button className="bg-blue-600 text-white rounded-xl px-4 py-1">Sign up</button>
    </header>
  );
};

export default NavbarBefore;
