import React, { useRef, useLayoutEffect, useState } from 'react';
import type { RefObject } from 'react';
import { X, Pencil, List, LayoutGrid } from 'lucide-react';
import GuidelineDropdownPortal from './GuidelineDropdownPortal';
import Dropdown from '../ui/Dropdown.tsx';

interface ProductFilterBarProps {
  searchInput: string;
  setSearchInput: (val: string) => void;
  selectedGuidelines: string[];
  setSelectedGuidelines: (val: string[]) => void;
  selectedCategories: string[];
  setSelectedCategories: (val: string[]) => void;
  guidelineOptions: string[];
  categories: string[];
  showGuidelineDropdown: boolean;
  setShowGuidelineDropdown: (open: boolean) => void;
  handleGuidelineToggle: (guideline: string) => void;
  handleCategoryChange: (cat: string) => void;
  guidelineDropdownRef: RefObject<HTMLDivElement | null>;
  viewType: 'card' | 'list';
  setViewType: (val: 'card' | 'list') => void;
  setShowFilters: (open: boolean) => void;
}

const ProductFilterBar: React.FC<ProductFilterBarProps> = ({
  searchInput,
  setSearchInput,
  selectedGuidelines,
  setSelectedGuidelines,
  selectedCategories,
  setSelectedCategories,
  guidelineOptions,
  categories,
  showGuidelineDropdown,
  setShowGuidelineDropdown,
  handleGuidelineToggle,
  handleCategoryChange,
  guidelineDropdownRef,
  viewType,
  setViewType,
  setShowFilters,
}) => {
  const [hasUserChangedCategories, setHasUserChangedCategories] = useState(false);



  return (
    <div className="w-full max-w-6xl bg-[#f7f7f7] rounded-2xl shadow sm:flex hidden flex-wrap items-center px-2 md:px-4 py-2 md:py-4 gap-2 md:gap-3 mb-6 md:mb-10 overflow-x-auto overflow-visible">
      {/* Guideline Dropdown */}
      <Dropdown
        options={guidelineOptions.map(option => ({ value: option, label: option }))}
        selectedValues={selectedGuidelines}
        onSelectionChange={handleGuidelineToggle}
        placeholder="Select Guideline"
        multiple={true}
        className="mr-2"
      />
      
      {/* Product Keywords pill */}
      <form
        className={`flex items-center rounded-xl px-3 py-2 md:px-6 md:py-3 text-base md:text-lg font-medium mr-2 min-w-[180px] md:min-w-[220px]
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
      
      {/* Category Dropdown */}
      <Dropdown
        options={categories.map(category => ({ value: category, label: category }))}
        selectedValues={selectedCategories}
        onSelectionChange={(value) => {
          setHasUserChangedCategories(true);
          handleCategoryChange(value);
        }}
        placeholder="All Categories"
        multiple={true}
        className="mr-2 min-w-[280px] md:min-w-[320px] flex-1"
        dropdownWidth={450}
        showCount={hasUserChangedCategories}
      />
      
      {/* View type toggle - moved to corner */}
      <div className="flex items-center gap-2 ml-auto">
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
};

export default ProductFilterBar; 