import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import NutritionFactsCard from './NutritionFactsCard';
import NutritionSummaryCard from './NutritionSummaryCard';
import ProductHeader from './ProductHeader';
import ProductDescription from './ProductDescription';
import ProductTagsSection from './ProductTagsSection';
import ProductDetailsLayout from '../../layouts/ProductDetailsLayout';

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
  const [allergens, setAllergens] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [productDetails, setProductDetails] = useState<any | null>(null);

  useEffect(() => {
    if (!product?.gtin) return;
    setLoading(true);
    setError(null);
    const apiUrl = import.meta.env.VITE_API_URL || '';
    // Fetch full product details
    fetch(`${apiUrl}/api/products/${product.gtin}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch product details');
        return res.json();
      })
      .then(data => setProductDetails(data))
      .catch(() => setProductDetails(null));
    // Fetch nutrition
    fetch(`${apiUrl}/api/nutrition/${product.gtin}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch nutrition');
        return res.json();
      })
      .then(data => setNutritionData(data))
      .catch(e => setError(e.message || 'Unknown error'))
      .finally(() => setLoading(false));
    // Fetch allergens
    fetch(`${apiUrl}/api/allergens/${product.gtin}`)
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (Array.isArray(data)) {
          setAllergens(data.map(a => a.allergentypename).filter(Boolean));
        } else {
          setAllergens([]);
        }
      })
      .catch(() => setAllergens([]));
  }, [product?.gtin]);

  const details = productDetails || product;
  const nutritionFacts = nutritionData ? mapNutritionFacts(nutritionData.nutrients) : {};
  const nutritionSummary = nutritionData ? mapNutritionSummary(nutritionData.nutrients) : {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="bg-white rounded-xl shadow-xl p-4 sm:p-6 md:p-8 w-full max-w-full sm:max-w-2xl md:max-w-4xl lg:max-w-5xl relative overflow-y-auto max-h-[95vh] mx-2 sm:mx-4">
        <button
          className="absolute top-2 right-2 sm:top-4 sm:right-4 text-gray-400 hover:text-gray-700 z-10"
          onClick={onClose}
          aria-label="Close"
        >
          <X className="w-6 h-6" />
        </button>
        <ProductDetailsLayout
          headerBlock={
            <>
              <div className="text-xs text-gray-500 mb-1">UPC/GTIN: {details.gtin}</div>
              <div className="font-bold text-2xl mb-2">{details.normalized_name?.trim() ? details.normalized_name : (details.name?.trim() ? details.name : (details.title?.trim() ? details.title : 'N/A'))}</div>
              <div className="flex gap-2 mb-2">{dummyBadges.map(b => <span key={b} className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-semibold">{b}</span>)}</div>
              <div className="flex gap-2 mb-2">
                <button className="bg-blue-100 text-blue-700 px-4 py-2 rounded font-semibold">Wishlist</button>
                <button className="bg-blue-600 text-white px-4 py-2 rounded font-semibold">Cart</button>
              </div>
            </>
          }
          descriptionBlock={
            <>
              <div className="font-semibold text-base mb-1">Product Description</div>
              <div className="text-sm text-gray-700 mb-4"><ProductDescription description={details.description} /></div>
            </>
          }
          ingredientsBlock={
            details.ingredients ? (
              <div>
                <div className="font-semibold text-base mb-1">Ingredients</div>
                <div className="text-sm text-gray-700 whitespace-pre-line">{details.ingredients}</div>
              </div>
            ) : null
          }
          halalKosherBlock={
            <>
              <ProductTagsSection title="Halal" tags={halalTags} />
              <ProductTagsSection title="Kosher" tags={kosherTags} />
            </>
          }
          allergensBlock={
            allergens.length > 0 ? (
              <div className="bg-gray-50 rounded-lg p-2 sm:p-4">
                <ProductTagsSection title="Allergens" tags={allergens} />
              </div>
            ) : null
          }
          nutritionFacts={
            loading ? <div>Loading nutrition...</div> : error ? <div className="text-red-500">{error}</div> : (
              <NutritionFactsCard
                nutrients={nutritionData ? nutritionData.nutrients : []}
                servingInfo={nutritionData ? nutritionData.serving_info : null}
              />
            )
          }
          nutritionSummary={
            loading ? <div>Loading summary...</div> : error ? <div className="text-red-500">{error}</div> : (
              <NutritionSummaryCard summary={nutritionSummary} />
            )
          }
        />
      </div>
    </div>
  );
};

export default ProductDetailsModal; 