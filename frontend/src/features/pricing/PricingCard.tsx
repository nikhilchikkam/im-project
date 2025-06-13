type PricingCardProps = {
  title: string;
  subtitle: string;
  price: string;
  period: string;
  features: { text: string; included: boolean }[];
  highlight?: boolean;
};

export const PricingCard = ({
  title,
  subtitle,
  price,
  period,
  features,
  highlight = false,
}: PricingCardProps) => {
  return (
    <div className={`rounded-xl p-6 shadow-sm border ${highlight ? 'bg-blue-50' : 'bg-white'}`}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{subtitle}</p>
      <div className="text-3xl font-bold mb-2">{price}</div>
      <div className="text-sm text-gray-500 mb-4">{period}</div>

      <ul className="space-y-2 mb-6">
        {features.map((f, idx) => (
          <li key={idx} className="flex items-center gap-2 text-sm">
            <span className={f.included ? 'text-green-600' : 'text-red-500'}>
              {f.included ? '✔' : '✘'}
            </span>
            {f.text}
          </li>
        ))}
      </ul>

      <button className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Get it now
      </button>
    </div>
  );
};
