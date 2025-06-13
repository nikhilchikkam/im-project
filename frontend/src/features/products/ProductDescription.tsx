type ProductDescriptionProps = {
  description: string;
};

const ProductDescription = ({ description }: ProductDescriptionProps) => (
  <div>
    <div className="text-xs font-semibold text-gray-700 mb-1">Product Description</div>
    <div className="text-sm text-gray-900 leading-relaxed">{description}</div>
  </div>
);

export default ProductDescription; 