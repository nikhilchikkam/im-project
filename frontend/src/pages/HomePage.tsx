import NavbarAfter from '../components/NavbarAfter';
import { useState, useRef } from 'react';
import { X, Filter } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import ProductTable from '../components/ProductTable';
import { List, LayoutGrid } from 'lucide-react';
import ProductDetailsModal from '../features/products/ProductDetailsModal';

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

const mockProducts = Array.from({ length: 6 }).map((_, i) => ({
  id: `${i}`,
  upc: '070038365266',
  title: 'Chex Mix Savory Snack Mix Traditional',
  category: i % 2 === 0 ? 'Produce' : 'Meat',
  description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
  itemNumber: '9090909090',
  name: 'Chex Mix',
}));

const HomePage = () => {
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [viewType, setViewType] = useState<'card' | 'list'>('card');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);

  const handleCategoryChange = (cat: string) => {
    setSelectedCategories((prev) =>
      prev.includes(cat)
        ? prev.filter((c) => c !== cat)
        : [...prev, cat]
    );
  };

  // Close dropdown on click outside
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Modular renderers
  const renderResults = () => {
    if (viewType === 'card') {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
          {mockProducts.map((p) => (
            <ProductCard
              key={p.id}
              upc={p.upc}
              title={p.title}
              category={p.category}
              description={p.description}
              onEnlarge={() => setSelectedProduct(p)}
            />
          ))}
        </div>
      );
    }
    return (
      <div className="mt-4">
        <ProductTable products={mockProducts.map(p => ({
          id: p.id,
          category: p.category,
          itemNumber: p.itemNumber,
          name: p.name,
          description: p.description,
        }))} />
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center pt-12 pb-8">
        <div className="flex items-center justify-center gap-8 mb-8">
          {/* Left image */}
          <img
            src="https://i.imgur.com/4QfKuz1.png" // Placeholder Coco Pops
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
            src="https://i.imgur.com/4QfKuz1.png" // Placeholder Ginger Beer
            alt="Ginger Beer"
            className="w-40 h-48 object-contain rotate-15"
            style={{ transform: 'rotate(15deg)' }}
          />
        </div>
        {/* Filter/Search Bar */}
        <div className="w-full flex flex-col items-center">
          <div className="w-[90%] max-w-6xl bg-[#f7f7f7] rounded-2xl shadow flex items-center px-4 py-4 gap-3 mb-10">
            {/* Guideline pill */}
            <div className="flex items-center bg-[#eaeaea] rounded-xl px-6 py-3 text-lg text-gray-400 font-medium mr-2 min-w-[220px]">
              <span className="flex-1">Select Guideline</span>
              <X className="w-5 h-5 ml-2 cursor-pointer" />
            </div>
            {/* Product Keywords pill */}
            <div className="flex items-center bg-[#eaeaea] rounded-xl px-6 py-3 text-lg text-gray-400 font-medium mr-2 min-w-[220px]">
              <span className="flex-1">Product Keywords</span>
              <X className="w-5 h-5 ml-2 cursor-pointer" />
            </div>
            {/* Category pill */}
            <div className="flex items-center bg-[#eaeaea] rounded-xl px-6 py-3 text-lg text-gray-400 font-medium mr-2 min-w-[220px]">
              <span className="flex-1">Select Category</span>
              <X className="w-5 h-5 ml-2 cursor-pointer" />
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
                        checked={selectedCategories.includes(cat)}
                        onChange={() => handleCategoryChange(cat)}
                      />
                      {cat}
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
          {/* Search Button */}
          <button className="w-[500px] max-w-full bg-[#007aff] text-white py-4 rounded-xl text-lg font-semibold shadow hover:bg-blue-700 transition">
            Search selection
          </button>
        </div>
      </section>
      {/* Results Section */}
      <section className="max-w-6xl mx-auto px-4 pb-12">
        <div className="text-lg font-medium mb-4 mt-2">Search results for: Chex Mex</div>
        {renderResults()}
        {/* Pagination */}
        <div className="flex items-center justify-between mt-8 text-gray-500 text-sm">
          <div>
            <button className="px-2 py-1 rounded hover:bg-gray-100">&lt; Previous</button>
            <span className="mx-2 font-semibold text-black">1</span>
            <button className="px-2 py-1 rounded hover:bg-gray-100">2</button>
            <button className="px-2 py-1 rounded hover:bg-gray-100">3</button>
            <button className="px-2 py-1 rounded hover:bg-gray-100">4</button>
            <button className="px-2 py-1 rounded hover:bg-gray-100">5</button>
            <span className="mx-2">...</span>
            <button className="px-2 py-1 rounded hover:bg-gray-100">Next &gt;</button>
          </div>
          <div>
            Products per Page
            <select className="ml-2 border rounded px-2 py-1">
              <option>49</option>
              <option>24</option>
              <option>12</option>
            </select>
          </div>
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