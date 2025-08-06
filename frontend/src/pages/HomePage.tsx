import NavbarAfter from '../components/navigation/NavbarAfter';
import { useState, useRef, useEffect } from 'react';
import ProductDetailsModal from '../features/products/ProductDetailsModal';
import Pagination from '../components/ui/Pagination';
import HeroSection from '../components/home/HeroSection';
import MobileFilterDrawer from '../components/home/MobileFilterDrawer';
import ProductSearchBar from '../components/home/ProductSearchBar';
import ProductFilterBar from '../components/home/ProductFilterBar';
import ProductResults from '../components/home/ProductResults';
import { useCartWishlist } from '../contexts/CartWishlistContext';
import { useAuth, useAuthenticatedFetch } from '../contexts/AuthContext';
import { FolderPlus } from 'lucide-react';



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

const guidelineOptions = [
  'Good Choice',
  'Smart Snack',
  'Philly',
];

const DEFAULT_LIMIT = 12;

const HomePage = () => {
  const { addToWishlist, addToCart } = useCartWishlist();
  const { authenticatedFetch } = useAuthenticatedFetch();
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(categories.slice());
  const [viewType, setViewType] = useState<'card' | 'list'>('card');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [showGuidelineDropdown, setShowGuidelineDropdown] = useState(false);
  const [selectedGuidelines, setSelectedGuidelines] = useState<string[]>([]);
  const guidelineDropdownRef = useRef<HTMLDivElement>(null);
  const [total, setTotal] = useState(0);
  const [showMobileFilter, setShowMobileFilter] = useState(false);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  // Debug selectedItems state changes
  useEffect(() => {
    console.log('HomePage selectedItems state changed:', selectedItems);
  }, [selectedItems]);



  const apiUrl = import.meta.env.VITE_API_URL || '';

  // Fetch products from API
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
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
        setLoading(false);
      }
    };
    fetchProducts();
  }, [selectedCategories, searchTerm, page, limit, apiUrl, selectedGuidelines]);

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setSearchTerm(searchInput);
      setPage(1); // Optionally reset to first page on new search
    }, 400);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const handleCategoryChange = (cat: string) => {
    if (cat === 'All Categories') {
      if (selectedCategories.includes('All Categories')) {
        // Uncheck all
        setSelectedCategories([]);
      } else {
        // Check all
        setSelectedCategories(categories.slice());
      }
    } else {
      let newSelected;
      if (selectedCategories.includes(cat)) {
        // Remove this category
        newSelected = selectedCategories.filter((c) => c !== cat && c !== 'All Categories');
      } else {
        // Add this category
        newSelected = [...selectedCategories.filter((c) => c !== 'All Categories'), cat];
        // If all categories (except 'All Categories') are now selected, add 'All Categories'
        if (newSelected.length === categories.length - 1) {
          newSelected = categories.slice();
        }
      }
      setSelectedCategories(newSelected);
    }
    setPage(1);
  };

  const handleLimitChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLimit(Number(e.target.value));
    setPage(1);
  };

  // Close dropdown on click outside
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Add click outside handler for guideline dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        guidelineDropdownRef.current &&
        !guidelineDropdownRef.current.contains(event.target as Node)
      ) {
        setShowGuidelineDropdown(false);
      }
    }
    if (showGuidelineDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showGuidelineDropdown]);

  const handleGuidelineToggle = (guideline: string) => {
    setSelectedGuidelines(prev => 
      prev.includes(guideline) 
        ? prev.filter(g => g !== guideline)
        : [...prev, guideline]
    );
    setPage(1);
  };

  // Selection handlers
  const handleItemSelect = (gtin: string) => {
    setSelectedItems(prev => {
      const newSelection = prev.includes(gtin) 
        ? prev.filter(item => item !== gtin)
        : [...prev, gtin];
      return newSelection;
    });
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]);
      setSelectAll(false);
    } else {
      const allGtins = products.map(p => p.gtin);
      setSelectedItems(allGtins);
      setSelectAll(true);
    }
  };

  // Bulk action handlers
  const handleCompare = () => {
    if (selectedItems.length > 4) {
      alert('You can only compare up to 4 items at a time');
      return;
    }
    // TODO: Implement comparison functionality
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



  // Calculate totalPages
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      <HeroSection />
      {/* Filter/Search Bar */}
      <div className="w-full flex flex-col items-center">
          {/* Mobile: Only show search, filter icon, and view icons */}
          <ProductSearchBar
            searchInput={searchInput}
            setSearchInput={setSearchInput}
            viewType={viewType}
            setViewType={setViewType}
            setShowMobileFilter={setShowMobileFilter}
          />
          {/* Desktop: Full filter/search bar */}
          <ProductFilterBar
            searchInput={searchInput}
            setSearchInput={setSearchInput}
            selectedGuidelines={selectedGuidelines}
            setSelectedGuidelines={setSelectedGuidelines}
            selectedCategories={selectedCategories}
            setSelectedCategories={setSelectedCategories}
            guidelineOptions={guidelineOptions}
            categories={categories}
            showGuidelineDropdown={showGuidelineDropdown}
            setShowGuidelineDropdown={setShowGuidelineDropdown}
            handleGuidelineToggle={handleGuidelineToggle}
            handleCategoryChange={handleCategoryChange}
            guidelineDropdownRef={guidelineDropdownRef}
            viewType={viewType}
            setViewType={setViewType}
            setShowFilters={setShowFilters}
          />
          {/* Filters Dropdown and Backdrop */}
          {showFilters && (
            <>
              {/* Backdrop to close dropdown on click */}
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowFilters(false)}
                aria-label="Close filters dropdown"
              />
              <div
                ref={dropdownRef}
                className="absolute z-20 mt-2 bg-white border rounded-lg shadow-lg p-4 md:p-6 flex flex-col md:flex-row gap-4 md:gap-8 w-[95vw] max-w-lg md:w-[700px] max-w-full"
                style={{ top: '340px' }}
              >
                <div className="flex flex-col gap-2 max-h-96 overflow-y-auto w-full">
                  {categories.map((cat) => (
                    <label key={cat} className="flex items-center gap-2 text-base">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(cat) || (cat !== 'All Categories' && selectedCategories.includes('All Categories'))}
                        onChange={() => handleCategoryChange(cat)}
                      />
                      {cat}
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      {/* Results Section */}
      <section className="max-w-6xl mx-auto px-4 pb-12">
        <div className="text-lg font-medium mb-4 mt-2">
          Search results for: {searchTerm || 'All Products'}
        </div>
        
        {/* Selection and Bulk Actions Bar */}
        {selectedItems.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 bg-white px-3 py-2 rounded-md border">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={handleSelectAll}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    {selectedItems.length} items selected
                  </span>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Compare items (max 4):</span>
                  <button
                    onClick={handleCompare}
                    disabled={selectedItems.length > 4}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    <span>Compare</span>
                  </button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Move items to:</span>
                  <button
                    onClick={handleMoveToWishlist}
                    className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 flex items-center space-x-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </button>
                  <button
                    onClick={handleMoveToCart}
                    className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 flex items-center space-x-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                    </svg>
                  </button>

                </div>
              </div>
            </div>
          </div>
        )}
        
        <ProductResults
          products={products}
          loading={loading}
          error={error}
          viewType={viewType}
          setSelectedProduct={setSelectedProduct}
          selectedItems={selectedItems}
          onItemSelect={handleItemSelect}
          selectAll={selectAll}
          onSelectAll={handleSelectAll}
        />
        {/* Pagination */}
        <div className="flex justify-center w-full mt-8">
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
            pageSize={limit}
            onPageSizeChange={setLimit}
          />
        </div>
      </section>
      {/* Product Details Modal */}
      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
      {/* Mobile Filter Drawer/Modal */}
      <MobileFilterDrawer
        open={showMobileFilter}
        onClose={() => setShowMobileFilter(false)}
        guidelineOptions={guidelineOptions}
        categories={categories}
        selectedGuidelines={selectedGuidelines}
        selectedCategories={selectedCategories}
        handleGuidelineToggle={handleGuidelineToggle}
        handleCategoryChange={handleCategoryChange}
      />


    </div>
  );
};

export default HomePage; 