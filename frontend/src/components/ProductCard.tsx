import { Heart, ShoppingCart, Maximize2 } from 'lucide-react';

type ProductCardProps = {
  upc: string;
  title: string;
  category: string;
  description: string;
  isFavorite?: boolean;
  onFavorite?: () => void;
  onAddToCart?: () => void;
  onEnlarge?: () => void;
};

const ProductCard = ({ upc, title, category, description, isFavorite, onFavorite, onAddToCart, onEnlarge }: ProductCardProps) => {
  return (
    <div className="border rounded-lg p-4 shadow-sm hover:shadow-md transition bg-white flex flex-col min-h-[260px] relative">
      <div className="flex items-center justify-between mb-2 w-full">
        <span className="text-xs text-gray-500">UPC/GTIN: {upc}</span>
        <div className="flex items-center gap-2">
          <input type="checkbox" />
          {onEnlarge && (
            <button
              className="text-gray-400 hover:text-gray-700 p-1 rounded"
              onClick={onEnlarge}
              aria-label="Enlarge product details"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
      <div className="font-bold text-lg mb-1 leading-tight">{title}</div>
      <div className="mb-2">
        <span className="inline-block bg-green-50 text-green-700 text-xs font-semibold rounded px-2 py-1 align-middle">• {category}</span>
      </div>
      <div className="text-sm text-gray-600 flex-1 mb-4">{description}</div>
      <div className="flex gap-2 mt-auto">
        <button className="flex-1 flex items-center justify-center gap-1 bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition" onClick={onFavorite}>
          <Heart className="w-5 h-5" />
        </button>
        <button className="flex-1 flex items-center justify-center gap-1 bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition" onClick={onAddToCart}>
          <ShoppingCart className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ProductCard; 