import React, { useState } from 'react';
import { Share2 } from 'lucide-react';

type ToolbarProps = {
  title: string;
  onBack: () => void;
  onTitleChange: (newTitle: string) => void;
  onShare: () => void;
  onAddItem: () => void;
  showShare?: boolean;
  showAddItem?: boolean;
  addItemLabel?: string;
};

const Toolbar: React.FC<ToolbarProps> = ({ 
  title, 
  onBack, 
  onTitleChange, 
  onShare, 
  onAddItem, 
  showShare = true,
  showAddItem = true,
  addItemLabel = "+ Add item"
}) => {
  const [editing, setEditing] = useState(false);
  const [input, setInput] = useState(title);

  const handleEdit = () => setEditing(true);
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value);
  const handleInputBlur = () => {
    setEditing(false);
    if (input !== title) onTitleChange(input);
  };
  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleInputBlur();
  };

  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 rounded hover:bg-gray-100">
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        {editing ? (
          <input
            className="text-2xl font-semibold border-b border-gray-300 focus:outline-none focus:border-blue-500 bg-transparent w-64"
            value={input}
            onChange={handleInputChange}
            onBlur={handleInputBlur}
            onKeyDown={handleInputKeyDown}
            autoFocus
          />
        ) : (
          <h1 className="text-2xl font-semibold flex items-center gap-2">
            {title}
            <button onClick={handleEdit} className="ml-1 p-1 rounded hover:bg-gray-100">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 112.828 2.828L11.828 15.828a4 4 0 01-1.414.828l-4 1a1 1 0 01-1.213-1.213l1-4a4 4 0 01.828-1.414z" />
              </svg>
            </button>
          </h1>
        )}
      </div>
      <div className="flex items-center gap-3">
        {showShare && (
          <button
            onClick={onShare}
            className="p-2 rounded hover:bg-gray-100"
            aria-label="Share"
          >
            <Share2 className="w-5 h-5 text-gray-600" />
          </button>
        )}
        {showAddItem && (
          <button onClick={onAddItem} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg text-base transition">
            {addItemLabel}
          </button>
        )}
      </div>
    </div>
  );
};

export default Toolbar; 