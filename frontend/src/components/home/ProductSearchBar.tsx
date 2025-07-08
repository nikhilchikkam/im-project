import React from 'react';
import { X, Filter, List, LayoutGrid } from 'lucide-react';

interface ProductSearchBarProps {
  searchInput: string;
  setSearchInput: (val: string) => void;
  viewType: 'card' | 'list';
  setViewType: (val: 'card' | 'list') => void;
  setShowMobileFilter: (open: boolean) => void;
}

const ProductSearchBar: React.FC<ProductSearchBarProps> = ({
  searchInput,
  setSearchInput,
  viewType,
  setViewType,
  setShowMobileFilter,
}) => (
  <div className="w-full max-w-6xl flex sm:hidden items-center px-2 py-2 gap-2 mb-6 overflow-x-auto">
    <form className="flex-1 flex items-center rounded-xl px-3 py-2 bg-[#eaeaea] text-base font-medium">
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
    {/* Filter icon (opens modal/drawer) */}
    <button
      className="flex items-center justify-center bg-white border border-gray-300 rounded-xl p-2 text-gray-500 hover:bg-gray-100 transition"
      onClick={() => setShowMobileFilter(true)}
      type="button"
      aria-label="Open filters"
    >
      <Filter className="w-6 h-6" />
    </button>
    {/* View type toggle */}
    <div className="flex items-center gap-1 ml-0">
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
);

export default ProductSearchBar; 