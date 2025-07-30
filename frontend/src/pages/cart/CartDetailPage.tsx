import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NavbarAfter from '../../components/navigation/NavbarAfter';
import Toolbar from '../../components/ui/Toolbar';
import BulkActionsBar from '../../components/common/BulkActionsBar';
import CartTable from '../../features/cart/CartTable';
import type { DataItem } from '../../components/ui/DataTable';
import AddToWishlistModal from '../../features/wishlist/AddToWishlistModal';
import ShareModal from '../../components/modals/ShareModal';
import { useCartWishlist } from '../../contexts/CartWishlistContext';

// Mock data based on the image
const mockCartItems: DataItem[] = Array.from({ length: 11 }).map((_, i) => ({
  id: `${i}`,
  category: 'Meat',
  itemNumber: '9090909090',
  product: 'Chex Mix',
  description: 'Description',
}));

const CartDetailPage = () => {
  const navigate = useNavigate();
  const { addToWishlist } = useCartWishlist();
  const [items, setItems] = useState<DataItem[]>(mockCartItems);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [cartTitle, setCartTitle] = useState('My Cart');
  const [itemToMove, setItemToMove] = useState<DataItem | null>(null);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  const handleSelect = (id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedItems(checked ? items.map(item => item.id) : []);
  };

  const handleDelete = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
    setSelectedItems(prev => prev.filter(itemId => itemId !== id));
  };
  
  const handleMoveToWishlist = async () => {
    try {
      for (const itemId of selectedItems) {
        await addToWishlist(itemId);
      }
      setSelectedItems([]);
    } catch (error) {
      console.error('Failed to move items to wishlist:', error);
    }
  };

  const handleMoveToWishlistGroup = async (wishlistId: string) => {
    try {
      const itemToMove = items.find(item => item.id === selectedItems[0]);
      if (itemToMove) {
        await addToWishlist(itemToMove.itemNumber);
        setSelectedItems([]);
      }
    } catch (error) {
      console.error('Failed to move item to wishlist group:', error);
    }
  };

  const handleShare = () => {
    setIsShareModalOpen(true);
  };
  
  const handleShareOption = (option: 'link' | 'email') => {
    // TODO: Implement sharing functionality
    setIsShareModalOpen(false);
  };

  const handleBulkDelete = () => {
    setItems(prev => prev.filter(item => !selectedItems.includes(item.id)));
    setSelectedItems([]);
  };

  const handleClearSelection = () => {
    setSelectedItems([]);
  };

  const handleBulkMoveToWishlist = () => {
    // TODO: Implement bulk move to wishlist
    setSelectedItems([]);
  };

  const handleAddToWishlistAndCloseModal = async (wishlistId?: string) => {
    if (itemToMove) {
      // TODO: Implement add to wishlist
      setItemToMove(null);
    }
  };

  const handleBack = () => navigate('/cart');
  const handleTitleChange = (newTitle: string) => setCartTitle(newTitle);
  const handleAddItem = () => navigate('/');

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <NavbarAfter />
      <main className="flex-1 container mx-auto px-6 py-8">
        <Toolbar 
          title={cartTitle}
          onBack={handleBack}
          onTitleChange={handleTitleChange}
          onShare={handleShare}
          onAddItem={handleAddItem}
        />
        {selectedItems.length > 0 && (
          <BulkActionsBar 
            selectedCount={selectedItems.length} 
            onDelete={handleBulkDelete}
            onClearSelection={handleClearSelection}
            onSecondaryAction={handleBulkMoveToWishlist}
            secondaryActionLabel="Wishlist"
          />
        )}
        <CartTable
          items={items}
          selectedItems={selectedItems}
          onSelect={handleSelect}
          onSelectAll={handleSelectAll}
          onDelete={handleDelete}
          onMoveToWishlist={handleMoveToWishlist}
        />
      </main>
      <AddToWishlistModal
        isOpen={!!itemToMove}
        onClose={() => setItemToMove(null)}
        productName={itemToMove?.product || null}
        onAddToWishlist={handleAddToWishlistAndCloseModal}
      />
      <ShareModal 
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        onShareOption={handleShareOption}
      />
    </div>
  );
};

export default CartDetailPage; 