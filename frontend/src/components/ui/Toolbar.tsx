import React, { useState, useEffect } from 'react';
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

  // Update input when title changes
  useEffect(() => {
    setInput(title);
  }, [title]);

  const handleEdit = () => setEditing(true);
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value);
  const handleInputBlur = () => {
    setEditing(false);
    if (input !== title) onTitleChange(input);
  };
  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleInputBlur();
    } else if (e.key === 'Escape') {
      setInput(title);
      setEditing(false);
    }
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
          <div className="flex items-center gap-2">
            <input
              className="text-2xl font-semibold border-b-2 border-blue-500 focus:outline-none bg-transparent w-64 px-2 py-1 rounded-t transition-colors duration-200"
              value={input}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              onKeyDown={handleInputKeyDown}
              autoFocus
              placeholder="Enter group name"
            />
            <div className="flex items-center gap-1">
              <button 
                onClick={handleInputBlur}
                className="p-1 text-green-600 hover:text-green-700 hover:bg-green-50 rounded transition-colors duration-200"
                title="Save changes"
              >
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <button 
                onClick={() => {
                  setInput(title);
                  setEditing(false);
                }}
                className="p-1 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors duration-200"
                title="Cancel editing"
              >
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <h1 className="text-2xl font-semibold flex items-center gap-2 group">
            <span className="transition-colors duration-200">{title}</span>
            <button 
              onClick={handleEdit} 
              className="ml-2 p-2 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-all duration-200 opacity-70 hover:opacity-100 group-hover:opacity-100"
              title="Edit group name (Click to edit)"
            >
              <svg 
                width="18" 
                height="18" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                className="group-hover:scale-110 transition-transform duration-200"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
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