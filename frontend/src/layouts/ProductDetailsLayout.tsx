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
}) => {
  const [cuisine, claim, allergens] = React.Children.toArray(halalKosherBlock as React.ReactNode);
  return (
    <div className="flex flex-col gap-8">
      {/* Top: header and description */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div>{headerBlock}</div>
        <div>{descriptionBlock}</div>
      </div>
      {/* Cuisine and Claim full width row */}
      <div className="flex gap-4 mb-2 w-full">
        <div className="flex-1">{cuisine}</div>
        <div className="flex-1">{claim}</div>
      </div>
      {/* Allergens full width row */}
      {allergens && (
        <div className="w-full mb-4">{allergens}</div>
      )}
      {/* Main content: Nutrition facts (left), Nutrition summary + Ingredients (right) */}
      <div className="flex flex-col md:flex-row gap-8 mt-6">
        <div className="flex-shrink-0 w-full md:w-1/2 flex flex-col justify-stretch">
          {nutritionFacts}
        </div>
        <div className="flex-1 flex flex-col gap-4 justify-between h-full">
          <div>{nutritionSummary}</div>
          <div>{ingredientsBlock}</div>
        </div>
      </div>
      {/* Gauges if any */}
      {gauges && <div className="flex flex-col gap-4">{gauges}</div>}
    </div>
  );
};

export default ProductDetailsLayout; 