import NavbarAfter from '../components/navigation/NavbarAfter';
import { useState, useRef, useEffect } from 'react';
import { X, Filter, Pencil } from 'lucide-react';
import ProductCard from '../components/product/ProductCard';
import ProductTable from '../components/product/ProductTable';
import { List, LayoutGrid } from 'lucide-react';
import ProductDetailsModal from '../features/products/ProductDetailsModal';
import Pagination from '../components/ui/Pagination';
import HeroSection from '../components/home/HeroSection';
import MobileFilterDrawer from '../components/home/MobileFilterDrawer';
import ProductSearchBar from '../components/home/ProductSearchBar';
import ProductFilterBar from '../components/home/ProductFilterBar';
import ProductResults from '../components/home/ProductResults';

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
  'Charity Giving',
  'FDA',
  'Good Choice',
  'Smart Snack',
];

const DEFAULT_LIMIT = 12;

const HomePage = () => {
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
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
    setSelectedGuidelines((prev) =>
      prev.includes(guideline)
        ? prev.filter((g) => g !== guideline)
        : [...prev, guideline]
    );
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
        <div className="text-lg font-medium mb-4 mt-2">Search results</div>
        <ProductResults
          products={products}
          loading={loading}
          error={error}
          viewType={viewType}
          setSelectedProduct={setSelectedProduct}
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