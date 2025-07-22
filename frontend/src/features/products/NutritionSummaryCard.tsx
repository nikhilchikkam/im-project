type NutritionSummary = {
  calories: string | number;
  calories_unit?: string;
  fat: string | number;
  fat_unit?: string;
  sodium: string | number;
  sodium_unit?: string;
  protein: string | number;
  protein_unit?: string;
};

const NutritionSummaryCard = ({ summary }: { summary: NutritionSummary }) => {
  const s = summary || {
    calories: 'N/A',
    fat: 'N/A',
    sodium: 'N/A',
    protein: 'N/A',
  };
  const showValueWithUnit = (val: string | number, unit?: string) => {
    const isNA = val === undefined || val === null || val === '' || val === 'N/A';
    const validUnit = unit && unit !== 'FLAGGED_UNIT';
    return (
      <span>
        {isNA ? 'N/A' : <span className="text-2xl font-bold">{val}</span>}
        {validUnit && (
          <span className={isNA ? 'text-gray-400 text-xs ml-1' : 'text-xs text-gray-500 ml-1 font-normal'}>{unit}</span>
        )}
      </span>
    );
  };
  return (
    <div className="flex bg-white rounded-lg border shadow-sm mb-4">
      <div className="flex-1 text-center p-4">
        <div className="text-2xl font-bold">{showValueWithUnit(s.calories, s.calories_unit)}</div>
        <div className="text-xs text-gray-500">Calories<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{showValueWithUnit(s.fat, s.fat_unit)}</div>
        <div className="text-xs text-gray-500">Fat<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{showValueWithUnit(s.sodium, s.sodium_unit)}</div>
        <div className="text-xs text-gray-500">Sodium<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{showValueWithUnit(s.protein, s.protein_unit)}</div>
        <div className="text-xs text-gray-500">Protein<br />per serving</div>
      </div>
    </div>
  );
};

export default NutritionSummaryCard; 