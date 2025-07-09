import { Heart, ShoppingCart, Maximize2 } from 'lucide-react';

interface ProductCardProps {
  upc: string;
  title?: string;
  normalized_name?: string;
  name?: string;
  category?: string;
  description?: string;
  isSmartSnack?: boolean;
  novaLabel?: string;
  isGoodChoice?: string;
  isFavorite?: boolean;
  onFavorite?: () => void;
  onAddToCart?: () => void;
  onEnlarge?: () => void;
}

const ProductCard: React.FC<ProductCardProps> = ({
  upc,
  title,
  normalized_name,
  name,
  category,
  description,
  isSmartSnack,
  novaLabel,
  isGoodChoice,
  onEnlarge,
  onAddToCart,
  onFavorite,
}) => {
  const displayTitle = normalized_name?.trim()
    ? normalized_name
    : (name?.trim() ? name : (title?.trim() ? title : 'N/A'));
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
      <div className="font-bold text-lg mb-1 leading-tight">{displayTitle}</div>
      <div className="mb-2 flex items-center gap-2 flex-wrap">
        <span className="inline-block bg-green-50 text-green-700 text-xs font-semibold rounded px-2 py-1 align-middle">• {category}</span>
        {isSmartSnack && (
          <span className="inline-block bg-green-50 text-green-700 text-xs font-semibold rounded px-2 py-1 align-middle ml-2">Smart Snack</span>
        )}
        {isGoodChoice === 'true' && (
          <span className="inline-block bg-emerald-100 text-emerald-700 text-xs font-semibold rounded px-2 py-1 align-middle ml-2">Good Choice</span>
        )}
        {novaLabel && (
          <span className="inline-block bg-blue-50 text-blue-700 text-xs font-semibold rounded px-2 py-1 align-middle ml-2">Processing Level: {novaLabel}</span>
        )}
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