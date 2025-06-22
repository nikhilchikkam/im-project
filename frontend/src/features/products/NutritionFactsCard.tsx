type NutritionFacts = {
  calories: number;
  servingSize: string;
  servingsPerContainer: number;
  totalFat: number;
  saturatedFat: number;
  transFat: number;
  cholesterol: number;
  sodium: number;
  totalCarb: number;
  dietaryFiber: number;
  sugars: number;
  protein: number;
  vitaminD: number;
  calcium: number;
  potassium: number;
  iron: number;
};

type ServingInfo = {
  serving_description?: string;
  serving_size_value?: number;
  serving_size_unit?: string;
  basis_quantity_type?: string;
  // ... (other serving fields if needed)
};

const NutritionFactsCard = ({ nutritionFacts, servingInfo }: { nutritionFacts: NutritionFacts, servingInfo: ServingInfo | null }) => {
  const nf = nutritionFacts || {};
  const si = servingInfo || {};
  const amountPerText = si.basis_quantity_type === 'BY_MEASURE' ? 'Amount Per Measure' : 'Amount Per Serving';
  const servingsPerContainerText = si.serving_size_value && si.serving_size_unit
    ? `${si.serving_size_value} ${si.serving_size_unit}`
    : 'N/A';

  return (
    <div className="bg-white border-2 border-black p-4 w-80 min-w-[320px] max-w-xs rounded-lg">
      <div className="text-2xl font-extrabold border-b-8 border-black pb-1 mb-1">Nutrition Facts</div>
      <div className="text-sm mb-1">Serving size {si.serving_description || 'N/A'}</div>
      <div className="text-sm mb-1">Servings Per Container {servingsPerContainerText}</div>
      <div className="border-b-4 border-black my-1" />
      <div className="font-bold text-sm py-1">{amountPerText}</div>
      <div className="border-b border-black my-1" />
      <div className="flex justify-between text-lg font-bold mb-1">
        <span>Calories</span>
        <span>{nf.calories || 0}</span>
      </div>
      <div className="border-b-4 border-black my-1" />
      <div className="text-xs mb-1">% Daily Value*</div>
      <div className="flex justify-between text-base font-semibold">
        <span>Total Fat {nf.totalFat || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Saturated Fat {nf.saturatedFat || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Trans Fat {nf.transFat || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Cholesterol {nf.cholesterol || 0}mg</span>
        <span></span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Sodium {nf.sodium || 0}mg</span>
        <span></span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Total Carbohydrate {nf.totalCarb || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Dietary Fiber {nf.dietaryFiber || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Sugars {nf.sugars || 0}g</span>
        <span></span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Protein {nf.protein || 0}g</span>
        <span></span>
      </div>
      <div className="flex flex-col gap-0.5 text-xs mt-2">
        <div>Vitamin D {nf.vitaminD || 0}mcg</div>
        <div>Calcium {nf.calcium || 0}mg</div>
        <div>Potassium {nf.potassium || 0}mg</div>
        <div>Iron {nf.iron || 0}mg</div>
      </div>
      <div className="text-[10px] text-gray-500 mt-2">* Percent Daily Values are based on a 2,000 calorie diet. Your Daily Values may be higher or lower depending on your calorie needs</div>
    </div>
  );
};

export default NutritionFactsCard; 