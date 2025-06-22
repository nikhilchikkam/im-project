import React from 'react';

type PricingToggleProps = {
  billing: 'monthly' | 'yearly';
  onChange: (billing: 'monthly' | 'yearly') => void;
};

export const PricingToggle = ({ billing, onChange }: PricingToggleProps) => {
  const isYearly = billing === 'yearly';
  
  const toggle = () => {
    onChange(isYearly ? 'monthly' : 'yearly');
  };

  return (
    <div className="flex items-center justify-center gap-4 mb-8">
      <span>Monthly</span>
      <button
        onClick={toggle}
        className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${
          isYearly ? 'bg-blue-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${
            isYearly ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      <span>Yearly</span>
      <span className="bg-blue-600 text-white text-sm font-semibold px-3 py-1 rounded-full">
        Save 25%
      </span>
    </div>
  );
};
