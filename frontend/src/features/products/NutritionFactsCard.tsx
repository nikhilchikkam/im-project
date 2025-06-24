import React from 'react';

type Nutrient = {
  nutrient_label: string;
  value: string | number;
  unit: string;
  daily_value_intake_percent?: string | number;
};

type ServingInfo = {
  serving_description?: string;
  serving_size_value?: number;
  serving_size_unit?: string;
  servings_per_container?: string | number;
};

type Props = {
  servingInfo?: ServingInfo | null;
  nutrients: Nutrient[];
};

const NutritionFactsCard: React.FC<Props> = ({ servingInfo, nutrients }) => {
  const si = servingInfo || {};
  // Helper to find nutrients by label
  const getNutrient = (label: string) =>
    nutrients.find(n => n.nutrient_label.toLowerCase().includes(label.toLowerCase()));

  const totalFat = getNutrient('total_fat');
  const satFat = getNutrient('saturated_fat');
  const transFat = getNutrient('trans_fat');
  const cholesterol = getNutrient('cholesterol');
  const sodium = getNutrient('sodium');
  const totalCarb = getNutrient('total_carbohydrate');
  const fiber = getNutrient('dietary_fiber');
  const totalSugars = getNutrient('sugars');
  const addedSugars = getNutrient('added_sugars');
  const protein = getNutrient('protein');
  const vitaminD = getNutrient('vitamin_d');
  const calcium = getNutrient('calcium');
  const iron = getNutrient('iron');
  const potassium = getNutrient('potassium');
  const calories = getNutrient('calories');

  return (
    <div className="bg-white border-[8px] border-black w-[380px] p-0 font-sans text-black select-none">
      {/* Header */}
      <div className="text-[2.1rem] font-extrabold leading-none border-b-[8px] border-black px-3 pt-2 pb-1 tracking-tight">Nutrition Facts</div>
      {/* Servings per container */}
      <div className="text-base font-normal px-3 pt-1 pb-0.5">{si.servings_per_container ?? 'N/A'} servings per container</div>
      {/* Serving size */}
      <div className="text-base font-normal px-3 pb-1"><span className="font-bold">Serving size</span> {si.serving_size_value ?? 'N/A'} {si.serving_size_unit ?? ''} {si.serving_description ? `(${si.serving_description})` : ''}</div>
      {/* Thick divider */}
      <div className="border-b-[4px] border-black mx-0 my-1" />
      {/* Amount per serving */}
      <div className="px-3 pt-1 pb-0.5 text-[1.05rem] font-bold">Amount per serving</div>
      {/* Calories */}
      <div className="flex justify-between items-end px-3 pb-1">
        <span className="text-[2.2rem] font-extrabold leading-none">Calories</span>
        <span className="text-[2.2rem] font-extrabold leading-none">{calories?.value || 0}</span>
      </div>
      {/* Thick divider */}
      <div className="border-b-[4px] border-black mx-0 my-1" />
      {/* % Daily Value */}
      <div className="flex justify-end px-3 text-xs font-bold uppercase pb-0.5">% Daily Value*</div>
      {/* Thin divider */}
      <div className="border-b border-black mx-0 my-1" />
      {/* Nutrient rows */}
      <div className="px-3">
        <div className="flex justify-between text-[1.05rem] border-0 border-b border-black font-bold">
          <span><span className="font-bold">Total Fat</span> <span className="font-normal">{totalFat?.value}{totalFat?.unit}</span></span>
          <span>{totalFat?.daily_value_intake_percent ? <span className="font-bold">{`${totalFat.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] ml-4 border-b border-black">
          <span><span className="font-bold">Saturated Fat</span> {satFat?.value}{satFat?.unit}</span>
          <span>{satFat?.daily_value_intake_percent ? <span className="font-bold">{`${satFat.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] ml-4 italic border-b border-black">
          <span><span className="font-bold not-italic">Trans Fat</span> {transFat?.value}{transFat?.unit}</span>
        </div>
        <div className="flex justify-between text-[1.05rem] border-0 border-b border-black font-bold">
          <span><span className="font-bold">Cholesterol</span> <span className="font-normal">{cholesterol?.value}{cholesterol?.unit}</span></span>
          <span>{cholesterol?.daily_value_intake_percent ? <span className="font-bold">{`${cholesterol.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[1.05rem] border-0 border-b border-black font-bold">
          <span><span className="font-bold">Sodium</span> <span className="font-normal">{sodium?.value}{sodium?.unit}</span></span>
          <span>{sodium?.daily_value_intake_percent ? <span className="font-bold">{`${sodium.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[1.05rem] border-0 border-b border-black font-bold">
          <span><span className="font-bold">Total Carbohydrate</span> <span className="font-normal">{totalCarb?.value}{totalCarb?.unit}</span></span>
          <span>{totalCarb?.daily_value_intake_percent ? <span className="font-bold">{`${totalCarb.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] ml-4 border-b border-black">
          <span><span className="font-bold">Dietary Fiber</span> {fiber?.value}{fiber?.unit}</span>
          <span>{fiber?.daily_value_intake_percent ? <span className="font-bold">{`${fiber.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] ml-4 border-b border-black">
          <span><span className="font-bold">Total Sugars</span> {totalSugars?.value}{totalSugars?.unit}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] ml-8 border-b border-black">
          <span>Includes {addedSugars?.value}{addedSugars?.unit} Added Sugars</span>
          <span>{addedSugars?.daily_value_intake_percent ? <span className="font-bold">{`${addedSugars.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[1.05rem] border-0 font-bold">
          <span><span className="font-bold">Protein</span> <span className="font-normal">{protein?.value}{protein?.unit}</span></span>
        </div>
      </div>
      {/* Thick divider */}
      <div className="border-b-[4px] border-black mx-0 my-2" />
      {/* Vitamins and minerals */}
      <div className="px-3">
        <div className="flex justify-between text-[0.98rem] border-b border-black">
          <span><span className="font-bold">Vitamin D</span> {vitaminD?.value}{vitaminD?.unit}</span>
          <span>{vitaminD?.daily_value_intake_percent ? <span className="font-bold">{`${vitaminD.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] border-b border-black">
          <span><span className="font-bold">Calcium</span> {calcium?.value}{calcium?.unit}</span>
          <span>{calcium?.daily_value_intake_percent ? <span className="font-bold">{`${calcium.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem] border-b border-black">
          <span><span className="font-bold">Iron</span> {iron?.value}{iron?.unit}</span>
          <span>{iron?.daily_value_intake_percent ? <span className="font-bold">{`${iron.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
        <div className="flex justify-between text-[0.98rem]">
          <span><span className="font-bold">Potassium</span> {potassium?.value}{potassium?.unit}</span>
          <span>{potassium?.daily_value_intake_percent ? <span className="font-bold">{`${potassium.daily_value_intake_percent}%`}</span> : ''}</span>
        </div>
      </div>
      {/* Thin divider */}
      <div className="border-b border-black mx-0 my-2" />
      {/* Footnote */}
      <div className="text-[0.68rem] text-black px-3 pb-2 pt-1 leading-tight">
        * The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.
      </div>
    </div>
  );
};

export default NutritionFactsCard; 