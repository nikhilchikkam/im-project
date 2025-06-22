import React from 'react';

export type DataItem = {
  id: string;
  category: string;
  itemNumber: string;
  product: string;
  description: string;
};

export type RowAction = {
  icon: React.ReactNode;
  onClick: (id: string) => void;
  className?: string;
  ariaLabel: string;
};

type DataTableProps = {
  items: DataItem[];
  selectedItems: string[];
  onSelect: (id: string) => void;
  onSelectAll: (checked: boolean) => void;
  rowActions: RowAction[];
  tableTitle?: string;
};

const DataTable: React.FC<DataTableProps> = ({ 
  items, 
  selectedItems, 
  onSelect, 
  onSelectAll, 
  rowActions,
  tableTitle 
}) => {
  const allSelected = items.length > 0 && selectedItems.length === items.length;
  
  return (
    <div className="overflow-hidden bg-white rounded-lg shadow border border-gray-200">
      <table className="min-w-full text-sm divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-4 py-3 w-12 text-left font-medium text-gray-600">
              <input 
                type="checkbox" 
                className="rounded"
                checked={allSelected} 
                onChange={e => onSelectAll(e.target.checked)} 
              />
            </th>
            <th scope="col" className="px-4 py-3 text-left font-medium text-gray-600">Category</th>
            <th scope="col" className="px-4 py-3 text-left font-medium text-gray-600">Item Number</th>
            <th scope="col" className="px-4 py-3 text-left font-medium text-gray-600">Product</th>
            <th scope="col" className="px-4 py-3 text-left font-medium text-gray-600">Description</th>
            <th scope="col" className="px-4 py-3 w-24"><span className="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {items.map(item => (
            <tr key={item.id} className={selectedItems.includes(item.id) ? 'bg-blue-50' : 'hover:bg-gray-50'}>
              <td className="px-4 py-3">
                <input 
                  type="checkbox" 
                  className="rounded"
                  checked={selectedItems.includes(item.id)} 
                  onChange={() => onSelect(item.id)} 
                />
              </td>
              <td className="px-4 py-3">
                <span className="inline-block bg-red-100 text-red-600 text-xs font-semibold rounded px-2 py-1">
                  • {item.category}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{item.itemNumber}</td>
              <td className="px-4 py-3 font-medium text-gray-800 whitespace-nowrap">{item.product}</td>
              <td className="px-4 py-3 text-gray-600">{item.description}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-3 justify-end">
                  {rowActions.map((action, index) => (
                    <button
                      key={index}
                      className={action.className || "text-gray-400 hover:text-gray-600 p-1 rounded"}
                      onClick={() => action.onClick(item.id)}
                      aria-label={action.ariaLabel}
                    >
                      {action.icon}
                    </button>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable; 