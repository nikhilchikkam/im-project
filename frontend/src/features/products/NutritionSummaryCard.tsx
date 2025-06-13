type NutritionSummary = {
  calories: number;
  fat: number;
  sodium: number;
  protein: number;
};

const NutritionSummaryCard = ({ summary }: { summary: NutritionSummary }) => {
  const s = summary || {
    calories: 417,
    fat: 10.3,
    sodium: 707,
    protein: 8.74,
  };
  return (
    <div className="flex bg-white rounded-lg border shadow-sm mb-4">
      <div className="flex-1 text-center p-4">
        <div className="text-2xl font-bold">{s.calories}</div>
        <div className="text-xs text-gray-500">Calories<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{s.fat} g</div>
        <div className="text-xs text-gray-500">Fat<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{s.sodium} g</div>
        <div className="text-xs text-gray-500">Sodium<br />per serving</div>
      </div>
      <div className="flex-1 text-center p-4 border-l">
        <div className="text-2xl font-bold">{s.protein} g</div>
        <div className="text-xs text-gray-500">Protein<br />per serving</div>
      </div>
    </div>
  );
};

export default NutritionSummaryCard; 