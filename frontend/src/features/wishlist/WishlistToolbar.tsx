import React, { useState } from 'react';

type WishlistToolbarProps = {
  title: string;
  onBack: () => void;
  onTitleChange: (newTitle: string) => void;
  onShare: (action: string) => void;
  onAddItem: () => void;
};

const WishlistToolbar: React.FC<WishlistToolbarProps> = ({ title, onBack, onTitleChange, onShare, onAddItem }) => {
  const [editing, setEditing] = useState(false);
  const [input, setInput] = useState(title);
  const [shareOpen, setShareOpen] = useState(false);

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
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
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
          <span className="text-2xl font-semibold flex items-center gap-2">
            {title}
            <button onClick={handleEdit} className="ml-1 p-1 rounded hover:bg-gray-100">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 112.828 2.828L11.828 15.828a4 4 0 01-1.414.828l-4 1a1 1 0 01-1.213-1.213l1-4a4 4 0 01.828-1.414z" /></svg>
            </button>
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <div className="relative">
          <button onClick={() => setShareOpen((v) => !v)} className="p-2 rounded hover:bg-gray-100">
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 12v2a4 4 0 004 4h8a4 4 0 004-4v-2M16 6l-4-4-4 4m4-4v16" /></svg>
          </button>
          {shareOpen && (
            <div className="absolute right-0 mt-2 w-36 bg-white border rounded shadow z-10">
              <button onClick={() => { setShareOpen(false); onShare('download'); }} className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3" /></svg>
                Download
              </button>
              <button onClick={() => { setShareOpen(false); onShare('share'); }} className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 8a3 3 0 11-6 0 3 3 0 016 0zM2 12a9 9 0 0118 0c0 7-9 11-9 11S2 19 2 12z" /></svg>
                Share
              </button>
            </div>
          )}
        </div>
        <button onClick={onAddItem} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg text-base transition">
          + Add item
        </button>
      </div>
    </div>
  );
};

export default WishlistToolbar; 