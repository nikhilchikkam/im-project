import React from 'react';
import BulkActionsBar from '../../components/common/BulkActionsBar';

type WishlistBulkActionsBarProps = {
  selectedCount: number;
  onDelete: () => void;
  onClearSelection: () => void;
};

const WishlistBulkActionsBar: React.FC<WishlistBulkActionsBarProps> = ({ selectedCount, onDelete, onClearSelection }) => {
  // Wishlist-specific secondary action (move to cart)
  const handleMoveToCart = () => {
    console.log('Move selected items to cart');
  };

  const cartIcon = (
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
    </svg>
  );

  return (
    <BulkActionsBar
      selectedCount={selectedCount}
      onDelete={onDelete}
      onClearSelection={onClearSelection}
      onSecondaryAction={handleMoveToCart}
      secondaryActionLabel="Cart"
      secondaryActionIcon={cartIcon}
    />
  );
};

export default WishlistBulkActionsBar; 