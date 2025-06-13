import React, { useState } from 'react';
import NavbarAfter from '../components/NavbarAfter';
import WishlistToolbar from '../features/wishlist/WishlistToolbar';
import WishlistBulkActionsBar from '../features/wishlist/WishlistBulkActionsBar';
import WishlistTable from '../features/wishlist/WishlistTable';

const PLACEHOLDER_ITEMS = Array.from({ length: 12 }).map((_, i) => ({
  id: String(i + 1),
  category: 'Meat',
  itemNumber: '9090909090',
  product: 'Chex Mix',
  description: 'Description',
}));

const WishlistDetailPage = () => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [items, setItems] = useState(PLACEHOLDER_ITEMS);
  const [title, setTitle] = useState('My Wishlist');

  // Placeholder handlers
  const handleBack = () => alert('Back');
  const handleTitleChange = (newTitle: string) => setTitle(newTitle);
  const handleShare = (action: string) => alert(`Share: ${action}`);
  const handleAddItem = () => alert('Add item');
  const handleDeleteSelected = () => {
    setItems(items.filter(item => !selectedItems.includes(item.id)));
    setSelectedItems([]);
  };
  const handleDelete = (id: string) => {
    setItems(items.filter(item => item.id !== id));
    setSelectedItems(selectedItems.filter(sid => sid !== id));
  };
  const handleSelect = (id: string) => {
    setSelectedItems(selectedItems.includes(id)
      ? selectedItems.filter(sid => sid !== id)
      : [...selectedItems, id]);
  };
  const handleSelectAll = (checked: boolean) => {
    setSelectedItems(checked ? items.map(item => item.id) : []);
  };

  return (
    <div className="min-h-screen bg-white">
      <NavbarAfter />
      <div className="px-8 pt-6">
        <WishlistToolbar
          title={title}
          onBack={handleBack}
          onTitleChange={handleTitleChange}
          onShare={handleShare}
          onAddItem={handleAddItem}
        />
        {selectedItems.length > 0 && (
          <WishlistBulkActionsBar
            selectedCount={selectedItems.length}
            onDelete={handleDeleteSelected}
            onClearSelection={() => setSelectedItems([])}
          />
        )}
        <div className="mt-4">
          <WishlistTable
            items={items}
            selectedItems={selectedItems}
            onSelect={handleSelect}
            onSelectAll={handleSelectAll}
            onDelete={handleDelete}
          />
        </div>
      </div>
    </div>
  );
};

export default WishlistDetailPage; 