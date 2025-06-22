import React from 'react';
import DataTable from '../../components/ui/DataTable';
import type { RowAction, DataItem } from '../../components/ui/DataTable';
import { Bookmark, Trash2 } from 'lucide-react';

type CartItem = {
  id: string;
  category: string;
  itemNumber: string;
  product: string;
  description: string;
};

type CartTableProps = {
  items: DataItem[];
  selectedItems: string[];
  onSelect: (id: string) => void;
  onSelectAll: (checked: boolean) => void;
  onDelete: (id: string) => void;
  onMoveToWishlist: (id: string) => void;
};

const CartTable: React.FC<CartTableProps> = ({ items, selectedItems, onSelect, onSelectAll, onDelete, onMoveToWishlist }) => {
  const cartRowActions: RowAction[] = [
    {
      icon: <Bookmark className="w-5 h-5" />,
      onClick: onMoveToWishlist,
      className: "text-gray-400 hover:text-blue-600 p-1 rounded",
      ariaLabel: "Move to Wishlist",
    },
    {
      icon: <Trash2 className="w-5 h-5" />,
      onClick: onDelete,
      className: "text-gray-400 hover:text-red-600 p-1 rounded",
      ariaLabel: "Delete item",
    }
  ];

  return (
    <DataTable
      items={items}
      selectedItems={selectedItems}
      onSelect={onSelect}
      onSelectAll={onSelectAll}
      rowActions={cartRowActions}
      tableTitle="Cart Items"
    />
  );
};

export default CartTable; 