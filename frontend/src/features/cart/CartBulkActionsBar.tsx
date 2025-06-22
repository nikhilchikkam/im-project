import React from 'react';
import BulkActionsBar from '../../components/common/BulkActionsBar';

type CartBulkActionsBarProps = {
  selectedCount: number;
  onDelete: () => void;
  onClearSelection: () => void;
};

const CartBulkActionsBar: React.FC<CartBulkActionsBarProps> = ({ selectedCount, onDelete, onClearSelection }) => {
  // Cart-specific secondary action (move to wishlist)
  const handleMoveToWishlist = () => {
    console.log('Move selected items to wishlist');
  };

  const wishlistIcon = (
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  );

  return (
    <BulkActionsBar
      selectedCount={selectedCount}
      onDelete={onDelete}
      onClearSelection={onClearSelection}
      onSecondaryAction={handleMoveToWishlist}
      secondaryActionLabel="Wishlist"
      secondaryActionIcon={wishlistIcon}
    />
  );
};

export default CartBulkActionsBar; 