import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import Toolbar from '../../components/ui/Toolbar';
import BulkActionsBar from '../../components/common/BulkActionsBar';
import WishlistTable from '../../features/wishlist/WishlistTable';
import type { DataItem } from '../../components/ui/DataTable';

// Mock data
const mockWishlistItems: DataItem[] = Array.from({ length: 11 }).map((_, i) => ({
  id: `${i}`,
  category: 'Meat',
  itemNumber: '9090909090',
  product: 'Chex Mix',
  description: 'Description of the product goes here',
}));

const WishlistDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [title, setTitle] = useState(`My Wishlist ${id}`);
  const [items, setItems] = useState<DataItem[]>(mockWishlistItems);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const handleSelect = (itemId: string) => {
    setSelectedItems(prev => prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]);
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedItems(checked ? items.map(item => item.id) : []);
  };

  const handleBulkDelete = () => {
    setItems(prev => prev.filter(item => !selectedItems.includes(item.id)));
    setSelectedItems([]);
  };

  const handleAddToList = (id: string) => {
    console.log(`Adding item ${id} to another list`);
  };
  
  const handleMoreOptions = (id: string) => {
    console.log(`More options for item ${id}`);
  };

  const handleBulkMoveToCart = () => {
    console.log(`Moving items ${selectedItems.join(', ')} to cart`);
    // Add logic to move items to cart
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <NavbarAfter />
      <main className="flex-1 container mx-auto px-6 py-8">
        <Toolbar
          title={title}
          onBack={() => navigate('/wishlist')}
          onTitleChange={setTitle}
          onShare={() => console.log('Share action')}
          onAddItem={() => navigate('/')}
        />
        {selectedItems.length > 0 && (
          <BulkActionsBar
            selectedCount={selectedItems.length}
            onDelete={handleBulkDelete}
            onClearSelection={() => setSelectedItems([])}
            onSecondaryAction={handleBulkMoveToCart}
            secondaryActionLabel="Move to Cart"
          />
        )}
        <WishlistTable
          items={items}
          selectedItems={selectedItems}
          onSelect={handleSelect}
          onSelectAll={handleSelectAll}
          onAddToList={handleAddToList}
          onMoreOptions={handleMoreOptions}
        />
      </main>
    </div>
  );
};

export default WishlistDetailPage; 