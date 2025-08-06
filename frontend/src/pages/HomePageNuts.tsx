import NavbarAfter from '../components/navigation/NavbarAfter';
import { useState, useRef, useEffect } from 'react';
import ProductDetailsModal from '../features/products/ProductDetailsModal';
import Pagination from '../components/ui/Pagination';
import { useCartWishlist } from '../contexts/CartWishlistContext';
import { useAuth, useAuthenticatedFetch } from '../contexts/AuthContext';
import { Search, Filter, Grid, List, ShoppingCart, Heart, Maximize2, Network, ChevronLeft, ChevronRight } from 'lucide-react';



// Categories from original HomePage
const categories = [
  'All Categories',
  'Beverages',
  'Bread/Bakery Products',
  'Cereal/Grain/Pulse Products',
  'Confectionery/Sugar Sweetening Products',
  'Fish and Seafood',
  'Food/Beverage Variety Packs',
  'Fresh Garnish (Food)',
  'Fruits - Unprepared/Unprocessed (Fresh)',
  'Fruits - Unprepared/Unprocessed (Frozen)',
  'Fruits - Unprepared/Unprocessed (Shelf Stable)',
  'Fruits/Vegetables Fresh & Fresh Cut',
  'Fruits/Vegetables Fresh Cut',
  'Fruits/Vegetables/Nuts/Seeds Prepared/Processed',
  'Insects Edible',
  'Leaf Vegetables - Unprepared/Unprocessed (Fresh)',
  'Meat/Fish/Seafood Substitutes',
  'Meat/Poultry/Other Animals',
  'Milk/Butter/Cream/Yogurts/Cheese/Eggs/Substitutes',
  'Nuts/Seeds - Unprepared/Unprocessed (In Shell)',
  'Nuts/Seeds - Unprepared/Unprocessed (Perishable)',
  'Oils/Fats Edible',
  'Prepared/Preserved Foods',
  'Seasonings/Preservatives/Extracts',
  'Vegetables - Unprepared/Unprocessed (Frozen)',
  'Vegetables - Unprepared/Unprocessed (Shelf Stable)',
  'Vegetables (Non Leaf) - Unprepared/Unprocessed (Fresh)',
];

// Guideline options from original HomePage
const guidelineOptions = [
  'Good Choice',
  'Smart Snack',
  'Philly',
];

const DEFAULT_LIMIT = 12;

