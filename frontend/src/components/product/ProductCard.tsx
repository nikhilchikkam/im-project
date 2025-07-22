import { Heart, ShoppingCart, Maximize2, Network, ChevronLeft, ChevronRight } from 'lucide-react';
import React, { useState } from 'react';

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
  imageUrl?: string; // fallback
  imageUrls?: string[]; // NEW: all images
  onFavorite?: () => void;
  onAddToCart?: () => void;
  onEnlarge?: () => void;
  onHierarchy?: () => void;
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
  imageUrl,
  imageUrls,
  onEnlarge,
  onAddToCart,
  onFavorite,
  onHierarchy,
}) => {
  const displayTitle = normalized_name?.trim()
    ? normalized_name
    : (name?.trim() ? name : (title?.trim() ? title : 'N/A'));

  // Flatten and deduplicate imageUrls if present
  let allImages: string[] = [];
  if (imageUrls && Array.isArray(imageUrls)) {
    allImages = imageUrls.filter(Boolean);
  }
  // fallback to imageUrl if no array
  if ((!allImages || allImages.length === 0) && imageUrl) {
    allImages = [imageUrl];
  }

  const [imgIdx, setImgIdx] = useState(0);
  const [failedIdxs, setFailedIdxs] = useState<number[]>([]);

  // Filter out failed images
  const validImages = allImages.filter((_, idx) => !failedIdxs.includes(idx));
  // If all images fail, validImages will be empty
  const currentImg = validImages.length > 0 ? validImages[imgIdx % validImages.length] : '';

  const handlePrev = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (validImages.length === 0) return;
    setImgIdx((idx) => (idx === 0 ? validImages.length - 1 : idx - 1));
  };
  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (validImages.length === 0) return;
    setImgIdx((idx) => (idx === validImages.length - 1 ? 0 : idx + 1));
  };

  const handleImgError = () => {
    // Mark this index as failed and try the next image
    if (!failedIdxs.includes(imgIdx)) {
      setFailedIdxs((prev) => [...prev, imgIdx]);
      // Try next image if available
      let nextIdx = imgIdx;
      let tries = 0;
      do {
        nextIdx = (nextIdx + 1) % allImages.length;
        tries++;
      } while (failedIdxs.includes(nextIdx) && tries < allImages.length);
      if (!failedIdxs.includes(nextIdx)) setImgIdx(nextIdx);
    }
  };

  React.useEffect(() => {
    // Reset index and failed list if images change
    setImgIdx(0);
    setFailedIdxs([]);
  }, [JSON.stringify(allImages)]);

  return (
    <div className="group border rounded-lg p-4 shadow-sm hover:shadow-md transition bg-white flex flex-col min-h-[260px] relative">
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
      {/* Product Image(s) or Placeholder */}
      <div className="mb-3 flex justify-center items-center relative min-h-48 h-48">
        {currentImg ? (
          <>
            {/* Left navigator: always show, but disabled if only one image */}
            <button
              className={`absolute left-2 z-10 rounded-full p-1 shadow opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 ${validImages.length > 1 ? 'hover:bg-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              onClick={validImages.length > 1 ? handlePrev : undefined}
              aria-label="Previous image"
              tabIndex={0}
              aria-disabled={validImages.length === 1}
              disabled={validImages.length === 1}
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
            <img
              src={currentImg}
              alt={displayTitle}
              className="w-full h-48 object-contain rounded-md bg-gray-50"
              onError={handleImgError}
            />
            {/* Right navigator: always show, but disabled if only one image */}
            <button
              className={`absolute right-2 z-10 rounded-full p-1 shadow opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 ${validImages.length > 1 ? 'hover:bg-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              onClick={validImages.length > 1 ? handleNext : undefined}
              aria-label="Next image"
              tabIndex={0}
              aria-disabled={validImages.length === 1}
              disabled={validImages.length === 1}
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          </>
        ) : (
          <div className="w-full h-48 flex flex-col items-center justify-center bg-gray-100 rounded-md text-gray-400 select-none">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a4 4 0 004 4h10a4 4 0 004-4V7a4 4 0 00-4-4H7a4 4 0 00-4 4z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11a4 4 0 118 0 4 4 0 01-8 0z" /></svg>
            <span className="text-xs">No image available</span>
          </div>
        )}
      </div>
      <div className="flex flex-col flex-1">
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
      </div>
      <div className="flex gap-2 mt-auto">
        <button className="flex-1 flex items-center justify-center gap-1 bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition" onClick={onFavorite}>
          <Heart className="w-5 h-5" />
        </button>
        <button className="flex-1 flex items-center justify-center gap-1 bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition" onClick={onAddToCart}>
          <ShoppingCart className="w-5 h-5" />
        </button>
        {onHierarchy && (
          <button 
            className="flex-1 flex items-center justify-center gap-1 bg-purple-600 text-white rounded-lg py-2 hover:bg-purple-700 transition" 
            onClick={onHierarchy}
            title="View Product Hierarchy"
          >
            <Network className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ProductCard; 