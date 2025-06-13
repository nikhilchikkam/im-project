import React from 'react';

type WishlistItem = {
  id: string;
  category: string;
  itemNumber: string;
  product: string;
  description: string;
};

type WishlistTableProps = {
  items: WishlistItem[];
  selectedItems: string[];
  onSelect: (id: string) => void;
  onSelectAll: (checked: boolean) => void;
  onDelete: (id: string) => void;
};

const WishlistTable: React.FC<WishlistTableProps> = ({ items, selectedItems, onSelect, onSelectAll, onDelete }) => {
  const allSelected = items.length > 0 && selectedItems.length === items.length;
  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2"><input type="checkbox" checked={allSelected} onChange={e => onSelectAll(e.target.checked)} /></th>
            <th className="px-4 py-2 text-left">Category</th>
            <th className="px-4 py-2 text-left">Item Number</th>
            <th className="px-4 py-2 text-left">Product</th>
            <th className="px-4 py-2 text-left">Description</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id} className={selectedItems.includes(item.id) ? 'bg-blue-50' : ''}>
              <td className="px-4 py-2"><input type="checkbox" checked={selectedItems.includes(item.id)} onChange={() => onSelect(item.id)} /></td>
              <td className="px-4 py-2"><span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-semibold">• {item.category}</span></td>
              <td className="px-4 py-2">{item.itemNumber}</td>
              <td className="px-4 py-2">{item.product}</td>
              <td className="px-4 py-2">{item.description}</td>
              <td className="px-4 py-2 flex gap-2 justify-end">
                <button className="text-blue-600 hover:bg-blue-100 p-1 rounded" onClick={() => onDelete(item.id)}>
                  <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
                <button className="text-gray-500 hover:bg-gray-100 p-1 rounded">
                  <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/><circle cx="5" cy="12" r="2"/></svg>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WishlistTable; 