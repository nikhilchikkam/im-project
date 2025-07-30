import React, { useState } from 'react';
import { useCartWishlist } from '../../contexts/CartWishlistContext';
import { Minus, Plus, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';

interface CartItem {
  id: number;
  gtin: string;
  quantity: number;
  added_at: string;
  product: {
    name: string;
    image_urls: string[] | null;
    product_type: string;
    description: string;
    normalized_name?: string;
  };
}

const CartList = ({ items }: { items: CartItem[] }) => {
  const { updateCartQuantity, removeFromCart, loading } = useCartWishlist();

  const handleQuantityChange = async (gtin: string, newQuantity: number) => {
    if (newQuantity >= 1) {
      await updateCartQuantity(gtin, newQuantity);
    }
  };

  const handleRemove = async (gtin: string) => {
    await removeFromCart(gtin);
  };

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold mb-6">Your Cart Items</h2>
      <div className="space-y-4">
        {items.map((item) => {
          // Handle image_urls - cart items have JSON object stored as string
          let imageUrls: string[] = [];
          if (item.product.image_urls) {
            try {
              // Parse JSON if it's a string, or use directly if it's already an object
              const imageData = typeof item.product.image_urls === 'string' 
                ? JSON.parse(item.product.image_urls) 
                : item.product.image_urls;
              
              // Extract URLs from the nested structure
              if (imageData && typeof imageData === 'object') {
                if (Array.isArray(imageData.externalFileLink)) {
                  imageUrls = imageUrls.concat(imageData.externalFileLink.filter(Boolean));
                }
                if (Array.isArray(imageData.dam)) {
                  imageUrls = imageUrls.concat(imageData.dam.filter(Boolean));
                }
              }
            } catch (error) {
              console.error('Error parsing image_urls:', error);
            }
          }

          return (
            <CartItemComponent 
              key={item.id} 
              item={item} 
              imageUrls={imageUrls}
              onQuantityChange={handleQuantityChange}
              onRemove={handleRemove}
              loading={loading}
            />
          );
        })}
      </div>
    </div>
  );
};

// Separate component for individual cart item with carousel
const CartItemComponent = ({ 
  item, 
  imageUrls, 
  onQuantityChange, 
  onRemove, 
  loading 
}: { 
  item: CartItem; 
  imageUrls: string[]; 
  onQuantityChange: (gtin: string, quantity: number) => Promise<void>;
  onRemove: (gtin: string) => Promise<void>;
  loading: boolean;
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());
  const [imageTimestamp, setImageTimestamp] = useState(Date.now());

  // Filter out failed images
  const workingImages = React.useMemo(() => {
    return imageUrls.filter(url => !failedImages.has(url));
  }, [imageUrls, failedImages]);

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

  const handleImageError = (imageUrl: string) => {
    setFailedImages(prev => new Set([...prev, imageUrl]));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border">
      <div className="flex items-start gap-4">
        {/* Product Image with Carousel */}
        <div className="w-24 h-24 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0 relative group">
          {workingImages && workingImages.length > 0 ? (
            <>
              <img
                src={`${workingImages[currentImageIndex]}?t=${imageTimestamp}`}
                alt={`${item.product.name} - Image ${currentImageIndex + 1}`}
                className="w-full h-full object-cover"
                key={`${currentImageIndex}-${workingImages[currentImageIndex]}-${imageTimestamp}`}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  handleImageError(target.src.split('?')[0]);
                }}
              />
              {workingImages.length > 1 && (
                <>
                  <button
                    className="absolute left-1 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-0.5 hover:bg-opacity-75 transition-opacity z-10 opacity-0 group-hover:opacity-100"
                    onClick={prevImage}
                  >
                    <ChevronLeft className="w-3 h-3" />
                  </button>
                  <button
                    className="absolute right-1 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-0.5 hover:bg-opacity-75 transition-opacity z-10 opacity-0 group-hover:opacity-100"
                    onClick={nextImage}
                  >
                    <ChevronRight className="w-3 h-3" />
                  </button>
                  {/* Image counter */}
                  <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white text-xs px-1 py-0.5 rounded z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                    {currentImageIndex + 1} / {workingImages.length}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>

        {/* Product Details */}
        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-1">
            {item.product.normalized_name || item.product.name}
          </h3>
          <p className="text-gray-600 text-sm mb-2">
            {item.product.description || 'No description available'}
          </p>
          <p className="text-sm text-gray-500">UPC/GTIN: {item.gtin}</p>
        </div>

        {/* Quantity Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center border rounded-lg">
            <button
              className="p-2 hover:bg-gray-100 disabled:opacity-50"
              onClick={() => onQuantityChange(item.gtin, item.quantity - 1)}
              disabled={loading || item.quantity <= 1}
            >
              <Minus className="w-4 h-4" />
            </button>
            <span className="px-4 py-2 font-semibold min-w-[3rem] text-center">
              {item.quantity}
            </span>
            <button
              className="p-2 hover:bg-gray-100 disabled:opacity-50"
              onClick={() => onQuantityChange(item.gtin, item.quantity + 1)}
              disabled={loading}
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* Remove Button */}
          <button
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            onClick={() => onRemove(item.gtin)}
            disabled={loading}
            title="Remove from cart"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartList; 