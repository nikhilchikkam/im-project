import { useState } from 'react';
import { PricingToggle } from './PricingToggle';
import { PricingCard } from './PricingCard';

const plans = {
  monthly: [
    {
      title: 'Starter Pack',
      subtitle: 'Best for individuals',
      price: '$0',
      period: 'per month',
      features: [true, true, true, false, false],
    },
    {
      title: 'Small Teams',
      subtitle: 'Best for teams of 5',
      price: '$34.99',
      period: 'per month',
      features: [true, true, true, true, false],
    },
    {
      title: 'Enterprise',
      subtitle: 'More than 10 users',
      price: '$899.99',
      period: 'per month',
      features: [true, true, true, true, true],
    },
  ],
  yearly: [
    {
      title: 'Starter Pack',
      subtitle: 'Best for individuals',
      price: '$0',
      period: 'per year',
      features: [true, true, true, false, false],
    },
    {
      title: 'Small Teams',
      subtitle: 'Best for teams of 5',
      price: '$799.99',
      period: 'per year',
      features: [true, true, true, true, false],
    },
    {
      title: 'Enterprise',
      subtitle: 'More than 10 users',
      price: '$1099.99',
      period: 'per year',
      features: [true, true, true, true, true],
    },
  ],
};

const featureTexts = [
  'Lorem ipsum dolor sit amet.',
  'Lorem ipsum dolor sit amet.',
  'Lorem ipsum dolor sit amet.',
  'Lorem ipsum dolor sit amet.',
  'Lorem ipsum dolor sit amet.',
];

export const PricingSection = () => {
  const [billing, setBilling] = useState<'monthly' | 'yearly'>('monthly');

  return (
    <section className="max-w-7xl mx-auto px-4 py-16">
      <h2 className="text-3xl font-bold text-center mb-2">Pricing</h2>
      <p className="text-center text-gray-600 max-w-xl mx-auto mb-8">
        We offer a range of plans. Choose based on your needs. You can downgrade or upgrade your plan later.
      </p>

      <PricingToggle billing={billing} onChange={setBilling} />

      <div className="grid md:grid-cols-3 gap-6">
        {plans[billing].map((plan, i) => (
          <PricingCard
            key={i}
            title={plan.title}
            subtitle={plan.subtitle}
            price={plan.price}
            period={plan.period}
            features={featureTexts.map((text, idx) => ({
              text,
              included: plan.features[idx],
            }))}
            highlight={i === 0} // highlight starter
          />
        ))}
      </div>
    </section>
  );
};
