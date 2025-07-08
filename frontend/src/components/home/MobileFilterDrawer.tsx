import React from 'react';
import { X } from 'lucide-react';

interface MobileFilterDrawerProps {
  open: boolean;
  onClose: () => void;
  guidelineOptions: string[];
  categories: string[];
  selectedGuidelines: string[];
  selectedCategories: string[];
  handleGuidelineToggle: (guideline: string) => void;
  handleCategoryChange: (cat: string) => void;
}

const MobileFilterDrawer: React.FC<MobileFilterDrawerProps> = ({
  open,
  onClose,
  guidelineOptions,
  categories,
  selectedGuidelines,
  selectedCategories,
  handleGuidelineToggle,
  handleCategoryChange,
}) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:hidden">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-30" onClick={onClose} />
      {/* Drawer */}
      <div className="relative w-full bg-white rounded-t-2xl shadow-xl p-6 max-h-[90vh] overflow-y-auto animate-slideInUp">
        {/* Close button */}
        <button
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-700"
          onClick={onClose}
          aria-label="Close filter drawer"
        >
          <X className="w-7 h-7" />
        </button>
        <h2 className="text-xl font-bold mb-4">Filters</h2>
        {/* Guidelines */}
        <div className="mb-6">
          <div className="font-semibold mb-2">Guidelines</div>
          <div className="flex flex-wrap gap-2">
            {guidelineOptions.map((option) => (
              <label key={option} className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 cursor-pointer text-base">
                <input
                  type="checkbox"
                  checked={selectedGuidelines.includes(option)}
                  onChange={() => handleGuidelineToggle(option)}
                  className="accent-blue-600"
                />
                {option}
              </label>
            ))}
          </div>
        </div>
        {/* Categories */}
        <div className="mb-6">
          <div className="font-semibold mb-2">Categories</div>
          <div className="flex flex-col gap-2 max-h-48 overflow-y-auto">
            {categories.map((cat) => (
              <label key={cat} className="flex items-center gap-2 text-base">
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(cat) || (cat !== 'All Categories' && selectedCategories.includes('All Categories'))}
                  onChange={() => handleCategoryChange(cat)}
                  className="accent-blue-600"
                />
                {cat}
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileFilterDrawer; 