import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import NutritionFactsCard from './NutritionFactsCard';
import NutritionSummaryCard from './NutritionSummaryCard';
import ProductHeader from './ProductHeader';
import ProductDescription from './ProductDescription';
import ProductTagsSection from './ProductTagsSection';
import ProductDetailsLayout from '../../layouts/ProductDetailsLayout';
import { useCartWishlist } from '../../contexts/CartWishlistContext';

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

// Helper to get nutrient by label
const getNutrient = (nutrients: any[], label: string) =>
  nutrients.find((n: any) => n.nutrient_label && n.nutrient_label.toLowerCase().includes(label.toLowerCase()));

// NutritionSummary type
interface NutritionSummary {
  calories: string | number;
  calories_unit?: string;
  fat: string | number;
  fat_unit?: string;
  sodium: string | number;
  sodium_unit?: string;
  protein: string | number;
  protein_unit?: string;
}

const claimColors = [
  'bg-blue-100 text-blue-700',
  'bg-green-100 text-green-700',
  'bg-yellow-100 text-yellow-700',
  'bg-purple-100 text-purple-700',
  'bg-pink-100 text-pink-700',
  'bg-red-100 text-red-700',
  'bg-gray-100 text-gray-700'
];

const ProductDetailsModal = ({ product, onClose }: ProductDetailsModalProps) => {
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [allergens, setAllergens] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [productDetails, setProductDetails] = useState<any | null>(null);
  const [dietClaims, setDietClaims] = useState<{diet_types: string[], claims: Record<string, string[]>} | null>(null);
  const [actionLoading, setActionLoading] = useState<'wishlist' | 'cart' | null>(null);
  const { addToWishlist, addToCart, isInWishlist, isInCart } = useCartWishlist();

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
    // Fetch diet types and claims
    fetch(`${apiUrl}/api/diet_claims/${product.gtin}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => setDietClaims(data))
      .catch(() => setDietClaims(null));
  }, [product?.gtin]);

  useEffect(() => {
    if (!product?.gtin) return;
    // Prevent background scroll
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  const details = productDetails || product;
  const nutritionFacts = nutritionData ? mapNutritionFacts(nutritionData.nutrients) : {};
  const nutritionSummary = nutritionData ? mapNutritionSummary(nutritionData.nutrients) : {};

  const summary: NutritionSummary = nutritionData && nutritionData.nutrients ? {
    calories: getNutrient(nutritionData.nutrients, 'calories')?.standardized_value ?? 'N/A',
    calories_unit: getNutrient(nutritionData.nutrients, 'calories')?.standardized_unit ?? '',
    fat: getNutrient(nutritionData.nutrients, 'total_fat')?.standardized_value ?? 'N/A',
    fat_unit: getNutrient(nutritionData.nutrients, 'total_fat')?.standardized_unit ?? '',
    sodium: getNutrient(nutritionData.nutrients, 'sodium')?.standardized_value ?? 'N/A',
    sodium_unit: getNutrient(nutritionData.nutrients, 'sodium')?.standardized_unit ?? '',
    protein: getNutrient(nutritionData.nutrients, 'protein')?.standardized_value ?? 'N/A',
    protein_unit: getNutrient(nutritionData.nutrients, 'protein')?.standardized_unit ?? '',
  } : {
    calories: 'N/A',
    calories_unit: '',
    fat: 'N/A',
    fat_unit: '',
    sodium: 'N/A',
    sodium_unit: '',
    protein: 'N/A',
    protein_unit: '',
  };

  const dietClaimsBlock = (
    <div className="flex flex-col gap-2">
      <ProductTagsSection
        title="Diet Types"
        tags={dietClaims?.diet_types ?? []}
        emptyText="No data available"
      />
      <div className="flex flex-wrap gap-2">
        {dietClaims && dietClaims.claims && Object.keys(dietClaims.claims).length > 0 ? (
          Object.entries(dietClaims.claims).map(([type, tags], idx) => (
            <ProductTagsSection
              key={type}
              title={type.replace(/_/g, ' ')}
              tags={tags}
              // @ts-ignore
              tagClass={claimColors[idx % claimColors.length]}
              emptyText="No data available"
            />
          ))
        ) : (
          <ProductTagsSection title="Claims" tags={[]} emptyText="No data available" />
        )}
      </div>
    </div>
  );

  // Placeholder: Replace with actual cuisine and claim tags from your data/API
  const cuisineTags = details.cuisineTags || [];
  const claimTags = details.claimTags || [];

  const cuisineAndClaimBlock = (
    <>
      <div className="flex gap-4 mb-2">
        <div className="flex-1">
          <ProductTagsSection title="Cuisine" tags={cuisineTags} emptyText="No data available" />
        </div>
        <div className="flex-1">
          <ProductTagsSection title="Claim" tags={claimTags} emptyText="No data available" />
        </div>
      </div>
      <div className="mb-4">
        <ProductTagsSection title="Allergens" tags={allergens} emptyText="No data available" />
      </div>
    </>
  );

  const handleAddToWishlist = async () => {
    if (!product?.gtin) return;
    setActionLoading('wishlist');
    try {
      await addToWishlist(product.gtin);
    } finally {
      setActionLoading(null);
    }
  };

  const handleAddToCart = async () => {
    if (!product?.gtin) return;
    setActionLoading('cart');
    try {
      await addToCart(product.gtin);
    } finally {
      setActionLoading(null);
    }
  };

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
              <div className="flex gap-2 mb-2">
                <button
                  className={`bg-blue-100 text-blue-700 px-4 py-2 rounded font-semibold ${isInWishlist(product.gtin) ? 'opacity-60 cursor-not-allowed' : ''}`}
                  onClick={handleAddToWishlist}
                  disabled={actionLoading === 'wishlist' || isInWishlist(product.gtin)}
                >
                  {actionLoading === 'wishlist' ? 'Adding...' : isInWishlist(product.gtin) ? 'Wishlisted' : 'Wishlist'}
                </button>
                <button
                  className={`bg-blue-600 text-white px-4 py-2 rounded font-semibold ${isInCart(product.gtin) ? 'opacity-60 cursor-not-allowed' : ''}`}
                  onClick={handleAddToCart}
                  disabled={actionLoading === 'cart' || isInCart(product.gtin)}
                >
                  {actionLoading === 'cart' ? 'Adding...' : isInCart(product.gtin) ? 'In Cart' : 'Cart'}
                </button>
              </div>
            </>
          }
          descriptionBlock={
            <>
              <div className="font-semibold text-base mb-1">Product Description</div>
              <div className="text-sm text-gray-700 mb-4"><ProductDescription description={details.description} /></div>
            </>
          }
          halalKosherBlock={cuisineAndClaimBlock}
          allergensBlock={null}
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
              <NutritionSummaryCard summary={summary} />
            )
          }
          ingredientsBlock={
            details.ingredients ? (
              <div>
                <div className="font-semibold text-base mb-1">Ingredients</div>
                <div className="text-sm text-gray-700 whitespace-pre-line">{details.ingredients}</div>
              </div>
            ) : null
          }
        />
      </div>
    </div>
  );
};

export default ProductDetailsModal; 