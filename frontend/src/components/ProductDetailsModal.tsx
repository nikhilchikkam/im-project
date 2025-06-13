import React from 'react';
import { X } from 'lucide-react';
import NutritionFactsCard from './NutritionFactsCard';
import NutritionSummaryCard from './NutritionSummaryCard';

const nutritionFacts = {
  calories: 260,
  servingSize: '1 cup (228g)',
  servingsPerContainer: 2,
  totalFat: 13,
  saturatedFat: 5,
  transFat: 5,
  cholesterol: 30,
  sodium: 660,
  totalCarb: 31,
  dietaryFiber: 0,
  sugars: 5,
  protein: 5,
  vitaminD: 2,
  calcium: 2260,
  potassium: 240,
  iron: 8,
};

const nutritionSummary = {
  calories: 417,
  fat: 10.3,
  sodium: 707,
  protein: 8.74,
};

type ProductDetailsModalProps = {
  product: any;
  onClose: () => void;
};

const ProductDetailsModal = ({ product, onClose }: ProductDetailsModalProps) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="bg-white rounded-xl shadow-xl p-8 max-w-5xl w-full relative overflow-y-auto max-h-[90vh]">
        <button
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-700"
          onClick={onClose}
          aria-label="Close"
        >
          <X className="w-6 h-6" />
        </button>
        {/* Product details content */}
        <div className="flex flex-col md:flex-row gap-8">
          {/* Left: Nutrition Facts */}
          <div className="flex-shrink-0">
            <NutritionFactsCard nutritionFacts={nutritionFacts} />
          </div>
          {/* Right: Summary and details */}
          <div className="flex-1 flex flex-col gap-4">
            <NutritionSummaryCard summary={nutritionSummary} />
            <div className="bg-gray-50 rounded-lg p-4 min-h-[120px]">Other product details go here...</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailsModal; 