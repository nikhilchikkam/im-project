import React, { useRef, useLayoutEffect, useState } from 'react';
import type { RefObject } from 'react';
import { X, Filter, Pencil, List, LayoutGrid } from 'lucide-react';
import GuidelineDropdownPortal from './GuidelineDropdownPortal';

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
  const guidelinePillRef = useRef<HTMLDivElement>(null);
  const [dropdownPos, setDropdownPos] = useState<{ left: number; top: number; width: number }>({ left: 0, top: 0, width: 0 });

  useLayoutEffect(() => {
    if (showGuidelineDropdown && guidelinePillRef.current) {
      const rect = guidelinePillRef.current.getBoundingClientRect();
      setDropdownPos({
        left: rect.left,
        top: rect.bottom + window.scrollY,
        width: rect.width,
      });
    }
  }, [showGuidelineDropdown]);

  return (
    <div className="w-full max-w-6xl bg-[#f7f7f7] rounded-2xl shadow sm:flex hidden flex-wrap items-center px-2 md:px-4 py-2 md:py-4 gap-2 md:gap-3 mb-6 md:mb-10 overflow-x-auto overflow-visible relative">
      {/* Guideline pill */}
      <div
        ref={guidelinePillRef}
        className={`flex items-center rounded-xl px-3 py-2 md:px-6 md:py-3 text-base md:text-lg font-medium mr-2 min-w-[180px] md:min-w-[220px] relative cursor-pointer
          ${selectedGuidelines.length > 0 ? 'bg-white border border-blue-400 text-black shadow' : 'bg-[#eaeaea] text-gray-400'}`}
        onClick={() => setShowGuidelineDropdown(!showGuidelineDropdown)}
      >
        <div className="flex flex-1 flex-wrap gap-2 items-center">
          {selectedGuidelines.length === 0 ? (
            <span className="flex-1">Select Guideline</span>
          ) : (
            selectedGuidelines.map((g) => (
              <span key={g} className="bg-white text-gray-700 rounded px-2 py-1 text-xs md:text-sm flex items-center gap-1">
                {g}
                <X className="w-4 h-4 cursor-pointer" onClick={e => { e.stopPropagation(); handleGuidelineToggle(g); }} />
              </span>
            ))
          )}
        </div>
        <X className="w-5 h-5 ml-2 cursor-pointer" onClick={e => { e.stopPropagation(); setSelectedGuidelines([]); }} />
      </div>
      {/* Guideline Dropdown Portal */}
      {showGuidelineDropdown && (
        <GuidelineDropdownPortal>
          <div
            ref={guidelineDropdownRef}
            className="bg-white border rounded-lg shadow-lg z-50 py-2 flex flex-col gap-2"
            style={{
              position: 'absolute',
              left: dropdownPos.left,
              top: dropdownPos.top,
              width: dropdownPos.width,
              minWidth: 220,
              maxWidth: 700,
            }}
          >
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
        </GuidelineDropdownPortal>
      )}
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
      {/* Category pill */}
      <div
        className={`flex items-center rounded-xl px-3 py-2 md:px-6 md:py-3 text-base md:text-lg font-medium mr-2 min-w-[180px] md:min-w-[220px]
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
      <div className="hidden md:block h-8 w-px bg-gray-300 mx-2" />
      {/* Filters button */}
      <button
        className="flex items-center gap-2 text-gray-500 font-medium px-4 py-2 rounded-lg hover:bg-gray-200 transition"
        onClick={() => setShowFilters(true)}
        type="button"
      >
        <Filter className="w-5 h-5" /> Filters
      </button>
      {/* View type toggle */}
      <div className="flex items-center gap-2 ml-0 md:ml-4">
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