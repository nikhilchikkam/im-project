type Props = {
  billing: 'monthly' | 'yearly';
  onChange: (val: 'monthly' | 'yearly') => void;
};

export const PricingToggle = ({ billing, onChange }: Props) => {
  return (
    <div className="flex items-center gap-2 mb-6 justify-center">
      <span>Monthly</span>
      <button
        className={`w-14 h-7 rounded-full p-1 transition bg-gray-200 flex ${
          billing === 'yearly' ? 'justify-end' : 'justify-start'
        }`}
        onClick={() => onChange(billing === 'monthly' ? 'yearly' : 'monthly')}
      >
        <div className="w-5 h-5 bg-white rounded-full shadow" />
      </button>
      <span>Yearly</span>
      <span className="text-xs text-blue-600 ml-2">Save 25%</span>
    </div>
  );
};
