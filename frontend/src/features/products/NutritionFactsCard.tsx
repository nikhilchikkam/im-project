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

const NutritionFactsCard = ({ nutritionFacts }: { nutritionFacts: NutritionFacts }) => {
  // For now, use placeholder data
  const nf = nutritionFacts || {
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
  return (
    <div className="bg-white border-2 border-black p-4 w-80 min-w-[320px] max-w-xs rounded-lg">
      <div className="text-2xl font-extrabold border-b-8 border-black pb-1 mb-1">Nutrition Facts</div>
      <div className="text-sm mb-1">Serving size {nf.servingSize}</div>
      <div className="text-sm mb-1">Servings Per Container {nf.servingsPerContainer}</div>
      <div className="border-b border-black my-1" />
      <div className="flex justify-between text-lg font-bold mb-1">
        <span>Calories</span>
        <span>{nf.calories}</span>
      </div>
      <div className="border-b-4 border-black my-1" />
      <div className="text-xs mb-1">% Daily Value*</div>
      <div className="flex justify-between text-base font-semibold">
        <span>Total Fat {nf.totalFat}g</span>
        <span>10%</span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Saturated Fat {nf.saturatedFat}g</span>
        <span>5%</span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Trans Fat {nf.transFat}g</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Cholesterol {nf.cholesterol}mg</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Sodium {nf.sodium}mg</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Total Carbohydrate {nf.totalCarb}g</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Dietary Fiber {nf.dietaryFiber}g</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-xs ml-4">
        <span>Sugars {nf.sugars}g</span>
        <span>0%</span>
      </div>
      <div className="flex justify-between text-base font-semibold">
        <span>Protein {nf.protein}g</span>
        <span>0%</span>
      </div>
      <div className="flex flex-col gap-0.5 text-xs mt-2">
        <div>Vitamin D {nf.vitaminD}mcg 10%</div>
        <div>Calcium {nf.calcium}mcg 10%</div>
        <div>Potassium {nf.potassium}mg 10%</div>
        <div>Iron {nf.iron}mg 10%</div>
      </div>
      <div className="text-[10px] text-gray-500 mt-2">* Percent Daily Values are based on a 2,000 calorie diet. Your Daily Values may be higher or lower depending on your calorie needs</div>
    </div>
  );
};

export default NutritionFactsCard; 