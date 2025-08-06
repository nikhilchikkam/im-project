import React, { useState } from 'react';
import ProductCard from '../product/ProductCard';
import ProductTable from '../product/ProductTable';
import HierarchyModal from '../modals/HierarchyModal';

interface ProductResultsProps {
  products: any[];
  loading: boolean;
  error: string | null;
  viewType: 'card' | 'list';
  setSelectedProduct: (product: any) => void;
  selectedItems?: string[];
  onItemSelect?: (gtin: string) => void;
  selectAll?: boolean;
  onSelectAll?: () => void;
}

const ProductResults: React.FC<ProductResultsProps> = ({
  products,
  loading,
  error,
  viewType,
  setSelectedProduct,
  selectedItems = [],
  onItemSelect,
  selectAll = false,
  onSelectAll,
}) => {
  const [hierarchyModal, setHierarchyModal] = useState<{
    isOpen: boolean;
    gtin: string;
  }>({
    isOpen: false,
    gtin: '',
  });

  const handleHierarchyClick = (product: any) => {
    setHierarchyModal({
      isOpen: true,
      gtin: product.gtin,
    });
  };

  const closeHierarchyModal = () => {
    setHierarchyModal({
      isOpen: false,
      gtin: '',
    });
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center text-red-500 py-8">{error}</div>;
  if (products.length === 0) return <div className="text-center py-8">No products found.</div>;
  
  if (viewType === 'card') {
    return (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
          {products.map((p) => {
            // Flatten image_urls JSON object to a single array
            let imageUrls: string[] = [];
            if (p.image_urls) {
              if (Array.isArray(p.image_urls.externalFileLink)) {
                imageUrls = imageUrls.concat(p.image_urls.externalFileLink.filter(Boolean));
              }
              if (Array.isArray(p.image_urls.dam)) {
                imageUrls = imageUrls.concat(p.image_urls.dam.filter(Boolean));
              }
            }
            return (
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
                imageUrls={imageUrls}
                onEnlarge={() => setSelectedProduct(p)}
                onHierarchy={() => handleHierarchyClick(p)}
                isSelected={selectedItems.includes(p.gtin)}
                onSelect={() => {
                  onItemSelect && onItemSelect(p.gtin);
                }}
                showCheckbox={true}
              />
            );
          })}
        </div>
        
        {/* Hierarchy Modal */}
        <HierarchyModal
          isOpen={hierarchyModal.isOpen}
          onClose={closeHierarchyModal}
          gtin={hierarchyModal.gtin}
        />
      </>
    );
  }
  
  return (
    <div className="mt-4">
      <ProductTable 
        products={products.map(p => ({
          id: p.gtin,
          category: p.family_title || '',
          itemNumber: p.gtin,
          name: p.name || p.title,
          normalized_name: p.normalized_name,
          description: p.description,
        }))}
        selectedItems={selectedItems}
        onItemSelect={onItemSelect}
        selectAll={selectAll}
        onSelectAll={onSelectAll}
      />
    </div>
  );
};

export default ProductResults; 