const HomePageNuts = () => {
  const { addToWishlist, addToCart, isInCart, isInWishlist, removeFromCart, removeFromWishlist, loading } = useCartWishlist();
  const { authenticatedFetch } = useAuthenticatedFetch();
  const [selectedCategories, setSelectedCategories] = useState<string[]>(categories.slice());
  const [viewType, setViewType] = useState<'grid' | 'list'>('grid');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [products, setProducts] = useState<any[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [total, setTotal] = useState(0);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);


  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [selectedGuidelines, setSelectedGuidelines] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('popularity');

  const apiUrl = import.meta.env.VITE_API_URL || '';

  // Fetch products from API
  useEffect(() => {
    const fetchProducts = async () => {
      setLoadingProducts(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (selectedCategories.length > 0 && !selectedCategories.includes('All Categories')) {
          selectedCategories.forEach(cat => params.append('family_title', cat));
        }
        if (searchTerm) {
          params.append('search_term', searchTerm);
        }
        // Add is_smart_snack filter if Smart Snack is selected
        if (selectedGuidelines.includes('Smart Snack')) {
          params.append('is_smart_snack', 'true');
        }
        // Add is_good_choice filter if Good Choice is selected
        if (selectedGuidelines.includes('Good Choice')) {
          params.append('is_good_choice', 'true');
        }
        // Add recommended_ok filter if Philly is selected
        if (selectedGuidelines.includes('Philly')) {
          params.append('recommended_ok', 'true');
        }
        params.append('limit', limit.toString());
        params.append('offset', ((page - 1) * limit).toString());
        
        const res = await fetch(`${apiUrl}/api/products?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch products');
        const data = await res.json();
        setProducts(data.products || []);
        setTotal(data.total || 0);
      } catch (err: any) {
        setError(err.message || 'Unknown error');
      } finally {
        setLoadingProducts(false);
      }
    };
    fetchProducts();
  }, [selectedCategories, selectedGuidelines, searchTerm, page, limit, apiUrl]);

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setSearchTerm(searchInput);
      setPage(1);
    }, 400);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const handleCategoryChange = (cat: string) => {
    if (cat === 'All Categories') {
      setSelectedCategories([]);
    } else {
      setSelectedCategories([cat]);
    }
    setPage(1);
  };

  const handleGuidelineToggle = (guideline: string) => {
    setSelectedGuidelines(prev => 
      prev.includes(guideline) 
        ? prev.filter(g => g !== guideline)
        : [...prev, guideline]
    );
  };

  const handleItemSelect = (gtin: string) => {
    setSelectedItems(prev => 
      prev.includes(gtin) 
        ? prev.filter(item => item !== gtin)
        : [...prev, gtin]
    );
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]);
      setSelectAll(false);
    } else {
      setSelectedItems(products.map(item => item.gtin));
      setSelectAll(true);
    }
  };

  const handleMoveToWishlist = async () => {
    try {
      for (const gtin of selectedItems) {
        await addToWishlist(gtin);
      }
      setSelectedItems([]);
      setSelectAll(false);
    } catch (error) {
      console.error('Failed to move items to wishlist:', error);
    }
  };

  const handleMoveToCart = async () => {
    try {
      for (const gtin of selectedItems) {
        await addToCart(gtin);
      }
      setSelectedItems([]);
      setSelectAll(false);
    } catch (error) {
      console.error('Failed to move items to cart:', error);
    }
  };



  const handleCartClick = async (gtin: string) => {
    if (isInCart(gtin)) {
      await removeFromCart(gtin);
    } else {
      await addToCart(gtin);
    }
  };

  const handleWishlistClick = async (gtin: string) => {
    if (isInWishlist(gtin)) {
      await removeFromWishlist(gtin);
    } else {
      await addToWishlist(gtin);
    }
  };

  // Nuts.com style product card
  const ProductCardNuts = ({ product }: { product: any }) => {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [failedImages, setFailedImages] = useState<Set<string>>(new Set());
    const [imageTimestamp, setImageTimestamp] = useState(Date.now());
    
    // Flatten image URLs
    let imageUrls: string[] = [];
    if (product.image_urls) {
      if (Array.isArray(product.image_urls.externalFileLink)) {
        imageUrls = imageUrls.concat(product.image_urls.externalFileLink.filter(Boolean));
      }
      if (Array.isArray(product.image_urls.dam)) {
        imageUrls = imageUrls.concat(product.image_urls.dam.filter(Boolean));
      }
    }
    
    // Pre-filter out known problematic URLs
    const preFilteredImages = imageUrls.filter(url => {
      if (url && url.includes('dam.catalog.1worldsync.com')) {
        return false;
      }
      return true;
    });

    // Ensure we have at least one image (fallback to original if all were filtered)
    const finalImages = preFilteredImages.length > 0 ? preFilteredImages : imageUrls;
    
    // Filter out failed images
    const workingImages = finalImages.filter(url => !failedImages.has(url));
    
    const displayName = product.normalized_name || product.name || product.title || 'N/A';

    // Carousel navigation functions
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
    


    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200 group">
        {/* Product Image */}
        <div className="relative h-48 bg-gray-50 rounded-t-lg overflow-hidden group">
          {workingImages && workingImages.length > 0 ? (
            <>
              <img
                src={`${workingImages[currentImageIndex]}?t=${imageTimestamp}`}
                alt={`${displayName} - Image ${currentImageIndex + 1}`}
                className="w-full h-full object-contain p-4"
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
          
          {/* Quick action buttons */}
          <div className="absolute top-2 right-2 flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelectedProduct(product);
              }}
              className="bg-white rounded-full p-1 shadow-sm hover:bg-gray-50"
              title="Quick view"
            >
              <Maximize2 className="w-4 h-4 text-gray-600" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleWishlistClick(product.gtin);
              }}
              className={`rounded-full p-1 shadow-sm ${
                isInWishlist(product.gtin) 
                  ? 'bg-red-500 text-white' 
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
              title={isInWishlist(product.gtin) ? 'Remove from wishlist' : 'Add to wishlist'}
            >
              <Heart className={`w-4 h-4 ${isInWishlist(product.gtin) ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-4">
          {/* Add to Cart Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCartClick(product.gtin);
            }}
            disabled={loading}
            className={`w-full mb-3 py-2 px-4 rounded-lg font-semibold text-sm transition-colors ${
              isInCart(product.gtin)
                ? 'bg-green-600 text-white'
                : 'bg-green-500 text-white hover:bg-green-600'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Adding...' : isInCart(product.gtin) ? 'In Cart' : 'Add to Cart'}
          </button>

          {/* Product Name */}
          <h3 
            className="font-semibold text-gray-900 mb-2 text-sm leading-tight cursor-pointer hover:text-blue-600"
            onClick={() => setSelectedProduct(product)}
          >
            {displayName}
          </h3>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavbarAfter />
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Top Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 gap-4">
          {/* Search Bar */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search for healthy products, ingredients, or nutrition info..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Results and Sort */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{total} results</span>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="popularity">Popularity</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="name">Name</option>
              </select>
            </div>
          </div>
        </div>

        {/* Mobile Filter Toggle */}
        <div className="lg:hidden mb-4">
          <button
            onClick={() => setShowMobileFilters(!showMobileFilters)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg bg-white"
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        <div className="flex gap-6">
          {/* Sidebar Filters */}
          <div className={`lg:block ${showMobileFilters ? 'block' : 'hidden'} w-64 flex-shrink-0`}>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-4">Filter By</h3>
              
              {/* Categories */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">CATEGORY</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                  {categories.map((category) => (
                    <label key={category} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(category)}
                        onChange={() => handleCategoryChange(category)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{category}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Guideline Filters */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">GUIDELINES</h4>
                <div className="space-y-2">
                  {guidelineOptions.map((guideline) => (
                    <label key={guideline} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedGuidelines.includes(guideline)}
                        onChange={() => handleGuidelineToggle(guideline)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{guideline}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Product Grid */}
          <div className="flex-1">
            {/* Bulk Actions */}
            {selectedItems.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={handleMoveToCart}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600"
                    >
                      Add to Cart
                    </button>
                    <button
                      onClick={handleMoveToWishlist}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600"
                    >
                      Add to Wishlist
                    </button>

                  </div>
                </div>
              </div>
            )}

            {/* Products */}
            {loadingProducts ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading products...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-red-500">{error}</p>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600">No products found.</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                  {products.map((product) => (
                    <ProductCardNuts key={product.gtin} product={product} />
                  ))}
                </div>

                {/* Pagination */}
                {total > limit && (
                  <div className="mt-8">
                    <Pagination
                      currentPage={page}
                      totalPages={Math.ceil(total / limit)}
                      onPageChange={setPage}
                      pageSize={limit}
                      onPageSizeChange={setLimit}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}


    </div>
  );
};

export default HomePageNuts; 