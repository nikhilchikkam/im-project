import React from 'react';
import ProductCard from '../product/ProductCard';
import ProductTable from '../product/ProductTable';

interface ProductResultsProps {
  products: any[];
  loading: boolean;
  error: string | null;
  viewType: 'card' | 'list';
  setSelectedProduct: (product: any) => void;
}

const ProductResults: React.FC<ProductResultsProps> = ({
  products,
  loading,
  error,
  viewType,
  setSelectedProduct,
}) => {
  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center text-red-500 py-8">{error}</div>;
  if (products.length === 0) return <div className="text-center py-8">No products found.</div>;
  if (viewType === 'card') {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
        {products.map((p) => (
          <ProductCard
            key={p.gtin}
            upc={p.gtin}
            normalized_name={p.normalized_name}
            name={p.name}
            title={p.title}
            category={p.family_title || ''}
            description={p.description}
            isSmartSnack={p.is_smart_snack}
            novaLabel={p.nova_label}
            isGoodChoice={p.is_good_choice}
            onEnlarge={() => setSelectedProduct(p)}
          />
        ))}
      </div>
    );
  }
  return (
    <div className="mt-4">
      <ProductTable products={products.map(p => ({
        id: p.gtin,
        category: p.family_title || '',
        itemNumber: p.gtin,
        name: p.name || p.title,
        normalized_name: p.normalized_name,
        description: p.description,
      }))} />
    </div>
  );
};

export default ProductResults; 