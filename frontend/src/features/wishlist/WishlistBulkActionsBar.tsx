import React from 'react';

type WishlistBulkActionsBarProps = {
  selectedCount: number;
  onDelete: () => void;
  onClearSelection: () => void;
};

const WishlistBulkActionsBar: React.FC<WishlistBulkActionsBarProps> = ({ selectedCount, onDelete, onClearSelection }) => (
  <div className="flex items-center justify-between bg-gray-50 border rounded-lg px-6 py-3 mb-4">
    <div className="flex items-center gap-3">
      <button onClick={onClearSelection} className="text-gray-500 hover:text-gray-700 p-1">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
      <span className="font-medium">{selectedCount} items selected</span>
    </div>
    <div className="flex items-center gap-2">
      <span className="text-gray-500 text-sm">Remove items:</span>
      <button onClick={onDelete} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-1.5 rounded-lg text-sm transition flex items-center gap-1">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
        Delete
      </button>
    </div>
  </div>
);

export default WishlistBulkActionsBar; 