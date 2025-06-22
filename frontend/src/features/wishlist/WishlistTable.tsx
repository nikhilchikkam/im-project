import React from 'react';
import DataTable from '../../components/ui/DataTable';
import type { RowAction, DataItem } from '../../components/ui/DataTable';
import { ListPlus, MoreHorizontal } from 'lucide-react';

type WishlistItem = {
  id: string;
  category: string;
  itemNumber: string;
  product: string;
  description: string;
};

type WishlistTableProps = {
  items: DataItem[];
  selectedItems: string[];
  onSelect: (id: string) => void;
  onSelectAll: (checked: boolean) => void;
  onAddToList: (id: string) => void;
  onMoreOptions: (id:string) => void;
};

const WishlistTable: React.FC<WishlistTableProps> = ({ items, selectedItems, onSelect, onSelectAll, onAddToList, onMoreOptions }) => {
  // Wishlist-specific secondary action (move to cart)
  const handleMoveToCart = (id: string) => {
    console.log('Move to cart:', id);
  };

  const cartIcon = (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
    </svg>
  );

  const wishlistRowActions: RowAction[] = [
    {
      icon: <ListPlus className="w-5 h-5" />,
      onClick: onAddToList,
      className: "text-gray-400 hover:text-blue-600 p-1 rounded",
      ariaLabel: "Add to another list",
    },
    {
      icon: <MoreHorizontal className="w-5 h-5" />,
      onClick: onMoreOptions,
      className: "text-gray-400 hover:text-gray-600 p-1 rounded",
      ariaLabel: "More options",
    }
  ];

  return (
    <DataTable
      items={items}
      selectedItems={selectedItems}
      onSelect={onSelect}
      onSelectAll={onSelectAll}
      rowActions={wishlistRowActions}
      tableTitle="Wishlist Items"
    />
  );
};

export default WishlistTable; 