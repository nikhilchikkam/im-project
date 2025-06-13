import { Heart, ShoppingCart } from 'lucide-react';

type ProductHeaderProps = {
  product: {
    upc: string;
    title: string;
    badges: string[];
  };
};

const badgeColors: Record<string, string> = {
  Meat: 'bg-red-100 text-red-600',
  Gluten: 'bg-yellow-100 text-yellow-700',
  Organic: 'bg-green-100 text-green-700',
};

const ProductHeader = ({ product }: ProductHeaderProps) => {
  return (
    <div>
      <div className="text-xs text-gray-500 mb-1">UPC/GTIN: {product.upc}</div>
      <div className="text-2xl font-bold mb-2 leading-tight">{product.title}</div>
      <div className="flex gap-2 mb-4">
        {product.badges.map((badge) => (
          <span
            key={badge}
            className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ${badgeColors[badge] || 'bg-gray-200 text-gray-700'}`}
          >
            {badge}
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <button className="bg-blue-600 text-white rounded-lg px-4 py-2 flex items-center gap-1 font-semibold hover:bg-blue-700 transition">
          <Heart className="w-5 h-5" /> Wishlist
        </button>
        <button className="bg-blue-600 text-white rounded-lg px-4 py-2 flex items-center gap-1 font-semibold hover:bg-blue-700 transition">
          <ShoppingCart className="w-5 h-5" /> Cart
        </button>
      </div>
    </div>
  );
};

export default ProductHeader; 