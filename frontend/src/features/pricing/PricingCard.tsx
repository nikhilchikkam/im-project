import React from 'react';
import { Link } from 'react-router-dom';
import { Check, X } from 'lucide-react';

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
  highlight,
}: PricingCardProps) => {
  const cardClasses = `
    border rounded-lg p-8 flex flex-col h-full
    ${highlight ? 'border-blue-500' : 'border-gray-300'}
  `;

  return (
    <div className={cardClasses}>
      <div className="flex-grow">
        <h3 className="text-xl font-bold text-center mb-2">{title}</h3>
        <p className="text-center text-gray-500 mb-6">{subtitle}</p>
        <p className="text-4xl font-bold text-center mb-1">{price}</p>
        <p className="text-center text-blue-500 font-semibold mb-8">{period}</p>
        <ul className="space-y-4">
          {features.map((feature, i) => (
            <li key={i} className="flex items-center gap-3">
              {feature.included ? (
                <Check className="w-5 h-5 text-green-500" />
              ) : (
                <X className="w-5 h-5 text-red-500" />
              )}
              <span>{feature.text}</span>
            </li>
          ))}
        </ul>
      </div>
      <Link to="/subscription" className="w-full mt-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 text-center">
        Get it now
      </Link>
    </div>
  );
};
