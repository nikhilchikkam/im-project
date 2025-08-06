import { Heart, ShoppingCart, Maximize2, Network, ChevronLeft, ChevronRight } from 'lucide-react';
import React, { useState, useEffect } from 'react';
import { useCartWishlist } from '../../contexts/CartWishlistContext';

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
  imageUrls?: string[] | { [key: string]: string[] }; // Support both array and nested object
  onFavorite?: () => void;
  onAddToCart?: () => void;
  onEnlarge?: () => void;
  onHierarchy?: () => void;
  onRemove?: () => void; // Custom remove handler
  isSelected?: boolean;
  onSelect?: () => void;
  showCheckbox?: boolean;
  className?: string; // Added for custom styling
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
  onRemove,
  isSelected = false,
  onSelect,
  showCheckbox = false,
  className,
}) => {
  const { 
    addToCart, 
    addToWishlist, 
    isInCart, 
    isInWishlist, 
    removeFromCart, 
    removeFromWishlist,
    loading 
  } = useCartWishlist();


  const displayTitle = normalized_name?.trim()
    ? normalized_name
    : (name?.trim() ? name : (title?.trim() ? title : 'N/A'));

  // Flatten and deduplicate imageUrls if present
  let allImages: string[] = [];
  
  if (imageUrls) {
    if (Array.isArray(imageUrls)) {
      // If it's already a string array
      allImages = imageUrls.filter(Boolean);
    } else if (typeof imageUrls === 'object') {
      // If it's an object with nested arrays (like {dam: [...], externalFileLink: [...]})
      const flattenedUrls: string[] = [];
      Object.values(imageUrls).forEach(value => {
        if (Array.isArray(value)) {
          flattenedUrls.push(...value.filter(Boolean));
        }
      });
      allImages = flattenedUrls;
    }
  }
  
  // fallback to imageUrl if no array
  if ((!allImages || allImages.length === 0) && imageUrl) {
    allImages = [imageUrl];
  }

  // Pre-filter out known problematic URLs (like dam.catalog.1worldsync.com)
  const preFilteredImages = allImages.filter(url => {
    if (url && url.includes('dam.catalog.1worldsync.com')) {
      return false;
    }
    return true;
  });

  // Ensure we have at least one image (fallback to original if all were filtered)
  const finalImages = preFilteredImages.length > 0 ? preFilteredImages : allImages;

  // Simple carousel state
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());
  const [imageTimestamp, setImageTimestamp] = useState(Date.now());
  const [previousWorkingImagesLength, setPreviousWorkingImagesLength] = useState(0);

  // Filter out failed images from final images
  const workingImages = React.useMemo(() => {
    return finalImages.filter(url => !failedImages.has(url));
  }, [finalImages, failedImages]);

  // Handle when working images change (due to failed images)
  React.useEffect(() => {
    if (previousWorkingImagesLength > 0 && workingImages.length < previousWorkingImagesLength) {
      // Some images failed, adjust index if needed
      if (currentImageIndex >= workingImages.length) {
        setCurrentImageIndex(Math.max(0, workingImages.length - 1));
      }
    }
    setPreviousWorkingImagesLength(workingImages.length);
  }, [workingImages.length, previousWorkingImagesLength, currentImageIndex]);

  const nextImage = () => {
    if (workingImages.length > 1) {
      const newIndex = (currentImageIndex + 1) % workingImages.length;
      setCurrentImageIndex(newIndex);
      setImageTimestamp(Date.now());
    }
  };

  const prevImage = () => {
    if (workingImages.length > 1) {
      const newIndex = (currentImageIndex - 1 + workingImages.length) % workingImages.length;
      setCurrentImageIndex(newIndex);
      setImageTimestamp(Date.now());
    }
  };

  // Handle image load errors
  const handleImageError = (imageUrl: string) => {
    setFailedImages(prev => new Set([...prev, imageUrl]));
  };

  // Cart and wishlist handlers
  const handleCartClick = async () => {
    if (isInCart(upc)) {
      await removeFromCart(upc);
    } else {
      await addToCart(upc);
    }
  };

  const handleWishlistClick = async () => {
    if (isInWishlist(upc)) {
      if (onRemove) {
        onRemove();
      } else {
        await removeFromWishlist(upc);
      }
    } else {
      await addToWishlist(upc);
    }
  };

  // Handle card click to open modal
  const handleCardClick = (e: React.MouseEvent) => {
    // Don't trigger if clicking on action buttons or checkbox
    const target = e.target as HTMLElement;
    const isActionButton = target.closest('button') || target.closest('input[type="checkbox"]');
    
    if (!isActionButton && onEnlarge) {
      onEnlarge();
    }
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 hover:shadow-lg hover:border-blue-300 transition-all duration-200 min-h-[320px] flex flex-col cursor-pointer ${className || ''}`}
      onClick={handleCardClick}
    >
      
      {/* Image Section */}
      <div className="relative h-56 bg-gray-100 overflow-hidden flex-shrink-0 group">
        {workingImages && workingImages.length > 0 ? (
          <>
            <img
              src={`${workingImages[currentImageIndex]}?t=${imageTimestamp}`}
              alt={`${name} - Image ${currentImageIndex + 1}`}
              className="w-full h-full object-contain"
              key={`${currentImageIndex}-${workingImages[currentImageIndex]}-${imageTimestamp}`}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                handleImageError(target.src.split('?')[0]); // Remove cache buster
              }}
            />
            {workingImages.length > 1 && (
              <>
                <button
                  className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-1 hover:bg-opacity-75 transition-opacity z-10 opacity-0 group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    prevImage();
                  }}
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-1 hover:bg-opacity-75 transition-opacity z-10 opacity-0 group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    nextImage();
                  }}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
                {/* Image counter */}
                <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                  {currentImageIndex + 1} / {workingImages.length}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-sm">No image available</span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-4 flex flex-col flex-1">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-500">UPC/GTIN: {upc}</span>
          <div className="flex items-center gap-2">
            {showCheckbox && (
                              <div 
                  className="flex items-center gap-1 bg-yellow-100 p-1 rounded cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onSelect) {
                      onSelect();
                    }
                  }}
                >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    console.log('ProductCard checkbox onChange triggered for gtin:', upc, 'isSelected:', isSelected, 'checked:', e.target.checked);
                    e.stopPropagation();
                    if (onSelect) {
                      console.log('Calling onSelect for gtin:', upc);
                      onSelect();
                    } else {
                      console.log('onSelect is not defined for gtin:', upc);
                    }
                  }}
                  className="w-6 h-6 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                  style={{ minWidth: '24px', minHeight: '24px' }}
                />
                
              </div>
            )}
            {onEnlarge && (
              <button
                className="text-gray-400 hover:text-gray-700 p-1 rounded"
                onClick={(e) => {
                  e.stopPropagation();
                  onEnlarge();
                }}
                aria-label="Enlarge product details"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
        <div className="flex flex-col flex-1">
          <div className="font-bold text-lg mb-3 leading-tight line-clamp-2 min-h-[3rem]">{displayTitle}</div>
          <div className="mb-3 flex flex-wrap gap-2 min-h-[4.5rem]">
            {category && (
              <span className="inline-flex items-center bg-green-50 text-green-700 text-xs font-medium rounded-full px-2 py-1">
                <span className="w-1 h-1 bg-green-500 rounded-full mr-1"></span>
                {category}
              </span>
            )}
            {isSmartSnack && (
              <span className="inline-flex items-center bg-blue-50 text-blue-700 text-xs font-medium rounded-full px-2 py-1">
                <span className="w-1 h-1 bg-blue-500 rounded-full mr-1"></span>
                Smart Snack
              </span>
            )}
            {isGoodChoice === 'true' && (
              <span className="inline-flex items-center bg-emerald-50 text-emerald-700 text-xs font-medium rounded-full px-2 py-1">
                <span className="w-1 h-1 bg-emerald-500 rounded-full mr-1"></span>
                Good Choice
              </span>
            )}
            {novaLabel && (
              <span className="inline-flex items-center bg-orange-50 text-orange-700 text-xs font-medium rounded-full px-2 py-1">
                <span className="w-1 h-1 bg-orange-500 rounded-full mr-1"></span>
                {novaLabel}
              </span>
            )}
          </div>
          <div className="text-sm text-gray-600 flex-1 mb-3 line-clamp-2 min-h-[3rem]">{description}</div>
        </div>
        <div className="flex gap-2 mt-auto justify-start">
          <button
            className={`p-2 transition-colors ${
              isInWishlist(upc) 
                ? 'text-red-500' 
                : 'text-blue-400 hover:text-red-400'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`} 
            onClick={(e) => {
              e.stopPropagation();
              handleWishlistClick();
            }}
            disabled={loading}
            title={isInWishlist(upc) ? 'Remove from wishlist' : 'Add to wishlist'}
          >
            <Heart className={`w-6 h-6 ${isInWishlist(upc) ? 'fill-current' : 'stroke-current'}`} />
          </button>
          <button
            className={`p-2 transition-colors ${
              isInCart(upc) 
                ? 'text-green-500' 
                : 'text-blue-400 hover:text-green-400'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`} 
            onClick={(e) => {
              e.stopPropagation();
              handleCartClick();
            }}
            disabled={loading}
            title={isInCart(upc) ? 'Remove from cart' : 'Add to cart'}
          >
            <ShoppingCart className={`w-6 h-6 ${isInCart(upc) ? 'fill-current' : 'stroke-current'}`} />
          </button>
          {onHierarchy && (
            <button
              className="p-2 text-blue-400 hover:text-blue-600 transition-colors" 
              onClick={(e) => {
                e.stopPropagation();
                onHierarchy();
              }}
              title="View Product Hierarchy"
            >
              <Network className="w-6 h-6 stroke-current" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard; 