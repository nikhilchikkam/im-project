import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import NutritionFactsCard from './NutritionFactsCard';
import NutritionSummaryCard from './NutritionSummaryCard';
import ProductHeader from './ProductHeader';
import ProductDescription from './ProductDescription';
import ProductTagsSection from './ProductTagsSection';

const dummyBadges = ['Meat', 'Gluten', 'Organic'];
const kosherTags = ['Vegan tag', 'Vegan tag', 'Vegan tag'];
const halalTags = ['Vegan tag', 'Vegan tag', 'Vegan tag'];

type NutritionData = {
  serving_info: any;
  nutrients: any[];
};

type ProductDetailsModalProps = {
  product: any;
  onClose: () => void;
};

const mapNutritionFacts = (nutritionArr: any[]) => {
  // Map the API nutrition array to the NutritionFactsCard prop shape
  const nf: any = {
    calories: 0,
    servingSize: '',
    servingsPerContainer: 0,
    totalFat: 0,
    saturatedFat: 0,
    transFat: 0,
    cholesterol: 0,
    sodium: 0,
    totalCarb: 0,
    dietaryFiber: 0,
    sugars: 0,
    protein: 0,
    vitaminD: 0,
    calcium: 0,
    potassium: 0,
    iron: 0,
  };
  nutritionArr.forEach(n => {
    const label = (n.nutrient_label || '').toLowerCase();
    switch (label) {
      case 'calories': nf.calories = n.value; break;
      case 'total_fat': nf.totalFat = n.value; break;
      case 'saturated_fat': nf.saturatedFat = n.value; break;
      case 'trans_fat': nf.transFat = n.value; break;
      case 'cholesterol': nf.cholesterol = n.value; break;
      case 'sodium': nf.sodium = n.value; break;
      case 'total_carbohydrate': nf.totalCarb = n.value; break;
      case 'dietary_fiber': nf.dietaryFiber = n.value; break;
      case 'sugars': nf.sugars = n.value; break;
      case 'protein': nf.protein = n.value; break;
      case 'vitamin_d': nf.vitaminD = n.value; break;
      case 'calcium': nf.calcium = n.value; break;
      case 'potassium': nf.potassium = n.value; break;
      case 'iron': nf.iron = n.value; break;
      default: break;
    }
  });
  return nf;
};

const mapNutritionSummary = (nutritionArr: any[]) => {
  // Map the API nutrition array to the NutritionSummaryCard prop shape
  let summary: any = { calories: 0, fat: 0, sodium: 0, protein: 0 };
  nutritionArr.forEach(n => {
    const label = (n.nutrient_label || '').toLowerCase();
    switch (label) {
      case 'calories': summary.calories = n.value; break;
      case 'total_fat': summary.fat = n.value; break;
      case 'sodium': summary.sodium = n.value; break;
      case 'protein': summary.protein = n.value; break;
      default: break;
    }
  });
  return summary;
};

const ProductDetailsModal = ({ product, onClose }: ProductDetailsModalProps) => {
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!product?.gtin) return;
    setLoading(true);
    setError(null);
    const apiUrl = import.meta.env.VITE_API_URL || '';
    fetch(`${apiUrl}/api/nutrition/${product.gtin}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch nutrition');
        return res.json();
      })
      .then(data => setNutritionData(data))
      .catch(e => setError(e.message || 'Unknown error'))
      .finally(() => setLoading(false));
  }, [product?.gtin]);

  const nutritionFacts = nutritionData ? mapNutritionFacts(nutritionData.nutrients) : {};
  const nutritionSummary = nutritionData ? mapNutritionSummary(nutritionData.nutrients) : {};
  const servingInfo = nutritionData ? nutritionData.serving_info : null;

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
        {/* Product header and description */}
        <div className="mb-6">
          <div className="flex flex-col md:flex-row gap-8">
            <div className="flex-1">
              <ProductHeader product={{
                upc: product.gtin,
                title: product.name || product.title,
                badges: dummyBadges,
              }} />
            </div>
            <div className="flex-1">
              <ProductDescription description={product.description} />
            </div>
          </div>
          <div className="flex flex-col md:flex-row gap-4 mt-4">
            <ProductTagsSection title="Kosher" tags={kosherTags} />
            <ProductTagsSection title="Halal" tags={halalTags} />
          </div>
        </div>
        {/* Nutrition and summary */}
        <div className="flex flex-col md:flex-row gap-8">
          {/* Left: Nutrition Facts */}
          <div className="flex-shrink-0">
            {loading ? (
              <div>Loading nutrition...</div>
            ) : error ? (
              <div className="text-red-500">{error}</div>
            ) : (
              <NutritionFactsCard
                nutrients={nutritionData ? nutritionData.nutrients : []}
                servingInfo={servingInfo}
              />
            )}
          </div>
          {/* Right: Summary and details */}
          <div className="flex-1 flex flex-col gap-4">
            {loading ? (
              <div>Loading summary...</div>
            ) : error ? (
              <div className="text-red-500">{error}</div>
            ) : (
              <NutritionSummaryCard summary={nutritionSummary} />
            )}
            <div className="bg-gray-50 rounded-lg p-4 min-h-[120px]">Other product details go here...</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailsModal; 