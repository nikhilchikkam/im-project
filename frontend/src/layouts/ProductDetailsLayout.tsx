import React, { type ReactNode } from 'react';

interface ProductDetailsLayoutProps {
  headerBlock: ReactNode;
  descriptionBlock: ReactNode;
  ingredientsBlock: ReactNode;
  halalKosherBlock: ReactNode;
  allergensBlock?: ReactNode;
  nutritionFacts: ReactNode;
  nutritionSummary: ReactNode;
  gauges?: ReactNode;
}

const ProductDetailsLayout: React.FC<ProductDetailsLayoutProps> = ({
  headerBlock,
  descriptionBlock,
  ingredientsBlock,
  halalKosherBlock,
  allergensBlock,
  nutritionFacts,
  nutritionSummary,
  gauges,
}) => (
  <div className="flex flex-col gap-8">
    {/* Top: 2x2 grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
      <div>{headerBlock}</div>
      <div>{descriptionBlock}</div>
      <div>{ingredientsBlock}</div>
      <div>{halalKosherBlock}</div>
    </div>
    {/* Allergens full width */}
    {allergensBlock && (
      <div className="w-full">{allergensBlock}</div>
    )}
    {/* Nutrition facts and summary side by side */}
    <div className="flex flex-col md:flex-row gap-8 mt-6">
      <div className="flex-shrink-0">{nutritionFacts}</div>
      <div className="flex-1 flex flex-col gap-4">
        {nutritionSummary}
        {gauges && <div className="flex flex-col gap-4">{gauges}</div>}
      </div>
    </div>
  </div>
);

export default ProductDetailsLayout; 