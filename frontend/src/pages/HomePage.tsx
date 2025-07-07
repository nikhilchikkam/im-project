import NavbarAfter from '../components/navigation/NavbarAfter';
import { useState, useRef, useEffect } from 'react';
import { X, Filter, Pencil } from 'lucide-react';
import ProductCard from '../components/product/ProductCard';
import ProductTable from '../components/product/ProductTable';
import { List, LayoutGrid } from 'lucide-react';
import ProductDetailsModal from '../features/products/ProductDetailsModal';
import Pagination from '../components/ui/Pagination';

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

  // Modular renderers
  const renderResults = () => {
    if (loading) return <div className="text-center py-8">Loading...</div>;
    if (error) return <div className="text-center text-red-500 py-8">{error}</div>;
    if (products.length === 0) return <div className="text-center py-8">No products found.</div>;
    if (viewType === 'card') {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
          {products.map((p) => (
            <ProductCard
              key={p.gtin}
              upc={p.gtin}
              title={p.name || p.title}
              category={p.family_title || ''}
              description={p.description}
              isSmartSnack={p.is_smart_snack}
              novaLabel={p.nova_label}
              isGoodChoice={p.is_good_choice}
              onEnlarge={() => setSelectedProduct(p)}
            />
          ))}
        </div>
      );
    }
    return (
      <div className="mt-4">
        <ProductTable products={products.map(p => ({
          id: p.gtin,
          category: p.family_title || '',
          itemNumber: p.gtin,
          name: p.name || p.title,
          description: p.description,
        }))} />
      </div>
    );
  };

  // Calculate totalPages
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center pt-12 pb-8">
        <div className="flex items-center justify-center gap-8 mb-8">
          {/* Left image */}
          <img
            src="https://i.imgur.com/4QfKuz1.png"
            alt="Coco Pops"
            className="w-48 h-48 object-contain -rotate-15"
            style={{ transform: 'rotate(-15deg)' }}
          />
          {/* Headline */}
          <h1 className="text-5xl font-bold text-center max-w-2xl">
            Discover best quality<br />food products that fit<br />your palette
          </h1>
          {/* Right image */}
          <img
            src="https://i.imgur.com/4QfKuz1.png"
            alt="Ginger Beer"
            className="w-40 h-48 object-contain rotate-15"
            style={{ transform: 'rotate(15deg)' }}
          />
        </div>
        {/* Filter/Search Bar */}
        <div className="w-full flex flex-col items-center">
          <div className="w-[90%] max-w-6xl bg-[#f7f7f7] rounded-2xl shadow flex items-center px-4 py-4 gap-3 mb-10">
            {/* Guideline pill */}
            <div
              className={`flex items-center rounded-xl px-6 py-3 text-lg font-medium mr-2 min-w-[220px] relative cursor-pointer
                ${selectedGuidelines.length > 0 ? 'bg-white border border-blue-400 text-black shadow' : 'bg-[#eaeaea] text-gray-400'}`}
              onClick={() => setShowGuidelineDropdown((v) => !v)}
            >
              <div className="flex flex-1 flex-wrap gap-2 items-center">
                {selectedGuidelines.length === 0 ? (
                  <span className="flex-1">Select Guideline</span>
                ) : (
                  selectedGuidelines.map((g) => (
                    <span key={g} className="bg-white text-gray-700 rounded px-2 py-1 text-sm flex items-center gap-1">
                      {g}
                      <X className="w-4 h-4 cursor-pointer" onClick={e => { e.stopPropagation(); handleGuidelineToggle(g); }} />
                    </span>
                  ))
                )}
              </div>
              <X className="w-5 h-5 ml-2 cursor-pointer" onClick={e => { e.stopPropagation(); setSelectedGuidelines([]); }} />
              {/* Dropdown */}
              {showGuidelineDropdown && (
                <div ref={guidelineDropdownRef} className="absolute left-0 top-full mt-2 bg-white border rounded-lg shadow-lg z-30 min-w-[220px] py-2">
                  {guidelineOptions.map((option) => (
                    <div key={option} className="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer gap-2"
                         onClick={e => { e.stopPropagation(); handleGuidelineToggle(option); }}>
                      <input
                        type="checkbox"
                        checked={selectedGuidelines.includes(option)}
                        readOnly
                        className="mr-2"
                      />
                      <span className="flex-1 text-gray-700">{option}</span>
                      <Pencil className="w-4 h-4 text-gray-400 ml-2" />
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Product Keywords pill */}
            <form
              className={`flex items-center rounded-xl px-6 py-3 text-lg font-medium mr-2 min-w-[220px]
                ${searchInput ? 'bg-white border border-blue-400 text-black shadow' : 'bg-[#eaeaea] text-gray-400'}`}
            >
              <input
                type="text"
                placeholder="Product Keywords"
                className="bg-transparent outline-none flex-1 text-black"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
              />
              {searchInput && (
                <X className="w-5 h-5 ml-2 cursor-pointer" onClick={() => setSearchInput('')} />
              )}
            </form>
            {/* Category pill */}
            <div
              className={`flex items-center rounded-xl px-6 py-3 text-lg font-medium mr-2 min-w-[220px]
                ${selectedCategories.length > 0 && !selectedCategories.includes('All Categories') ? 'bg-white border border-blue-400 text-black shadow' : 'bg-[#eaeaea] text-gray-400'}`}
            >
              <span className="flex-1">
                {selectedCategories.includes('All Categories') || selectedCategories.length === 0
                  ? 'All Categories'
                  : selectedCategories.length === 1
                    ? selectedCategories[0]
                    : `${selectedCategories.length} filters applied`}
              </span>
              <X className="w-5 h-5 ml-2 cursor-pointer" onClick={() => setSelectedCategories([])} />
            </div>
            {/* Divider */}
            <div className="h-8 w-px bg-gray-300 mx-2" />
            {/* Filters button */}
            <button
              className="flex items-center gap-2 text-gray-500 font-medium px-4 py-2 rounded-lg hover:bg-gray-200 transition"
              onClick={() => setShowFilters((v) => !v)}
              type="button"
            >
              <Filter className="w-5 h-5" /> Filters
            </button>
            {/* View type toggle */}
            <div className="flex items-center gap-2 ml-4">
              <button
                className={`p-2 rounded-lg ${viewType === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:bg-gray-200'}`}
                onClick={() => setViewType('list')}
                aria-label="List view"
              >
                <List className="w-6 h-6" />
              </button>
              <button
                className={`p-2 rounded-lg ${viewType === 'card' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:bg-gray-200'}`}
                onClick={() => setViewType('card')}
                aria-label="Card view"
              >
                <LayoutGrid className="w-6 h-6" />
              </button>
            </div>
          </div>
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
                className="absolute z-20 mt-2 bg-white border rounded-lg shadow-lg p-6 flex gap-8 w-[700px] max-w-full"
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
      </section>
      {/* Results Section */}
      <section className="max-w-6xl mx-auto px-4 pb-12">
        <div className="text-lg font-medium mb-4 mt-2">Search results</div>
        {renderResults()}
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
    </div>
  );
};

export default HomePage; 